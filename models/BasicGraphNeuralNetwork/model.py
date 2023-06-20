import torch
from torch_geometric.nn import MessagePassing, knn_graph
from torch_geometric.utils import scatter
from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid, Tanh
import torch.nn.functional as F

try:
    import PyC.Transform.CUDA as Tr
except:
    import PyC.Transform.Tensors as Tr

try:
    import PyC.Physics.CUDA.Polar as PP
except:
    import PyC.Physics.Tensors.Polar as PP

try:
    import PyC.Physics.CUDA.Cartesian as PC
except:
    import PyC.Physics.Tensors.Cartesian as PC

torch.set_printoptions(4, profile="full", linewidth=100000)


class ParticleEdgeConv(MessagePassing):
    def __init__(self):
        super().__init__(aggr="max")
        self._mlp_edge = Seq(
            Linear(16, 256),
            Tanh(),
            Linear(256, 256),
            ReLU(),
            Linear(256, 256),
            Tanh(),
            Linear(256, 16),
        )

    def forward(self, edge_index, N_eta, N_pT, N_energy, N_phi, N_is_b, N_is_lep):
        Pmc = torch.cat([Tr.PxPyPz(N_pT, N_eta, N_phi), N_energy], -1)
        return self.propagate(
            edge_index,
            Pmc=Pmc,
            pt=N_pT,
            eta=N_eta,
            phi=N_phi,
            islep=N_is_lep,
            isb=N_is_b,
        )

    def message(
        self, Pmc_i, Pmc_j, eta_i, eta_j, phi_i, phi_j, islep_i, islep_j, isb_i, isb_j
    ):
        dR = PP.DeltaR(eta_i, eta_j, phi_i, phi_j)
        m_ij, m_i, m_j = PC.Mass(Pmc_i + Pmc_j), PC.Mass(Pmc_i), PC.Mass(Pmc_j)
        i_attrs = torch.cat([Pmc_i, m_i, islep_i, isb_i], -1)
        ij_diff = torch.cat(
            [Pmc_i - Pmc_j, m_i - m_j, islep_i - islep_j, isb_i - isb_j], -1
        )
        ij_feats = torch.cat([m_ij, dR], -1)
        return self._mlp_edge(torch.cat([i_attrs, ij_diff, ij_feats], -1))


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
            Linear(11, 64),
            ReLU(),
            Linear(64, 64),
            Sigmoid(),
            Linear(64, 2),
            ReLU(),
            Linear(2, 2),
        )

        self.O_ntops = None
        self.L_ntops = "CEL"

        self._nt_mlp = Seq(
            Linear(6, 64),
            ReLU(),
            Linear(64, 64),
            Sigmoid(),
            Linear(64, 2),
            ReLU(),
            Linear(2, 5),
        )

    def forward(
        self,
        edge_index,
        batch,
        G_met,
        G_phi,
        G_n_jets,
        N_eta,
        N_pT,
        N_energy,
        N_phi,
        N_is_b,
        N_is_lep,
    ):
        top = self._top_edge(edge_index, N_eta, N_pT, N_energy, N_phi, N_is_b, N_is_lep)
        res = self._res_edge(edge_index, N_eta, N_pT, N_energy, N_phi, N_is_b, N_is_lep)

        top_edge_ = knn_graph(top, 4, batch=batch, loop=True, flow=self.flow)
        top = self._top_edge(top_edge_, N_eta, N_pT, N_energy, N_phi, N_is_b, N_is_lep)

        res_edge_ = knn_graph(top, 4, batch=batch, loop=True, flow=self.flow)
        res = self._res_edge(res_edge_, N_eta, N_pT, N_energy, N_phi, N_is_b, N_is_lep)

        self.O_res_edge, self.O_top_edge = self.propagate(edge_index, top=top, res=res)
        res_, top_ = self.O_res_edge.max(-1)[1], self.O_top_edge.max(-1)[1]

        # // Aggregate result into tops.
        Pmc_ = torch.cat([Tr.PxPyPz(N_pT, N_eta, N_phi), N_energy], -1)
        aggr_c = torch.zeros_like(Pmc_)
        aggr_c[edge_index[0]] += Pmc_[edge_index[1]] * (top_.view(-1, 1))
        aggr_c = torch.cat([PC.Mass(aggr_c), N_is_b, N_is_lep], -1)

        _ntops = torch.cat([G_met, G_phi, G_n_jets], -1)
        gr = torch.zeros_like(_ntops)
        gr[batch] += aggr_c
        self.O_ntops = self._nt_mlp(torch.cat([_ntops, gr], -1))

        # // Aggregate result into resonance edges, provided there is a top edge.
        Pmc_ = torch.cat([Tr.PxPyPz(N_pT, N_eta, N_phi), N_energy], -1)
        aggr_c = torch.zeros_like(Pmc_)
        aggr_c[edge_index[0]] += Pmc_[edge_index[1]] * (
            res_.view(-1, 1) * top_.view(-1, 1)
        )
        aggr_c = torch.cat([PC.Mass(aggr_c), N_is_b, N_is_lep], -1)

        sig = torch.cat([G_met, G_phi, G_n_jets], -1)
        gr = torch.zeros_like(sig)
        gr[batch] += aggr_c
        self.O_signal = self._gr_mlp(torch.cat([sig, gr, self.O_ntops], -1))

    def message(self, edge_index, top_i, top_j, res_i, res_j):
        tmp_r = self._r_edge(torch.cat([res_i, res_i - res_j], -1))
        tmp_t = self._t_edge(torch.cat([top_i, top_i - top_j], -1))
        return F.softmax(tmp_r, -1), F.softmax(tmp_t, -1)

    def aggregate(self, message):
        return message
