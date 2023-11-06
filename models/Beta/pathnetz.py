import torch
import torch.nn as nn
from torch_geometric.nn import MessagePassing
from torch_geometric.utils import to_dense_adj, degree
from torch.nn import Sequential as Seq, Linear, ReLU, Tanh

# custom pyc extension functions
import pyc
import pyc.Graph.Cartesian as graph
import pyc.Graph.Base as graph_base
import pyc.NuSol.Polar as nusol
import pyc.Physics.Cartesian as physics
import pyc.Transform as transform
from time import sleep

torch.set_printoptions(precision=3, sci_mode = True)


def init_norm(m):
    if not type(m) == nn.Linear: return
    nn.init.uniform(m.weight)

def NuNuCombinatorial(edge_index, batch, pmu, pid, G_met, G_phi, masses, msk, idx):
    i, j = edge_index
    pmu = pmu.to(dtype = torch.double)
    masses = masses.to(dtype = torch.double)
    sol_feat = torch.zeros_like(i).to(dtype = torch.double)-1
    pmu_i, pmu_j = torch.zeros_like(pmu[i]), torch.zeros_like(pmu[j])
    if not msk.sum(-1): return sol_feat, pmu_i, pmu_j

    # Find edges where the source/dest are a b and lep
    msk = (((pid[i] + pid[j]) == 1).sum(-1) == 2)*msk[i]

    # Block out nodes which are neither leptons or b-jets
    _i, _j = i[msk], j[msk]

    # Find the pairs where source particle is the lepton and the destination is a b-jet
    p_msk_i = (pid[_i][:, 0] * pid[_j][:, 1]) == 1

    # Find the pairs where destination particle is the lepton and the source is a b-jet
    p_msk_j = (pid[_j][:, 0] * pid[_i][:, 1]) == 1

    # Make sure the that source == destination (destination == source) particle index
    msk_ij = _i[p_msk_i] == _j[p_msk_j]
    msk_ji = _j[p_msk_i] == _i[p_msk_j]
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
    li, bi, lj, bj = [NuNu_[:, i] for i in range(4)]

    # Run the algorithm
    met_phi = torch.cat([G_met[batch[bi]], G_phi[batch[bi]]], -1).to(dtype = torch.double)
    _sols = nusol.NuNu(pmu[bi], pmu[bj], pmu[li], pmu[lj], met_phi, masses, 10e-8)
    nu1, nu2, dist, _, _, _, nosol = _sols
    is_sol = nosol == False


    # Populate the null tensors with synthetic neutrinos 
    nu1 = torch.cat([nu1, (nu1.pow(2).sum(-1, keepdim = True)).pow(0.5)], -1)
    nu2 = torch.cat([nu2, (nu2.pow(2).sum(-1, keepdim = True)).pow(0.5)], -1)

    # Create a correct edge mapping
    if not dist.size(1): return sol_feat, pmu_i, pmu_j
    e_i, e_j = NuNu_i[:, is_sol], NuNu_j[:, is_sol]
    idx_i, idx_j = idx[e_i[0], e_i[1]], idx[e_j[0], e_j[1]]
    sol_feat[idx_i] = dist[:, 0][is_sol]
    sol_feat[idx_j] = dist[:, 0][is_sol]
    pmu_i[idx_i] = nu1[:, 0, :][is_sol]
    pmu_j[idx_j] = nu2[:, 0, :][is_sol]
    return sol_feat, pmu_i, pmu_j

def NuCombinatorial(edge_index, batch, pmu, pid, G_met, G_phi, masses, msk):
    SXX = torch.tensor([[100, 0, 0, 100]], device = msk.device, dtype = pmu.dtype)
    i, j = edge_index

    # Output
    pmu_i = torch.zeros_like(pmu[i])
    pmu_j = torch.zeros_like(pmu[i])
    chi2_f = torch.zeros_like(i).to(dtype = torch.double)-1

    # make the network fully connected, and get only edges where src and dst are 
    # paired with leptons and b-jets
    pairs = (pid[i, 0] * pid[j, 1])*msk[i]

    # find which one of the nodes is the lepton and the b-jet
    l_, b_ = i[pid[i, 0]*pairs], j[pid[j, 1]*pairs]
    if not msk.sum(-1): return chi2_f, pmu_i, pmu_j

    # Run the algorithm
    met_phi = torch.cat([G_met, G_phi], -1)[batch[l_]]
    nu, chi2 = nusol.Nu(pmu[l_], pmu[b_], met_phi, masses, SXX, 10e-8)

    # Create a mask such that 0 valued solutions are excluded
    nu_low_msk = ((chi2 != -1).cumsum(-1)-1) == 0
    nu_, chi2_ = nu[nu_low_msk], chi2[nu_low_msk]
    nu_ = torch.cat([nu_, nu_.pow(2).sum(-1, keepdim = True)], -1)

    nu_feat = torch.cat([nu_low_msk.sum(-1, keepdim = True)]*4, -1).to(dtype = torch.double)
    nu_feat[nu_feat.sum(-1) != 0] *= nu_

    chi2_feat = torch.cat([nu_low_msk.sum(-1, keepdim = True)], -1)
    chi2_feat = chi2_feat.to(dtype = torch.double).view(-1)
    chi2_feat[nu_feat.sum(-1) != 0] = chi2_

    # populate the nodes
    pmu_i[pairs] += nu_feat
    chi2_f[pairs] = chi2_feat

    return chi2_f, pmu_i, pmu_j



