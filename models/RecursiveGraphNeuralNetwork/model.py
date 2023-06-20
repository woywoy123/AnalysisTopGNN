import torch
from torch_geometric.nn import MessagePassing, LayerNorm
from torch_geometric.nn.models import MLP
from torch_geometric.utils import remove_self_loops

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

try:
    import PyC.Operators.CUDA as OP
except:
    import PyC.Operators.Tensors as OP

try:
    import PyC.NuSol.CUDA as NuSol
except:
    import PyC.NuSol.Tensors as NuSol

torch.set_printoptions(4, profile="full", linewidth=100000)

from time import sleep
from torch_geometric.utils import to_dense_adj


class ParticleRecursion(MessagePassing):
    def __init__(self):
        super().__init__(aggr=None, flow="target_to_source")
        end = 64

        self.edge = None

        ef = 3
        self._norm_i = LayerNorm(ef, mode="node")
        self._inpt = MLP([ef, end])
        self._edge = MLP([end, 2])

        self._norm_r = LayerNorm(end, mode="node")
        self._rnn = MLP([end * 2, end * 2, end * 2, end])

    def edge_updater(self, edge_index, batch, Pmc, Pmu, PiD):
        i, j = edge_index[0], edge_index[1]
        mlp, _ = self.message(
            batch[i], batch[j], Pmc[i], Pmc[j], Pmu[i], Pmu[j], PiD[i], PiD[j]
        )
        if self.edge is None:
            self.edge = self._norm_r(mlp)
            return

    def message(self, batch_i, batch_j, Pmc_i, Pmc_j, Pmu_i, Pmu_j, PiD_i, PiD_j):
        m_i, m_j, m_ij = PC.Mass(Pmc_i), PC.Mass(Pmc_j), PC.Mass(Pmc_i + Pmc_j)
        f_ij = torch.cat([m_i + m_j, m_ij, torch.abs(m_i - m_j)], -1)
        f_ij = f_ij + self._norm_i(f_ij)
        return self._inpt(f_ij), Pmc_j

    def aggregate(self, message, index, Pmc):
        mlp_ij, Pmc_j = message

        msk = self._idx == 1
        torch.cat([mlp_ij, self.edge[msk]], -1)
        self.edge[msk] = self._norm_r(
            self._rnn(torch.cat([mlp_ij, self.edge[msk]], -1))
        )

        sel = self._edge(self.edge[msk])
        sel = sel.max(-1)[1]
        self._idx[msk] *= (sel == 0).to(dtype=torch.int)

        Pmc = Pmc.clone()
        Pmc.index_add_(0, index[sel == 1], Pmc_j[sel == 1])
        Pmu = Tr.PtEtaPhi(
            Pmc[:, 0].view(-1, 1), Pmc[:, 1].view(-1, 1), Pmc[:, 2].view(-1, 1)
        )
        Pmu = torch.cat([Pmu, Pmc[:, 3].view(-1, 1)], -1)
        return sel, Pmc, Pmu

    def forward(self, i, edge_index, batch, Pmc, Pmu, PiD):
        if self.edge is None:
            self._idx = torch.ones_like(edge_index[0])
            self._idx *= edge_index[0] != edge_index[1]
            self.edge_updater(edge_index, batch=batch, Pmc=Pmc, Pmu=Pmu, PiD=PiD)
            edge_index, _ = remove_self_loops(edge_index)

        _idx = self._idx.clone()
        sel, Pmc, Pmu = self.propagate(
            edge_index, batch=batch, Pmc=Pmc, Pmu=Pmu, PiD=PiD
        )
        edge_index = edge_index[:, sel == 0]
        if edge_index.size()[1] == 0:
            pass
        elif (_idx != self._idx).sum(-1) != 0:
            return self.forward(i, edge_index, batch, Pmc, Pmu, PiD)
        mlp = self._edge(self.edge)
        self.edge = None
        return mlp


