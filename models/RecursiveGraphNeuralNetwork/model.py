import torch
from torch_geometric.nn import MessagePassing, LayerNorm
from torch_geometric.nn.models import MLP
from torch_geometric.utils import remove_self_loops

try:
    import PyC.Transform.CUDA as Tr
    import PyC.Physics.CUDA.Polar as PP
    import PyC.Physics.CUDA.Cartesian as PC
    import PyC.Operators.CUDA as OP
    import PyC.NuSol.CUDA as NuSol
except:
    import PyC.Transform.Tensors as Tr
    import PyC.Physics.Tensors.Polar as PP
    import PyC.Physics.Tensors.Cartesian as PC
    import PyC.Operators.Tensors as OP
    import PyC.NuSol.Tensors as NuSol
torch.set_printoptions(4, profile="full", linewidth=100000)
from time import sleep
from torch_geometric.utils import to_dense_adj


class ParticleRecursion(MessagePassing):
    def __init__(self):
        super().__init__(aggr=None, flow="target_to_source")
        end = 32

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
        super().__init__(aggr = "max")

        self.O_top_edge = None
        self.L_top_edge = "CEL"
        self._edgeRNN = ParticleRecursion()

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

        _sols = NuSol.NuNuPtEtaPhiE(
            Pmu[b1], Pmu[b2], Pmu[l1], Pmu[l2], met, phi, mT, mW, mN, 10e-8
        )

        if len(_sols) == 5:
            return False
        SkipEvent = _sols[0]

        # Get the Neutrino Solutions
        Pmc_nu1, Pmc_nu2 = _sols[1], _sols[2]

        # Create a mask such that 0 valued solutions are excluded
        nu1_msk = Pmc_nu1.sum(-1, keepdim = True) != 0
        nu2_msk = Pmc_nu2.sum(-1, keepdim = True) != 0
        _msk = (nu1_msk*nu2_msk).view(-1, 6)

        # Compute the Neutrino 4-vector 
        _e1, _e2 = Pmc_nu1.pow(2), Pmc_nu2.pow(2)
        _e1, _e2 = _e1.sum(-1, keepdim = True), _e2.sum(-1, keepdim = True)
        _e1, _e2 = _e1.pow(0.5), _e2.pow(0.5)
        Pmc_nu1, Pmc_nu2 = torch.cat([Pmc_nu1, _e1], -1), torch.cat([Pmc_nu2, _e2], -1)

        # Remove l which are marked as a skip event.
        l1, l2 = l1[SkipEvent == False], l2[SkipEvent == False]

        # Further Remove pairs based on null neutrino solutions 
        l1, l2 = (l1.view(-1, 1)*_msk)[_msk], (l2.view(-1, 1)*_msk)[_msk]

        # Collect only the leptons from the original vector and match them to the neutrino
        lep1 = Tr.PxPyPz(Pmu[l1][:, 0].view(-1, 1), Pmu[l1][:, 1].view(-1, 1), Pmu[l1][:, 2].view(-1, 1))
        lep2 = Tr.PxPyPz(Pmu[l2][:, 0].view(-1, 1), Pmu[l2][:, 1].view(-1, 1), Pmu[l2][:, 2].view(-1, 1))

        W1 = torch.cat([lep1, Pmu[l1][:, 3].view(-1, 1)], -1) + Pmc_nu1[_msk]
        W2 = torch.cat([lep2, Pmu[l2][:, 3].view(-1, 1)], -1) + Pmc_nu2[_msk]

        Pmu_W1 = torch.cat([Tr.PtEtaPhi(W1[:, 0].view(-1, 1), W1[:, 1].view(-1, 1), W1[:, 2].view(-1, 1)), W1[:, 3].view(-1, 1)], -1)
        Pmu_W2 = torch.cat([Tr.PtEtaPhi(W2[:, 0].view(-1, 1), W2[:, 1].view(-1, 1), W2[:, 2].view(-1, 1)), W2[:, 3].view(-1, 1)], -1)

        return Pmu_W1, Pmu_W2, W1, W2, l1, l2

    def forward(
        self, i, edge_index, batch, G_met, G_phi, G_n_jets,
        N_pT, N_eta, N_phi, N_energy, N_is_lep, N_is_b, G_T_n_nu,
    ):

        Pmc = torch.cat([Tr.PxPyPz(N_pT, N_eta, N_phi), N_energy], -1)
        Pmu = torch.cat([N_pT, N_eta, N_phi, N_energy], -1)
        PiD = torch.cat([N_is_lep, N_is_b], -1)
        batch = batch.view(-1, 1)

        o = self.NuNuCombinatorial(edge_index, batch, Pmu, PiD, G_met, G_phi)

        top_edges = self._edgeRNN(i, edge_index, batch, Pmc, Pmu, PiD)
        if not o: self.O_top_edge = top_edges
        else:
            Pmu_W1, Pmu_W2, Pmc_W1, Pmc_W2, l1, l2 = o
            for k in torch.arange(l1.size()[0]):
                Pmu_c = Pmu.clone()
                Pmu_c[l1[k]] = Pmu_W1[k]
                Pmu_c[l2[k]] = Pmu_W2[k]

                Pmc_c = Pmc.clone()
                Pmc_c[l1[k]] = Pmc_W1[k]
                Pmc_c[l2[k]] = Pmc_W2[k]

                top_edges += self._edgeRNN(i, edge_index, batch, Pmc_c, Pmu_c, PiD)
            top_edges /= (l1.size()[0]+1)
        self.O_top_edge = top_edges
