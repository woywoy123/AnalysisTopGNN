import torch
import torch.nn.functional as F
from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid
from torch_geometric.nn import MessagePassing

# torch extension modules
import pyc.Transform as transform
import pyc.Physics as physics

from torch_geometric.utils import to_dense_adj, add_remaining_self_loops


torch.set_printoptions(4, profile="full", linewidth=100000)


class BasicBaseLineRecursion(MessagePassing):
    def __init__(self):
        super().__init__(aggr=None, flow="target_to_source")
        self.O_top_edge = None
        self.L_top_edge = "CEL"

        self.O_res_edge = None
        self.L_res_edge = "CEL"

        end = 64
        self._isEdge = Seq(
            Linear(end * 4, end), ReLU(),
            Linear(end, 256), Sigmoid(),
            Linear(256, 128), ReLU(),
            Linear(128, 2),
        )

        self._isMass = Seq(Linear(1, end), Linear(end, end))

        self._isResEdge = Seq(
            Linear(end * 4, end), ReLU(),
            Linear(end, 256), Sigmoid(),
            Linear(256, 128), ReLU(),
            Linear(128, 2),
        )

        self._it = 0

    def forward(self, i, edge_index, N_pT, N_eta, N_phi, N_energy):
        if self._it == 0:
            self.device = N_pT.device
            self.edge_mlp = torch.zeros((edge_index.shape[1], 2), device=self.device)
            self.res_mlp = torch.zeros((edge_index.shape[1], 2), device=self.device)
            self.node_count = torch.ones((N_pT.shape[0], 1), device=self.device)
            self.index_map = to_dense_adj(edge_index)[0]
            self.index_map[self.index_map != 0] = torch.arange(
                self.index_map.sum(), device=self.device
            )
            self.index_map = self.index_map.to(dtype=torch.long)

        pmu = torch.cat([N_pT, N_eta, N_phi, N_energy], -1)
        pmc = transform.PxPyPzE(pmu)
        n_mass = physics.M(pmc)

        edge_index_n, pmu = self.propagate(edge_index, pmc = pmc, pmu = pmu)

        s1 = torch.sum(self.index_map[edge_index_n])
        s2 = torch.sum(self.index_map[edge_index])

        if s1 != s2:
            self._it += 1
            pt, eta, phi, e = [pmu[:, i:i+1] for i in range(4)]
            return self.forward(i, edge_index_n, pt, eta, phi, e)

        self._it = 0
        self.O_top_edge = self.edge_mlp
        self.O_res_edge = self.res_mlp

    def message(self, edge_index, pmc_i, pmc_j):
        e_dr = physics.Cartesian.DeltaR(pmc_i, pmc_j)
        m_ij = physics.M(pmc_i + pmc_j)/1000
        m_i, m_j = physics.M(pmc_i)/1000, physics.M(pmc_j)/1000

        mlp_ij = self._isMass(m_ij.to(dtype = torch.float))
        mlp_i = self._isMass(m_i.to(dtype = torch.float))
        mlp_j = self._isMass(m_j.to(dtype = torch.float))

        ef = torch.cat([
            mlp_ij, torch.abs(mlp_i - mlp_j),
            torch.abs(mlp_ij - mlp_i - mlp_j),
            mlp_ij + mlp_i + mlp_j], -1)

        mlp_t = self._isEdge(ef)
        mlp_r = self._isResEdge(ef)
        return edge_index[1], mlp_t, mlp_r

    def aggregate(self, message, index, pmc, pmu):
        edge_index, mlp_t, res = message
        edge_t = mlp_t.max(dim=1)[1]

        max_c = (edge_t == 1).nonzero().view(-1)
        idx = self.index_map[index[max_c], edge_index[max_c]]
        idx_all = self.index_map[index, edge_index]

        max_c = max_c[index[max_c] != edge_index[max_c]]

        # Get the index of the current node and the incoming node
        idx_i, idx_j = index[max_c], edge_index[max_c],

        # Get the four vectors of non zero edges for incoming edge
        pmc_idx_j = pmc[idx_j]

        node_c_j = self.node_count[idx_j].view(-1, 1)  # Node j count

        pmc_i = pmc.clone()  # Collect the node's own four vector
        pmc_i.index_add_(0, idx_i, pmc_idx_j * node_c_j)

        self.node_count[index[max_c]] = 0
        self.node_count[edge_index[max_c]] = 0

        self.edge_mlp[idx_all] += mlp_t
        self.res_mlp[idx_all] += res

        not_t = edge_t == 0
        edge_index = torch.cat([index[not_t].view(1, -1), edge_index[not_t].view(1, -1)], 0)
        edge_index = add_remaining_self_loops(edge_index, num_nodes=pmc.shape[0])[0]
        return edge_index, transform.PtEtaPhiE(pmc_i)