class ParticleRecursion(MessagePassing):

    def __init__(self):
        super().__init__(aggr = None)
        self._edge = Seq(Linear(5, 18), Tanh(), ReLU(), Linear(18, 7))

        self._encoder = Seq(Linear(4, 256), Tanh(), ReLU(), Linear(256, 4))
        self._decoder = Seq(Linear(5, 256), Tanh(), ReLU(), Linear(256, 1))

        self._red = Seq(Linear(7, 2))
        self._edge.apply(init_norm)
        self._red.apply(init_norm)

    def message(self, edge_index, pmc, trk_i, trk_j):
        src, dst = edge_index
        src, dst = src.view(-1, 1), dst.view(-1, 1)
        idx = self._idx_mlp[dst, src].view(-1)

        pmc_i  = (graph_base.unique_aggregation(trk_i, pmc) + self._nu_i[idx]).to(dtype = torch.float)
        pmc_j  = (graph_base.unique_aggregation(trk_j, pmc) + self._nu_j[idx]).to(dtype = torch.float)
        pmc_ij = graph_base.unique_aggregation(torch.cat([src, trk_i], -1), pmc)
        pmc_ij = (pmc_ij + self._nu_i[idx] + self._nu_j[idx]).to(dtype = torch.float)

        m_ij, m_i, m_j = physics.M(pmc_ij), physics.M(pmc_i), physics.M(pmc_j)
        enc_ij, enc_i, enc_j = self._encoder(pmc_ij), self._encoder(pmc_i), self._encoder(pmc_j)
        dec_ij = self._decoder(torch.cat([enc_ij - pmc_ij, m_ij], -1)) - m_ij
        dec_i  = self._decoder(torch.cat([enc_i - pmc_i  , m_i ], -1)) - m_i
        dec_j  = self._decoder(torch.cat([enc_j - pmc_j  , m_j ], -1)) - m_j

        feat = torch.cat([m_ij, m_j, self._sol_ij[idx], dec_ij, dec_i - dec_j], -1)
        feat = feat.to(dtype = torch.float)
        self._hid = self._edge(feat)
        return edge_index, self._hid, self._red(self._hid).max(-1)[1]

    def aggregate(self, message, trk, pmc):
        edge_index, mlp_edge, sel = message
        src, dst = edge_index

        if self.O_top_edge is None:
            self.O_top_edge = mlp_edge
            return self.propagate(edge_index, pmc = pmc, trk = trk)

        idx = self._idx_mlp[dst, src]
        if self._sel is not None: msk = self._sel[idx] == sel
        else: self._sel, msk = sel, sel == 1
        self._sel[idx] = sel.clone()

        if not (msk != True).sum(-1): return self.O_top_edge
        if not msk.sum(-1): return self.O_top_edge
        elif sel.sum(-1) == sel.size(0): return self.O_top_edge
        elif sel[msk].sum(-1) == 0: return self.O_top_edge
        elif sel.sum(-1) == 0: return self.O_top_edge

        gr = graph.edge(edge_index, sel, pmc, True)[1]
        trk = gr["clusters"][gr["reverse_clusters"]]
        self.O_top_edge[idx] = mlp_edge
        return self.propagate(edge_index[:, msk == False], pmc = pmc, trk = trk)

    def forward(self, edge_index, batch, pmc, nu_i, nu_j, sol):

        self._sel = None
        self.O_top_edge = None
        track = (torch.ones_like(batch).cumsum(-1)-1).view(-1, 1)
        mass = physics.M(pmc)

        self._hid = torch.cat([track]*3, -1)
        self._hid = torch.zeros_like(self._hid)
        self._hid = torch.cat([mass, mass, self._hid], -1)[edge_index[0]].clone()

        self._hid = self._edge(self._hid.to(dtype = torch.float))
        self._sol_ij = sol.view(-1, 1)
        self._nu_i = nu_i
        self._nu_j = nu_j

        self._idx_mlp = torch.cumsum(torch.ones_like(edge_index[0]), dim = -1)-1
        self._idx_mlp = to_dense_adj(edge_index, edge_attr = self._idx_mlp)[0]

        return self._red(self.propagate(edge_index, pmc = pmc, trk = track))

