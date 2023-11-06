import torch
from torch_geometric.nn import MessagePassing, LayerNorm
from torch_geometric.utils import remove_self_loops
from torch_geometric.nn.models import MLP

import pyc.Transform as transform
import pyc.Physics as physics
import pyc.NuSol as nusol

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

    def edge_updater(self, edge_index, batch, pmc, pmu, pid):
        i, j = edge_index[0], edge_index[1]
        mlp, _ = self.message(batch[i], batch[j], pmc[i], pmc[j], pmu[i], pmu[j], pid[i], pid[j])
        if self.edge is not None: pass
        else: self.edge = self._norm_r(mlp)

    def message(self, batch_i, batch_j, pmc_i, pmc_j, pmu_i, pmu_j, pid_i, pid_j):
        m_i, m_j, m_ij = physics.M(pmc_i), physics.M(pmc_j), physics.M(pmc_i + pmc_j)
        f_ij = torch.cat([m_i + m_j, m_ij, torch.abs(m_i - m_j)], -1)
        f_ij = f_ij.to(dtype = torch.float)
        f_ij = f_ij + self._norm_i(f_ij)
        return self._inpt(f_ij), pmc_j

    def aggregate(self, message, index, pmc):
        mlp_ij, pmc_j = message

        msk = self._idx == 1
        torch.cat([mlp_ij, self.edge[msk]], -1)
        self.edge[msk] = self._norm_r(self._rnn(torch.cat([mlp_ij, self.edge[msk]], -1)))

        sel = self._edge(self.edge[msk])
        sel = sel.max(-1)[1]
        self._idx[msk] *= (sel == 0).to(dtype=torch.int)

        pmc = pmc.clone()
        pmc.index_add_(0, index[sel == 1], pmc_j[sel == 1])
        pmu = transform.PtEtaPhiE(pmc)
        return sel, pmc, pmu

    def forward(self, i, edge_index, batch, pmc, pmu, pid):
        if self.edge is None:
            self._idx = torch.ones_like(edge_index[0])
            self._idx *= edge_index[0] != edge_index[1]
            self.edge_updater(edge_index, batch = batch, pmc = pmc, pmu = pmu, pid = pid)
            edge_index, _ = remove_self_loops(edge_index)

        _idx = self._idx.clone()
        sel, pmc, pmu = self.propagate(edge_index, batch=batch, pmc = pmc, pmu = pmu, pid = pid)
        edge_index = edge_index[:, sel == 0]
        if edge_index.size()[1] == 0: pass
        elif (_idx != self._idx).sum(-1) != 0: return self.forward(i, edge_index, batch, pmc, pmu, pid)
        mlp = self._edge(self.edge)
        self.edge = None
        return mlp


class RecursiveGraphNeuralNetwork(MessagePassing):
    def __init__(self):
        super().__init__(aggr = "max")

        self.O_top_edge = None
        self.L_top_edge = "CEL"
        self._edgeRNN = ParticleRecursion()

    def NuNuCombinatorial(self, edge_index, batch, pmu, pid, G_met, G_phi):
        i, j = edge_index[0], edge_index[1]

        # Find edges where the source/dest are a b and lep
        msk = (((pid[i] + pid[j]) == 1).sum(-1) == 2) == 1

        # Block out nodes which are neither leptons or b-jets
        _i, _j = i[msk], j[msk]

        # Find the pairs where source particle is the lepton and the destination is a b-jet
        this_lep_i = (pid[_i][:, 0] == 1).view(-1, 1)
        this_b_i = (pid[_j][:, 1] == 1).view(-1, 1)
        p_msk_i = torch.cat([this_lep_i, this_b_i], -1).sum(-1) == 2  # enforce this

        # Find the pairs where destination particle is the lepton and the source is a b-jet
        this_lep_j = (pid[_j][:, 0] == 1).view(-1, 1)
        this_b_j = (pid[_i][:, 1] == 1).view(-1, 1)
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
        b_i = batch[par_ij[0][src]].view(-1)
        b_j = batch[par_ij[1][dst]].view(-1)

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
        masses = torch.cat([mW, mT, mN], -1)
        met_phi = torch.cat([G_met[batch[b1]], G_phi[batch[b1]]], -1).view(-1, 2)

        _sols = nusol.Polar.NuNu(
                pmu[b1].to(dtype = torch.double),
                pmu[b2].to(dtype = torch.double),
                pmu[l1].to(dtype = torch.double),
                pmu[l2].to(dtype = torch.double),
                met_phi.to(dtype = torch.double),
                masses.to(dtype = torch.double) , 10e-8)
        nu1, nu2, dist, _, _, _, nosol = _sols
        nosol = nosol == False

        # Create a mask such that 0 valued solutions are excluded
        nu1_msk = nu1.sum(-1, keepdim = True) != 0
        nu2_msk = nu2.sum(-1, keepdim = True) != 0
        if nu1_msk.size()[1]: pass
        else: return

        # retain the batch index of the solutions
        batch_l1 = (torch.ones_like(nu1)*l1.view(-1, 1, 1)).unique(False, dim = -1).view(-1, 1)
        batch_l2 = (torch.ones_like(nu1)*l2.view(-1, 1, 1)).unique(False, dim = -1).view(-1, 1)
        nu1, nu2, dist = nu1[nosol], nu2[nosol], dist[nosol]

        # Compute the Neutrino 4-vector 
        _e1, _e2 = nu1.pow(2).sum(-1, keepdim = True), nu2.pow(2).sum(-1, keepdim = True)
        _e1, _e2 = _e1.pow(0.5), _e2.pow(0.5)
        nu1, nu2 = torch.cat([nu1, _e1], -1), torch.cat([nu2, _e2], -1)
        l1, l2 = l1[nosol], l2[nosol]

        # Collect final leptons from the original vector and match them to the neutrino to create W-bosons
        lep1, lep2 = transform.PxPyPzE(pmu[l1]), transform.PxPyPzE(pmu[l2])
        wBos1, wBos2 = (lep1.view(-1, 1, 4) + nu1).view(-1, 4), (lep2.view(-1, 1, 4) + nu2).view(-1, 4)
        pmu_w1, pmu_w2 = transform.PtEtaPhiE(wBos1), transform.PtEtaPhiE(wBos2)

        return pmu_w1, pmu_w2, batch_l1, batch_l2

    def forward(self, i, edge_index, batch, G_met, G_phi, G_n_jets, N_pT, N_eta, N_phi, N_energy, N_is_lep, N_is_b):
        pmu = torch.cat([N_pT, N_eta, N_phi, N_energy], -1)
        pmc = transform.PxPyPzE(pmu)
        pid = torch.cat([N_is_lep, N_is_b], -1)
        batch = batch.view(-1, 1)
        o = self.NuNuCombinatorial(edge_index, batch, pmu, pid, G_met, G_phi)
        if o is not None: pmu_w1, pmu_w2, b1, b2 = o
        self.O_top_edge = self._edgeRNN(i, edge_index, batch, pmc, pmu, pid)
