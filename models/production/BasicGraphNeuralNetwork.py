import torch
import torch.nn.functional as F
from torch_geometric.nn import MessagePassing, knn_graph
from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid, Tanh


import pyc
import pyc.Transform as transform
import pyc.Graph.Cartesian as graph
import pyc.Physics.Cartesian as physics

class ParticleEdgeConv(MessagePassing):
    def __init__(self):
        super().__init__(aggr="max")
        self._mlp_edge = Seq(
            Linear(16, 256), Tanh(),
            Linear(256, 256), ReLU(),
            Linear(256, 256), Tanh(),
            Linear(256, 16),
        )

    def forward(self, edge_index, N_eta, N_pT, N_energy, N_phi, N_is_b, N_is_lep):
        pmu = torch.cat([N_pT, N_eta, N_phi, N_energy], -1)
        pmc = transform.PxPyPzE(pmu)
        particle = torch.cat([N_is_b, N_is_lep], -1).to(dtype = N_energy.dtype)
        return self.propagate(edge_index, pmc = pmc, particle = particle)

    def message(self, pmc_i, pmc_j, particle_i, particle_j):
        dr = physics.DeltaR(pmc_i, pmc_j)
        m_ij, m_i, m_j = physics.M(pmc_i + pmc_j), physics.M(pmc_i), physics.M(pmc_j)
        i_attrs = torch.cat([pmc_i, m_i, particle_i], -1)
        ij_diff = torch.cat([pmc_i - pmc_j, m_i - m_j, particle_i - particle_j], -1)
        ij_feats = torch.cat([m_ij, dr], -1)
        inpt = torch.cat([i_attrs, ij_diff, ij_feats], -1).to(dtype = torch.float)
        return self._mlp_edge(inpt)


class BasicGraphNeuralNetwork(MessagePassing):
    def __init__(self):
        super().__init__(aggr=None)
        self.O_top_edge = None
        self.L_top_edge = "CEL"
        self._top_edge = ParticleEdgeConv()
        self._t_edge = Seq(Linear(16 * 2, 16 * 2), ReLU(), Linear(16 * 2, 2))

        self.O_res_edge = None
        self.L_res_edge = "CEL"
        self._res_edge = ParticleEdgeConv()
        self._r_edge = Seq(Linear(16 * 2, 16 * 2), ReLU(), Linear(16 * 2, 2))

        self.O_signal = None
        self.L_signal = "CEL"

        self._gr_mlp = Seq(
            Linear(5, 64), ReLU(),
            Linear(64, 64), Sigmoid(),
            Linear(64, 2), ReLU(),
            Linear(2, 2),
        )


    def forward(self, edge_index, batch, G_met, G_phi, G_n_jets, N_eta, N_pT, N_energy, N_phi, N_is_b, N_is_lep):

        top = self._top_edge(edge_index, N_eta, N_pT, N_energy, N_phi, N_is_b, N_is_lep)
        res = self._res_edge(edge_index, N_eta, N_pT, N_energy, N_phi, N_is_b, N_is_lep)
        self.O_res_edge, self.O_top_edge = self.propagate(edge_index, top=top, res=res)
        res_, top_ = self.O_res_edge.max(-1)[1], self.O_top_edge.max(-1)[1]

        # // Aggregate result into tops.
        pmc_ = transform.PxPyPzE(N_pT, N_eta, N_phi, N_energy)
        out = graph.edge(edge_index, top_, pmc_, True)
        try: aggr_c = out[1]["unique_sum"]
        except KeyError: aggr_c = out[0]["unique_sum"]*0
        top = physics.M(aggr_c)[0].view(-1, 1)

        out = graph.edge(edge_index, res_, pmc_, True)
        try: aggr_c = out[1]["unique_sum"]
        except KeyError: aggr_c = out[0]["unique_sum"]*0
        res = physics.M(aggr_c)[0].view(-1, 1)

        sig = torch.cat([G_met, G_phi, G_n_jets, res, top], -1)
        self.O_signal = self._gr_mlp(sig.to(dtype = torch.float))

    def message(self, edge_index, top_i, top_j, res_i, res_j):
        tmp_r = self._r_edge(torch.cat([res_i, res_i - res_j], -1))
        tmp_t = self._t_edge(torch.cat([top_i, top_i - top_j], -1))
        return F.softmax(tmp_r, -1), F.softmax(tmp_t, -1)

    def aggregate(self, message):
        return message
