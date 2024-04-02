from torch_geometric.nn import MessagePassing, LayerNorm, aggr
from torch_geometric.utils import to_dense_adj
from torch_geometric.nn import GCNConv

import torch
from torch.nn import Sequential as Seq, Linear
from torch.nn import ReLU

import pyc
import pyc.Transform as transform
import pyc.Graph.Base as graph
import pyc.Physics.Cartesian as physics
import pyc.NuSol.Cartesian as nusol


class RecursiveGraphNeuralNetwork(MessagePassing):

    def __init__(self):

        super().__init__(aggr = None)

        try: dev = self.__param__["device"]
        except AttributeError: dev = "cuda:0"

        try: self._gev = self.__param__["gev"]
        except AttributeError: self._gev = False

        try: self._nuR = self.__params__["nu_reco"]
        except AttributeError: self._nuR = False

        self.O_top_edge = None
        self.L_top_edge = "CEL"

        self.O_ntops = None
        self.L_ntops = "CEL"

        self.soft_aggr = aggr.SoftmaxAggregation(learn = True)
        self.max_aggr  = aggr.MaxAggregation()
        self.var_aggr  = aggr.VarAggregation()

        self._o = 2
        self._rep = 32

        self._dx  = 5
        self.rnn_dx = Seq(
                Linear(self._dx*2, self._rep),
                LayerNorm(self._rep), ReLU(),
                Linear(self._rep, self._rep)
        )

        self._x   = 7
        self.rnn_x = Seq(
                Linear(self._x, self._rep),
                LayerNorm(self._rep),
                Linear(self._rep, self._rep)
        )

        self.rnn_mrg = Seq(
                Linear(self._rep*2, self._rep),
                LayerNorm(self._rep), ReLU(),
                Linear(self._rep, self._o)
        )

        self.node_feat = Seq(Linear(18, self._rep), Linear(self._rep, self._rep))
        self.node_delta = Seq(Linear(6, self._rep), ReLU(), Linear(self._rep, self._rep))
        self.graph_feat = Seq(
                Linear(self._rep*6, self._rep),
                Linear(self._rep, self._rep),
                Linear(self._rep, 5)
        )

    def message(self, trk_i, trk_j, pmc_i, pmc_j):
        pmci ,    _ = graph.unique_aggregation(trk_i, self.pmc)
        pmcj ,    _ = graph.unique_aggregation(trk_j, self.pmc)
        pmc_ij, pth = graph.unique_aggregation(torch.cat([trk_i, trk_j], -1), self.pmc)

        m_i, m_j, m_ij = physics.M(pmci), physics.M(pmcj), physics.M(pmc_ij)
        jmp = (pth > -1).sum(-1, keepdims = True)
        dR  = physics.DeltaR(pmci, pmcj)

        dx = [m_j, m_j - m_i, pmc_j, pmc_j - pmc_i]
        self._hdx = self.rnn_dx(torch.cat(dx, -1).to(dtype = torch.float))

        _x = [m_ij, dR, jmp, pmc_ij]
        self._hx  = self.rnn_x(torch.cat(_x, -1).to(dtype = torch.float))

        self._hid = self.rnn_mrg(torch.cat([self._hx, self._hx - self._hdx], -1))
        return self._hid

    def aggregate(self, message, edge_index, pmc, trk):
        gr_  = graph.edge_aggregation(edge_index, message, self.pmc)[1]
        trk_ = gr_["clusters"][gr_["reverse_clusters"]]
        cls  = gr_["clusters"].size(0)

        if cls >= self._cls: return self._hid
        self._cls = cls
        self.iter += 1

        return self.propagate(edge_index, pmc = gr_["node_sum"], trk = trk)

    def forward(self,
                edge_index, batch, G_met, G_phi, G_n_jets, G_n_lep,
                N_pT, N_eta, N_phi, N_energy, N_is_lep, N_is_b
        ):

        self.pmu      = torch.cat([N_pT, N_eta, N_phi, N_energy], -1)
        self.pmc      = transform.PxPyPzE(self.pmu)
        self._index   = to_dense_adj(edge_index, edge_attr = (edge_index[0] > -1).cumsum(-1)-1)[0]

        self.batch    = batch
        self.edge_idx = edge_index
        self.pid      = torch.cat([N_is_lep, N_is_b], -1)
        self.met_xy   = torch.cat([transform.Px(G_met, G_phi), transform.Py(G_met, G_phi)], -1)

        if self._nuR:
            data = nusol.Combinatorial(
                    edge_index, batch, self.pmc, self.pid, self.met_xy,
                    null = 10e-10, gev = self._gev, top_up_down = 0.95, w_up_down = 0.95
            )
            nu1, nu2, m1, m2 = data["nu_1f"], data["nu_2f"], data["ms_1f"], data["ms_2f"]
            combi = data["combi"]

        self.iter = 0
        self._hid = None
        self._cls = N_pT.size(0)
        self._t   = torch.ones_like(N_pT).cumsum(0)-1

        self.O_top_edge = self.propagate(edge_index, pmc = self.pmc, trk = self._t)
        self.O_top_edge = self.O_top_edge.softmax(-1)

        gr_  = graph.edge_aggregation(edge_index, self.O_top_edge, self.pmc)[1]

        masses = physics.M(gr_["node_sum"])
        mT = torch.ones_like(masses) * 172.62 * (1000 if not self._gev else 1)
        mW = torch.ones_like(masses) * 80.385 * (1000 if not self._gev else 1)
        mass_delta = torch.cat([mT - masses, mW - masses], -1)

        sft = self.soft_aggr(self.O_top_edge, edge_index[0])
        mx  = self.max_aggr(self.O_top_edge, edge_index[0])
        var = self.var_aggr(self.O_top_edge, edge_index[0])

        feat  = [gr_["node_sum"], physics.M(gr_["node_sum"])]
        feat += [self.pmc, physics.M(self.pmc)]
        feat += [self.pid, sft, mx, var]
        node = self.node_feat(torch.cat(feat, -1).to(dtype = torch.float))

        sft = self.soft_aggr(node, batch)
        mx  = self.max_aggr(node, batch)
        var = self.var_aggr(node, batch)


        feat  = [self.met_xy[batch] - gr_["node_sum"][:, :2]]
        feat += [self.met_xy[batch] - self.pmc[:, :2], mass_delta]
        node_dx = self.node_delta(torch.cat(feat, -1).to(dtype = torch.float))

        sft_dx = self.soft_aggr(node_dx, batch)
        mx_dx  = self.max_aggr(node_dx, batch)
        var_dx = self.var_aggr(node_dx, batch)
        self.O_ntops = self.graph_feat(torch.cat([sft, sft_dx, mx, mx_dx, var, var_dx], -1))
        self.O_ntops = self.O_ntops.softmax(-1)
