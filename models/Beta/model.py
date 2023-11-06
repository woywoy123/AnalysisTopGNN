import torch
from torch.nn.functional import softmax
from torch_geometric.nn import MessagePassing
from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid
from torch_geometric.utils import to_dense_adj, dense_to_sparse, degree


# custom pyc extension functions
import pyc
import pyc.Transform as transform
import pyc.Graph.Cartesian as graph
import pyc.Graph.Base as graph_base
import pyc.Physics.Cartesian as physics
import pyc.Operators as operators
from time import sleep

class MarkovGraphNet(MessagePassing):

    def __init__(self):
        super().__init__(aggr = None, flow = "source_to_target")
        end = 32
        self.O_top_edge = None
        self.L_top_edge = "CEL"

        self._edge = Seq(
            Linear(1, end),
            Linear(end, 2),
        )

    def message(self, edge_index, pmc, trk_j, trk_i):
        src, dst = edge_index[0].view(-1, 1), edge_index[1].view(-1, 1)
        pmc_ij = graph_base.unique_aggregation(torch.cat([src, trk_i], -1), pmc)
        mass_ij = physics.M(pmc_ij).to(dtype = torch.float)/1000
        mlp_ = self._edge(torch.cat([mass_ij], -1))
        return mlp_, src, dst


    def aggregate(self, message, index, pmc, trk):
        mlp_ij, src, dst = message
        edge_index = torch.cat([src.view(1, -1), dst.view(1, -1)], 0)

        # Create the probability topologies
        # p0: probability of not choosing this node. p1: probability of choosing node.
        adj_p1 = softmax(to_dense_adj(edge_index, edge_attr = mlp_ij[:, 1])[0], -1)
        adj_p0 = (1-adj_p1)

        # Create the probability field that the given edge is being connected by the MLP
        # p0: mlp predicts a non connection. p1: mlp predicts this to be an edge
        gamma_p1 = to_dense_adj(edge_index, edge_attr = softmax(mlp_ij, -1)[:, 1])[0]
        gamma_p0 = 1 - gamma_p1

        # Create the probability field that a given edge is predicted to be connected
        G_ij1 = adj_p1 * gamma_p1

        # Create the probability field that a given edge is selected p(ij | gamma {0, 1})
        G_ij = adj_p1 * gamma_p1 + adj_p1 * gamma_p0 + adj_p0 * gamma_p1 + adj_p0 * gamma_p0

        # Protect against null probabilities
        prior_matrix = to_dense_adj(edge_index, edge_attr = self.prior.view(-1)[dst.view(-1)])[0]
        G_ij1 = prior_matrix*G_ij1

        remain = (G_ij.sum(-1) > 0)*(G_ij1.sum(-1) > 0)
        if not remain.sum(-1): return self.O_top_edge

        # Randomly sample the probability space and choose a node transition
        trk = torch.cat([trk, torch.ones_like(trk)*-1], -1)
        next_node = torch.multinomial(G_ij1[remain]/G_ij[remain], 1)

        # Record the transition probability of selected node and update the tracks
        p_ij = (G_ij1[remain]/G_ij[remain]).gather(dim = -1, index = next_node)
        trk[remain, -1] = next_node.view(-1)
        remove = torch.cat([trk[remain, 0].view(1, -1), next_node.view(-1).view(1, -1)], 0)
        num_nodes = pmc.size(0)
        adj  = to_dense_adj(edge_index, max_num_nodes = num_nodes)[0]
        adj -= to_dense_adj(remove    , max_num_nodes = num_nodes)[0]
        edge_index, _ = dense_to_sparse(adj)

        # Update the prior with the new posterior
        self.prior[remain] += self.prior[remain] * p_ij

        pmc_ = graph_base.unique_aggregation(trk[src.view(-1)], pmc)
        mass_ = physics.M(pmc_).to(dtype = torch.float)/1000

        # update the output mlp with the new data
        idx = self.idx[src.view(-1), dst.view(-1)]
        self.O_top_edge[idx] = self._edge(torch.cat([mass_], -1))

        return self.propagate(edge_index, pmc = pmc, trk = trk)

    def forward(self, edge_index, batch, N_pT, N_eta, N_phi, N_energy, E_T_top_edge):
        src, dst = edge_index
        pmc = transform.PxPyPzE(torch.cat([N_pT, N_eta, N_phi, N_energy], -1))
        track = (torch.ones_like(batch).cumsum(-1)-1).view(-1, 1)
        self.idx = to_dense_adj(edge_index, edge_attr = torch.ones_like(src).cumsum(-1)-1)[0]

        self.prior = (1/degree(src)).view(-1, 1)
        self.O_top_edge = self.message(edge_index, pmc, track[src], track[dst])[0]
        output = self.propagate(edge_index, pmc = pmc, trk = track)