class RecursiveGraphNeuralNetwork(MessagePassing):
    def __init__(self):
        super().__init__(aggr=None, flow="target_to_source")

        self.O_top_edge = None
        self.L_top_edge = "CEL"
        self._edgeRNN = ParticleRecursion()

        self.O_res_edge = None
        self.L_res_edge = "CEL"
        self._resRNN = ParticleRecursion()

    def NuNuCombinatorial(self, edge_index, batch, Pmu, PiD, G_met, G_phi):
        i, j, batch = edge_index[0], edge_index[1], batch.view(-1)

        # Find edges where the source/dest are a b and lep
        msk = (((PiD[i] + PiD[j]) == 1).sum(-1) == 2) == 1

        # Block out nodes which are neither leptons or b-jets
        _i, _j = i[msk], j[msk]

        # Find the pairs where source particle is the lepton and the destination is a b-jet
        this_lep_i = (PiD[_i][:, 0] == 1).view(-1, 1)
        this_b_i = (PiD[_j][:, 1] == 1).view(-1, 1)
        p_msk_i = torch.cat([this_lep_i, this_b_i], -1).sum(-1) == 2  # enforce this

        # Find the pairs where destination particle is the lepton and the source is a b-jet
        this_lep_j = (PiD[_j][:, 0] == 1).view(-1, 1)
        this_b_j = (PiD[_i][:, 1] == 1).view(-1, 1)
        p_msk_j = torch.cat([this_lep_j, this_b_j], -1).sum(-1) == 2

        # Make sure the that source == destination (destination == source) particle index
        msk_ij = edge_index[:, msk][:, p_msk_i][0] == edge_index[:, msk][:, p_msk_j][1]
        msk_ji = edge_index[:, msk][:, p_msk_i][1] == edge_index[:, msk][:, p_msk_j][0]
        msk_ = msk_ji * msk_ij  # eliminates non-overlapping cases

        # Find the original particle index in the event
        par_ij = edge_index[:, msk][:, p_msk_i][:, msk_]

        # create proxy particle indices (these are used to assign NON-TOPOLOGICALLY CONNECTED PARTICLE PAIRS)
        # e.g. 1 -> 2, 3 -> 4 is ok, but 1 -> 2, 1 -> 4 is not ok (they share the same lepton/b-quark).
        # This means NuNu(p1, p1, p2, p4) would be incorrect, we want NuNu(p1, p3, p2, p4)
        nodes = par_ij.size()[1]
        dst = torch.tensor(
            [i for i in torch.arange(nodes)], dtype=torch.int, device=par_ij.device
        ).view(1, -1)
        src = torch.cat(
            [torch.ones_like(dst) * i for i in torch.arange(nodes)], -1
        ).view(-1)
        dst = torch.cat([dst for _ in torch.arange(nodes)], -1).view(-1)

        # Check whether the particles involved for these proxy node pairs are from the same event (batch).
        b_i = batch.view(-1)[par_ij[0][src]].view(-1)
        b_j = batch.view(-1)[par_ij[1][dst]].view(-1)

        # Make sure we dont double count. We do want cases where [p1, p3, p2, p4] <=> [p3, p1, p4, p2]
        # But not [p1, p1, p2, p4] <=> [p1, p1, p4, p2]
        b_ = (b_j == b_i) * (src != dst)

        # Get the original particle index of the b-jet and lepton for each event
        NuNu_i = par_ij[:, src[b_]]
        NuNu_j = par_ij[:, dst[b_]]

        # Make it look nicer
        NuNu_ = torch.cat([NuNu_i.t(), NuNu_j.t()], -1)

        b1, b2 = NuNu_[:, 1], NuNu_[:, 3]
        l1, l2 = NuNu_[:, 0], NuNu_[:, 2]

        mT = torch.ones_like(b1.view(-1, 1)) * 172.62 * 1000
        mW = torch.ones_like(b1.view(-1, 1)) * 80.385 * 1000
        mN = torch.zeros_like(mW)
        met, phi = G_met[batch[b1]], G_phi[batch[b1]]
        res = NuSol.NuNuPtEtaPhiE(
            Pmu[b1], Pmu[b2], Pmu[l1], Pmu[l2], met, phi, mT, mW, mN, 10e-8
        )
        SkipEvent = res[0]

        if len(res) == 5:
            return SkipEvent
        _pt, _eta, _phi, _e = Pmu[:, 0], Pmu[:, 1], Pmu[:, 2], Pmu[:, 3]
        p3_v = Tr.PxPyPz(_pt, _eta, _phi)

        l1, l2 = l1[SkipEvent == False], l2[SkipEvent == False]
        nu1, nu2 = res[1], res[2]
        l1_v, l2_v = p3_v[l1].view(-1, 1, 3), p3_v[l2].view(-1, 1, 3)
        W_1, W_2 = (nu1 + l1_v).view(-1, 3), (nu2 + l2_v).view(-1, 3)

        # Create a reverse look-up map of the leptons being used (edge_index)
        nu1_msk, nu2_msk = nu1 == 0, nu2 == 0
        l1_map = (torch.ones_like(nu1_msk[:, :, :1]) * (l1.view(-1, 1, 1))).view(-1, 1)
        l2_map = (torch.ones_like(nu2_msk[:, :, :1]) * (l2.view(-1, 1, 1))).view(-1, 1)

        # Remove Zero values solutions
        nu1_msk, nu2_msk = nu1_msk.sum(-1).view(-1) > 0, nu2_msk.sum(-1).view(-1) > 0
        l1_map, l2_map = l1_map[nu1_msk], l2_map[nu2_msk]
        l1l2_map = torch.cat([l1_map, l2_map], -1)
        W_1, W_2 = W_1[nu1_msk], W_2[nu2_msk]

        # Continue here .....
        print(l1l2_map.size())
        exit()
        print(l1l2_map)
        print(W_1)
        print(W_2)

        exit()

    def forward(
        self,
        i,
        edge_index,
        batch,
        G_met,
        G_phi,
        G_n_jets,
        N_pT,
        N_eta,
        N_phi,
        N_energy,
        N_is_lep,
        N_is_b,
        G_T_n_nu,
    ):
        Pmc = torch.cat([Tr.PxPyPz(N_pT, N_eta, N_phi), N_energy], -1)
        Pmu = torch.cat([N_pT, N_eta, N_phi, N_energy], -1)
        PiD = torch.cat([N_is_lep, N_is_b], -1)
        batch = batch.view(-1, 1)

        # self.NuNuCombinatorial(edge_index, batch, Pmu, PiD, G_met, G_phi)
        # self.propagate(edge_index, batch = batch, Pmc = Pmc, PiD = PiD, met = G_met, phi = G_phi)

        self.O_top_edge = self._edgeRNN(i, edge_index, batch, Pmc, Pmu, PiD)
        self.O_res_edge = self._resRNN(i, edge_index, batch, Pmc, Pmu, PiD)