class RecursivePathNetz(MessagePassing):

    def __init__(self):
        super().__init__()
        self._top = ParticleRecursion()
        self.O_top_edge = None
        self.L_top_edge = "CEL"

        self._res = ParticleRecursion()
        self.O_res_edge = None
        self.L_res_edge = "CEL"

        self.O_signal = None
        self.L_signal = "CEL"

        self._signal = Seq(
                Linear(8, 256)  , Tanh(),
                Linear(256, 256), ReLU(),
                Linear(256, 2)
        )


    def NuNu(self, edge_index, batch, pmu, pid, G_met, G_phi, masses, msk, idx):
        return NuNuCombinatorial(edge_index, batch, pmu, pid, G_met, G_phi, masses, msk, idx)

    def Nu(self, edge_index, batch, pmu, pid, G_met, G_phi, masses, msk):
        return NuCombinatorial(edge_index, batch, pmu, pid, G_met, G_phi, masses, msk)

    def forward(self, edge_index, batch, G_met, G_phi, G_n_jets, G_n_lep, N_pT, N_eta, N_phi, N_energy, N_is_lep, N_is_b):

        pmu = torch.cat([N_pT / 1000, N_eta, N_phi, N_energy / 1000], -1)
        pmc = transform.PxPyPzE(pmu)
        pid = torch.cat([N_is_lep, N_is_b], -1)
        src, dst = edge_index

        mT = torch.ones_like(N_pT.view(-1, 1)) * 172.62
        mW = torch.ones_like(N_pT.view(-1, 1)) * 80.385
        mN = torch.zeros_like(mW)
        masses = torch.cat([mW, mT, mN], -1)

        idx = torch.cumsum(torch.ones_like(edge_index[0]), dim = -1)-1
        idx = to_dense_adj(edge_index, edge_attr = idx)[0]

        _, n_bjets = (batch[N_is_b.view(-1) == 1]*1).unique(return_counts = True, dim = -1)
        msk_nu = (n_bjets[batch] > 1)*(G_n_lep.view(-1)[batch] == 1)
        msk_e_nu = msk_nu[src]

        msk_nunu = (n_bjets[batch] > 1)*(G_n_lep.view(-1)[batch] == 2)
        msk_e_nunu = msk_nunu[src]

        chi2 = torch.zeros_like(src).to(dtype = torch.double)
        pmu_i, pmu_j = torch.zeros_like(pmu[src]), torch.zeros_like(pmu[src])

        # weird segmentation fault with single neutrino reconstruction
        # Intel MKL ERROR: Parameter 3 was incorrect on entry to DGEBAL.
        #chi2_n , pmu_i_n, pmu_j_n = self.Nu(  edge_index, batch, pmu, pid, G_met, G_phi, masses, msk_nu)
        chi2_nn, pmu_inn, pmu_jnn = self.NuNu(edge_index, batch, pmu, pid, G_met, G_phi, masses, msk_nunu, idx)

        #pmu_i[msk_e_nu]   += pmu_i_n[msk_e_nu]
        pmu_i[msk_e_nunu] += pmu_inn[msk_e_nunu]

        #pmu_j[msk_e_nu]   += pmu_j_n[msk_e_nu]
        pmu_j[msk_e_nunu] += pmu_jnn[msk_e_nunu]

        #chi2[msk_e_nu]   += chi2_n[msk_e_nu]
        chi2[msk_e_nunu] += chi2_nn[msk_e_nunu]

        self.O_top_edge = self._top(edge_index, batch, pmc, pmu_i, pmu_j, chi2)
        self.O_res_edge = self._res(edge_index, batch, pmc, pmu_i, pmu_j, chi2)

        compress = torch.zeros_like(torch.cat([G_n_lep, G_n_lep], -1)).to(dtype = torch.float)
        compress[batch[dst]] += (self.O_top_edge - self.O_res_edge)

        is_res = self.O_res_edge.max(-1)[1] == 1
        is_top = self.O_top_edge.max(-1)[1] == 1
        common = (is_res * is_top)

        is_sig = torch.zeros_like(torch.cat([G_n_lep]*3, -1)).to(dtype = torch.float)
        is_sig[batch[dst]] += torch.cat([is_res.view(-1, 1), is_top.view(-1, 1), common.view(-1, 1)], -1)

        graph_feat = torch.cat([G_n_lep, G_n_jets, n_bjets.view(-1, 1)], -1)
        self.O_signal = self._signal(torch.cat([graph_feat, is_sig, compress], -1))
