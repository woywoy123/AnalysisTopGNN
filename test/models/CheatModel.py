from torch_geometric.nn import MessagePassing
from torch.nn import Sequential as Seq, Linear, ReLU
import torch
import pyc

class CheatModel(MessagePassing):
    def __init__(self, test):
        super().__init__(aggr=None, flow="target_to_source")
        self.O_top_edge = None
        self.L_top_edge = "CEL"
        self.test = test

        self.O_signal = None
        self.L_signal = "CEL"

        end = 16
        self._isEdge = Seq(Linear(8, end), ReLU(), Linear(end, 2))
        self._isMass = Seq(Linear(1, end), Linear(end, 2))

        self._isSig = Seq(Linear(1, end), Linear(end, 2))

    def forward(self, i, edge_index, N_pT, N_eta, N_phi, N_energy, E_T_top_edge, G_T_signal):
        Pmu = torch.cat([N_pT, N_eta, N_phi, N_energy], dim=1)
        Pmc = pyc.Transform.PtEtaPhiE(Pmu)
        self.O_top_edge = self.propagate(
            edge_index, Pmc=Pmc, Pmu=Pmu, E_T_edge=E_T_top_edge
        )

        self.O_signal = self._isSig(G_T_signal.to(dtype = torch.float))



    def message(self, edge_index, Pmc_i, Pmc_j, Pmu_i, Pmu_j, E_T_edge):
        e_dr = pyc.Physics.Polar.DeltaR(Pmu_i, Pmu_j).to(dtype = torch.float)
        e_mass = pyc.Physics.Cartesian.M(Pmc_i + Pmc_j).to(dtype = torch.float)

        i_mass = pyc.Physics.Cartesian.M(Pmc_i).to(dtype = torch.float)
        j_mass = pyc.Physics.Cartesian.M(Pmc_j).to(dtype = torch.float)

        e_mass_mlp = self._isMass(e_mass / 1000)
        ni_mass = self._isMass(i_mass / 1000)
        nj_mass = self._isMass(j_mass / 1000)

        mlp = self._isEdge(
            torch.cat([E_T_edge, ni_mass, nj_mass, e_mass_mlp, e_dr], dim=1)
        )
        return edge_index[1], mlp, Pmc_j

    def aggregate(self, message, index, Pmc, Pmu):
        edge_index, mlp_mass, Pmc_j = message
        return mlp_mass
