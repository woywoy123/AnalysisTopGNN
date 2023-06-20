import torch
from torch_geometric.nn import MessagePassing
from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid, Tanh
import torch.nn.functional as F
import PyC.Transform.Tensors as Tt
import PyC.Physics.Tensors.Polar as PtP
import PyC.Physics.Tensors.Cartesian as PtC
from torch_geometric.utils import (
    to_dense_adj,
    add_remaining_self_loops,
    dense_to_sparse,
)

torch.set_printoptions(4, profile="full", linewidth=100000)


class CheatModel(MessagePassing):
    def __init__(self):
        super().__init__(aggr=None, flow="target_to_source")
        self.O_top_edge = None
        self.L_top_edge = "CEL"

        end = 16
        self._isEdge = Seq(Linear(8, end), ReLU(), Linear(end, 2))
        self._isMass = Seq(Linear(1, end), Linear(end, 2))

    def forward(self, i, edge_index, N_pT, N_eta, N_phi, N_energy, E_T_top_edge):
        Pmu = torch.cat([N_pT, N_eta, N_phi, N_energy], dim=1)
        Pmc = torch.cat([Tt.PxPyPz(N_pT, N_eta, N_phi), N_energy], dim=-1)

        self.O_top_edge = self.propagate(
            edge_index, Pmc=Pmc, Pmu=Pmu, E_T_edge=E_T_top_edge
        )

    def message(self, edge_index, Pmc_i, Pmc_j, Pmu_i, Pmu_j, E_T_edge):
        e_dr = PtP.DeltaR(
            Pmu_i[:, 1].view(-1, 1),
            Pmu_j[:, 1].view(-1, 1),
            Pmu_i[:, 2].view(-1, 1),
            Pmu_j[:, 2].view(-1, 1),
        )
        e_mass, i_mass, j_mass = (
            PtC.Mass(Pmc_i + Pmc_j),
            PtC.Mass(Pmc_i),
            PtC.Mass(Pmc_j),
        )

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
