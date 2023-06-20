import torch
from torch_geometric.nn import MessagePassing
from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid, Tanh

try:
    import PyC.Transform.CUDA as Tr
except:
    import PyC.Transform.Tensor as Tr

try:
    import PyC.Physics.CUDA.Cartesian as PhC
except:
    import PyC.Physics.Tensors as PhC
try:
    import PyC.Physics.CUDA.Polar as PhP
except:
    import PyC.Physics.Polar as PhP

torch.set_printoptions(4, profile="full", linewidth=100000)


class RecursiveBase(MessagePassing):
    def __init__(self):
        super().__init__(aggr=None, flow="target_to_source")

        self.edge = None
        self.edge = "CEL"

        end = 16
        self._isEdge = Seq(Linear(1, end), Linear(end, end))
        self._recEdge = Seq(Linear(end + 2, end), Linear(end, 2))
        self._it = 0

    def message(self, edge_index, Pmc_i, Pmc_j, Pmu_i, Pmu_j):
        eta_i, phi_i = Pmu_i[:, 1].view(-1, 1), Pmu_i[:, 2].view(-1, 1)
        eta_j, phi_j = Pmu_j[:, 1].view(-1, 1), Pmu_j[:, 2].view(-1, 1)

        mass_ij, dR = PhC.Mass(Pmc_i + Pmc_j), PhP.DeltaR(eta_i, eta_j, phi_i, phi_j)
        mass_i, mass_j = PhC.Mass(Pmc_i), PhC.Mass(Pmc_j)
        return self._isEdge(torch.cat([mass_ij], -1)), Pmc_j

    def aggregate(self, message, index, Pmc):
        mlp, pmc_j = message
        msk = self._msk.clone()

        # // Recursively update the message
        self.messages = self._recEdge(torch.cat([self.messages, mlp], -1))
        idx = self.messages.max(-1)[1]

        # // aggregate the incoming edges that the MLP predicted to be correct
        self.nodes[index[idx == 1]] += pmc_j[idx == 1]
        mlp = self._isEdge(PhC.Mass(self.nodes[index]))
        self.messages = self._recEdge(torch.cat([self.messages, mlp], -1))
        idx[self.messages.max(-1)[1] == idx] = 1

        # // update the already used edges and remove them from the allowed edges
        # idx[(self._edge_index[0] == self._edge_index[1])[msk == 1]] = 1
        # self._msk[msk == 1] -= idx
        self._msk[idx == 1] = 0

        # // Make sure the self node has the appropriate 4-vector if self loops were not selected
        zeros = self.nodes.sum(-1) == 0
        self.nodes[zeros] += Pmc[zeros]
        return idx

    def forward(self, i, edge_index, N_pT, N_eta, N_phi, N_energy):
        Pmu = torch.cat([N_pT, N_eta, N_phi, N_energy], -1)
        Pmc = torch.cat([Tr.PxPyPz(N_pT, N_eta, N_phi), N_energy], -1)
        if self._it == 0:
            self.device = N_pT.device
            self._edge_index = edge_index.clone()
            self._msk = torch.ones_like(self._edge_index[0])

            self.messages = (
                torch.zeros_like(edge_index).to(dtype=N_pT.dtype).view(-1, 2)
            )
            self._it = 1
            self.forward(i, edge_index, N_pT, N_eta, N_phi, N_energy)
            self._it = 0
            self.edge = self.messages
            return self
        self._it += 1
        self.nodes = torch.zeros_like(Pmu)
        idx = self._msk.clone()
        sel = self.propagate(edge_index, Pmc=Pmc, Pmu=Pmu)
        edge_index_n = edge_index  # torch.cat([edge_index[0][sel == 0].view(1, -1), edge_index[1][sel == 0].view(1, -1)], 0)
        if (sel - idx).sum(-1) == 0:
            return
        if self._msk.sum(-1) == 0:
            return
        if sel.sum(-1) <= 0:
            return
        # if edge_index_n.size()[1] == edge_index.size()[1]: return
        # if edge_index_n.size()[1] == 0: return
        if self._msk.sum(-1) <= 0:
            return
        # self.nodes = self.nodes
        # Pmu = Tr.PtEtaPhi(self.nodes[:, 0].view(-1, 1), self.nodes[:, 1].view(-1, 1), self.nodes[:, 2].view(-1, 1))
        # N_pT, N_eta, N_phi, N_energy = Pmu[:, 0].view(-1, 1), Pmu[:, 1].view(-1, 1), Pmu[:, 2].view(-1, 1), self.nodes[:, 3].view(-1, 1)
        if self._it == 4:
            return
        self.forward(i, edge_index_n, N_pT, N_eta, N_phi, N_energy)


class Recursive(MessagePassing):
    def __init__(self):
        super().__init__()

        self.O_edge_top = None
        self.L_edge_top = "CEL"

        # self.O_edge_lep = None
        # self.L_edge_lep = "CEL"

        self._top = RecursiveBase()
        # self._res = RecursiveBase()
        # self._lep = RecursiveBase()

        end = 6
        # self._top_e = Seq(Linear(4, end), Linear(end, end), Tanh(), Linear(end, 2))

    def forward(self, i, edge_index, N_pT, N_eta, N_phi, N_energy):
        self.O_edge_top = self._top(i, edge_index, N_pT, N_eta, N_phi, N_energy).edge
        # self.O_edge_lep = self._lep(i, edge_index, N_pT, N_eta, N_phi, N_energy).edge
        # self.O_edge_top = self._top_e(torch.cat([self.O_edge_top, self.O_edge_lep], -1))

        topology = self.O_edge_top.max(-1)[1]  # + self.O_edge_lep.max(-1)[1]

        # edge_index = torch.cat([edge_index[0][topology].view(1, -1), edge_index[0][topology].view(1, -1)], 0)
        # self.O_edge_top = self._top(i, edge_index, N_pT, N_eta, N_phi, N_energy).edge
