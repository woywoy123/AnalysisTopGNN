import torch
from torch_geometric.nn import MessagePassing
from torch_geometric.utils import degree, to_dense_adj
from torch_geometric.nn.resolver import aggregation_resolver as aggr_resolver
from torch.nn import Sequential as Seq, Linear, ReLU, Tanh
try:
    import PyC.Transform.CUDA as TC
    import PyC.Physics.CUDA.Cartesian as PCC
    import PyC.Physics.CUDA.Polar as PCP
except:
    import PyC.Transform.Tensor as TC
    import PyC.Physics.Tensor.Cartesian as PCC
    import PyC.Physics.Tensor.Polar as PCP

class Base(MessagePassing):
    
    def __init__(self):
        super().__init__(aggr = None, flow = "source_to_target")
       
        end = 256
        self._MLP = Seq(
                Linear(1 + end + 2, end),
                Tanh(), ReLU(), 
                Linear(end, 2)
        )
        self._Feat = Seq(
                Linear(4, end),
                Tanh(), ReLU(), 
                Linear(end, end)
        )

        self.aggr_module_add = aggr_resolver("add")

    # j is the source, i is the destination
    def message(self, edge_index, pmc_i, pmc_j, pmc__i, pmc__j, mlp_ji, mlp_i, mlp_j):
        src, dst = edge_index
        edge = mlp_ji.max(-1)[1].view(-1, 1)
        
        m__j, m_j = PCC.Mass(pmc__j + pmc_i), PCC.Mass(pmc__j)
        dR_ji = PCC.DeltaR(pmc_i[:,0], pmc_j[:,0], pmc_i[:,1], pmc_j[:,1], pmc_i[:,2], pmc_j[:,2])
        dR__ji = PCC.DeltaR(pmc_i[:,0], pmc__j[:,0], pmc_i[:,1], pmc__j[:,1], pmc_i[:,2], pmc__j[:,2])

        Edge_ji = self._Feat(torch.cat([m__j, m_j, dR_ji, dR__ji], -1))
        mlp_ji = self._MLP(torch.cat([(self._it +1)*(edge - 0.5), Edge_ji, mlp_ji - mlp_i - mlp_j], -1))      
        
        sel = (mlp_ji.max(-1)[1]*(src != dst)).view(-1, 1)
        return pmc_i*sel, mlp_ji, src

    def aggregate(self, message, index, pmc_, mlp):
        (pmc_i, mlp_ji, src), dst = message, index
        edge = (mlp_ji.max(-1)[1].view(-1, 1))
        
        pmc = pmc_.clone()
        pmc += self.aggr_module_add(pmc_i, dst)

        mlp = self.aggr_module_add(mlp_ji, src) + mlp
        mlp /= (degree(index).view(-1, 1))

        px__j, py__j, pz__j = pmc[src][:, 0], pmc[src][:,1], pmc[src][:,2]
        px_j, py_j, pz_j = pmc_[src][:, 0], pmc_[src][:,1], pmc_[src][:,2]
        px_i, py_i, pz_i = pmc_[dst][:, 0], pmc_[dst][:,1], pmc_[dst][:,2]

        dR_ji = PCC.DeltaR(px_i, px_j, py_i, py_j, pz_i, pz_j)
        dR__ji = PCC.DeltaR(px_i, px__j, py_i, py__j, pz_i, pz__j)
        m_, m = PCC.Mass(pmc), PCC.Mass(pmc_)

        Edge_ji = self._Feat(torch.cat([m_[src]*edge, m[src], dR_ji, dR__ji], -1))
        mlp_ji = self._MLP(torch.cat([(self._it +1)*(edge - 0.5), Edge_ji, mlp_ji - mlp[src] - mlp[index]], -1))      
        return mlp_ji, mlp, pmc_

    def forward(self, edge_index, Pmc):
        (src, dst), self._it = edge_index, 0
        pmc, it = Pmc.clone(), degree(dst).max(-1)[0]
        edge = torch.ones_like(torch.cat([degree(dst).view(-1, 1) for i in range(2)], -1))[:, 0].view(-1, 1)
        
        mass_n = PCC.Mass(pmc)
        mass_ji, mass_j = PCC.Mass(pmc[src] + pmc[dst]*(src != dst).view(-1, 1)), PCC.Mass(pmc)[src]
        px_j, py_j, pz_j = pmc[src][:, 0], pmc[src][:,1], pmc[src][:,2]
        px_i, py_i, pz_i = pmc[dst][:, 0], pmc[dst][:,1], pmc[dst][:,2]
        dR_ji = PCC.DeltaR(px_i, px_j, py_i, py_j, pz_i, pz_j)
        
        Mass_n = self._Feat(torch.cat([mass_n, mass_n, edge, edge], -1))
        Mass_ji = self._Feat(torch.cat([mass_ji, mass_j, dR_ji, edge[src]], -1))

        mlp = self._MLP(torch.cat([(self._it+1)*(edge - 0.5), Mass_n, -edge, edge], -1))
        mlp_ji = self._MLP(torch.cat([(self._it+1)*(edge[src] - 0.5), Mass_ji, mlp[src] - mlp[src] - mlp[dst]], -1))
        for i in torch.arange(it):
            mlp_ji, mlp, pmc = self.propagate(edge_index, pmc = Pmc, pmc_ = pmc, mlp_ji = mlp_ji, mlp = mlp)
            self._it += 1
        return mlp_ji


class GraphPassing(MessagePassing):
    
    def __init__(self):
        super().__init__()
        self._top = Base()
        self.O_edge = None
        self.L_edge = "CEL"
        self.C_edge = True 
    
        end = 256
        self._MLP = Seq(
                Linear(8, end),
                Tanh(), 
                ReLU(), 
                Linear(end, 2)
        )

        self.O_edge_res = None 
        self.L_edge_res = "CEL"
        self.C_edge_res = True

        self.O_signal = None 
        self.L_signal = "CEL"
        self.C_signal = True

    def message(self, pmc_i, pmc_j, edge):
        px_i, py_i, pz_i = pmc_i[:, 0], pmc_i[:, 1], pmc_i[:, 2] 
        px_j, py_j, pz_j = pmc_j[:, 0], pmc_j[:, 1], pmc_j[:, 2] 
        dr = PCC.DeltaR(px_i, px_j, py_i, py_j, pz_i, pz_j)
        return self._MLP(torch.cat([PCC.Mass(pmc_i + pmc_j*(1 - edge)), dr, PCC.Mass(pmc_j), PCC.Mass(pmc_i), pmc_j - pmc_i], -1))

    def forward(self, edge_index, batch, N_pT, N_eta, N_phi, N_energy, G_met, G_met_phi):
        pt, eta, phi, E = N_pT/1000, N_eta, N_phi, N_energy/1000
        Pmc = torch.cat([TC.PxPyPz(pt, eta, phi), E.view(-1, 1)], -1)
        src, dst = edge_index 

        self.O_edge = self._top(edge_index, Pmc)
        sel = self.O_edge.max(-1)[1].view(-1, 1) 

        tops = self.aggr_module(Pmc[src]*sel, dst)
        zero = (PCC.Mass(tops) == 0).view(-1)
        tops[zero] = Pmc[zero]

        self.O_edge_res = self.message(tops[dst], tops[src], sel)
        self.O_signal = self.aggr_module(self.O_edge_res, batch[src])        

