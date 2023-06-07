import torch
from torch_geometric.nn import MessagePassing
from torch_geometric.utils import degree, to_dense_adj
from torch_geometric.nn.resolver import aggregation_resolver as aggr_resolver
from torch.nn import Sequential as Seq, Linear, ReLU, Tanh
try:
    import PyC.Transform.CUDA as TC
    import PyC.Physics.CUDA.Cartesian as PCC
except:
    import PyC.Transform.Tensor as TC
    import PyC.Physics.Tensor.Cartesian as PCC

class Base(MessagePassing):
    
    def __init__(self):
        super().__init__(aggr = None, flow = "source_to_target")
        end = 256
        self._MLP = Seq(
                Linear(3 + 2, end),
                Tanh(), 
                ReLU(), 
                Linear(end, 2)
        )

        self.aggr_module_add = aggr_resolver("add")

    # j is the source, i is the destination
    def message(self, edge_index, pmc_j, pmc_i, pmc__i, mlp_i, mlp_j):
        src, dst = edge_index

        px_j, py_j, pz_j = pmc_j[:, 0], pmc_j[:,1], pmc_j[:,2]
        px_i, py_i, pz_i = pmc_i[:, 0], pmc_i[:,1], pmc_i[:,2]
        dR = PCC.DeltaR(px_i, px_j, py_i, py_j, pz_i, pz_j)

        m_i, m_ij = PCC.Mass(pmc__i), PCC.Mass(pmc__i + pmc_j)
        mlp_ij = self._MLP(torch.cat([m_i, m_ij, dR, mlp_j - mlp_i], -1))
        
        return pmc_j*(mlp_ij.max(-1)[1]*(src != dst)).view(-1, 1), mlp_ij

    def aggregate(self, message, index, pmc, pmc_, mlp):
        pmc_j, mlp_ij = message
            
        mlp_ij_sum = self.aggr_module_add(mlp_ij, index) + mlp
        mlp_ij_sum /= (degree(index).view(-1, 1))

        pmc_ = pmc_.clone()
        pmc_[index.unique()] += self.aggr_module_add(pmc_j, index)

        px, py, pz = pmc[:, 0], pmc[:,1], pmc[:,2]
        px_, py_, pz_ = pmc_[:, 0], pmc_[:,1], pmc_[:,2]
        dR = PCC.DeltaR(px, px_, py, py_, pz, pz_)
        
        #mlp = self._MLP(torch.cat([PCC.Mass(pmc), PCC.Mass(pmc_), dR, mlp_ij_sum - mlp], -1))
        return mlp_ij, mlp_ij_sum, pmc_

    def forward(self, edge_index, Pmc):
        
        (src, dst), mass = edge_index, PCC.Mass(Pmc)
        zero_ = torch.zeros_like(torch.cat([mass for i in range(3)], -1)) 
        mlp = self._MLP(torch.cat([mass, mass, zero_], -1))
        
        self._edgemap = to_dense_adj(edge_index, edge_attr = zero_[:, 0][src].view(-1))[0]
         
        pmc = Pmc.clone()
        for i in torch.arange(degree(src).max(0)[0]):
            mass = PCC.Mass(pmc[src])
            px, py, pz = pmc[src, 0], pmc[src, 1], pmc[src, 2]
            
            mlp_ij, mlp, pmc_ = self.propagate(edge_index, pmc = Pmc, pmc_ = pmc, mlp = mlp)
            
            mass_ = PCC.Mass(pmc_[src])
            px_, py_, pz_ = pmc_[src, 0], pmc_[src, 1], pmc_[src, 2]
            
            dR = PCC.DeltaR(px, px_, py, py_, pz, pz_)
            edge = mlp_ij.max(-1)[1].view(-1, 1)

            mlp_ij = self._MLP(torch.cat([mass, mass_*edge, dR, mlp_ij - mlp[src] - mlp[dst]], -1))
            pmc = pmc_
          
            update = to_dense_adj(edge_index, edge_attr = edge.view(-1))[0]
            if update.sum(-1).sum(-1) == 0:
                break
            
            self._edgemap += update 
            kill = ((self._edgemap > 1).sum(-1) > 1) 
            kill += (self._edgemap.sum(-1) == 0) 
            kill += (self._edgemap.sum(-1) >= degree(src)-1)
            if kill.sum(-1) > 1:
                break
        return mlp_ij

class PassNet(MessagePassing):
    
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

