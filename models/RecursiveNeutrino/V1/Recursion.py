import torch
from torch_geometric.nn import MessagePassing
from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid, Tanh, Softmax 
import torch.nn.functional as F
import PyC.NuSol.CUDA as NuC
import PyC.Transform.CUDA as TC
import PyC.Physics.CUDA.Cartesian as PCC
from torch_geometric.utils import to_dense_adj, sort_edge_index, dense_to_sparse, softmax, scatter, degree
from time import sleep
from torch_geometric.nn.resolver import aggregation_resolver as aggr_resolver


torch.set_printoptions(4, profile = "full", linewidth = 100000)
torch.autograd.set_detect_anomaly(True)

class Recursion(MessagePassing):
    def __init__(self):
        super().__init__(aggr = None, flow = "source_to_target")
    
        self.O_edge = None 
        self.L_edge = "CEL"
        self.C_edge = True

        end = 128

        self._MassMLP = Seq(
                Linear(1, end),
                Tanh(), 
                Linear(end, end), 
        )

        self._RecurMLP = Seq(
                Linear(end*3 + 2, end), 
                Tanh(), 
                ReLU(), 
                Tanh(), 
                Linear(end, end), 
                Tanh(), 
                Linear(end, 2)
        )

        self.aggr_module_add = aggr_resolver("add")

    def message(self, edge_index, pmc_i, pmc_j, Pmc_i, Pmc_j):
        src, dst = edge_index
        msk_ = self._msk.clone()
        
        mlp_i = self._MassMLP(PCC.Mass(pmc_i))
        mlp_i_ = self._MassMLP(PCC.Mass(pmc_i + Pmc_j))

        mlp_j = self._MassMLP(PCC.Mass(pmc_j))
        mlp_j_ = self._MassMLP(PCC.Mass(pmc_j + Pmc_i))
        #mlp_j__ = self._RecurMLP(torch.cat([mlp_j_, mlp_j_ - mlp_j, self._i[msk_] - self._i[msk_]], -1))
        mlp_i__ = self._RecurMLP(torch.cat([mlp_i_ - mlp_j_, mlp_i - mlp_j, mlp_i_, self._i[msk_]], -1))

        msk = to_dense_adj(edge_index, edge_attr = (mlp_i__).max(-1)[1])[0]
        msk = to_dense_adj(edge_index)[0] + msk + msk.t()
        msk = (dense_to_sparse(msk)[1]  > 1)
        msk = msk.view(-1, 1)

        #self._i[msk_] += mlp_i__*msk
        #self._i[msk_] += mlp_j__*mlp_j__.max(-1)[1].view(-1, 1)

        #sel = F.softmax(mlp_i__, -1)
        #sel = sel[:, 1]
        #sel += self._T[self._msk].view(-1)*1
        #if sel.sum(-1) > 0:
        #    msk = torch.multinomial(sel, num_samples = 1)
        #    idx = edge_index[:, msk]
        #    msk = to_dense_adj(edge_index)[0]
        #    msk_ = to_dense_adj(idx, max_num_nodes = torch.cat([src, dst], -1).max()+1)[0]
        #    msk += msk_ + msk_.t()
        #
        return (Pmc_j)*msk, msk.view(-1) == 1, src

    def aggregate(self, message, index, Pmc, pmc):
        (pmc_j, msk_, src), dst = message, index
        
        msk = self._msk.clone()
    
        _indx = index.unique()
        eij_ = torch.cat([src.view(1, -1), dst.view(1, -1)], 0)[:, msk_]
        self._Path = torch.cat([self._Path, eij_], -1) 
        pmc[_indx] += self.aggr_module_add(pmc_j, dst)[_indx]

        self._MassMatrix.append(to_dense_adj(self._Path)[0]*PCC.Mass(pmc))
        
        return pmc, msk_

    def forward(self, i, num_nodes, batch, edge_index, N_pT, N_eta, N_phi, N_energy, G_met, G_met_phi, E_T_edge):
        pt, eta, phi, E = N_pT/1000, N_eta, N_phi, N_energy/1000
        Pmc = torch.cat([TC.PxPyPz(pt, eta, phi), E.view(-1, 1)], -1)
        src, dst = edge_index
        zero_ = torch.zeros_like(edge_index).t()
        self._msk = src != dst
        
        self._T = E_T_edge.clone()
        self._Path = edge_index[:, self._msk == False].clone()
        self._MassMatrix = []
        self._MassMatrix = [to_dense_adj(self._Path)[0]*PCC.Mass(Pmc)]
        
        mlp_i = self._MassMLP(PCC.Mass(Pmc[src]))
        mlp_j = self._MassMLP(PCC.Mass(Pmc[dst]))
        
        mlp_i_ = self._MassMLP(PCC.Mass(Pmc[dst] + Pmc[src]*self._msk.view(-1, 1)))
        mlp_j_ = self._MassMLP(PCC.Mass(Pmc[src] + Pmc[dst]*self._msk.view(-1, 1)))
        self._i = self._RecurMLP(torch.cat([mlp_i_ - mlp_j_, mlp_i - mlp_j, mlp_i_, zero_], -1))

        pmc_ = Pmc.clone()
        while True:

            mlp_i = self._MassMLP(PCC.Mass(pmc_)[src])
            mlp_j = self._MassMLP(PCC.Mass(pmc_)[dst])

            msk = self._msk.clone()
            pmc_, msk_ = self.propagate(edge_index[:, msk], pmc = pmc_, Pmc = Pmc)

            mlp_i_ = self._MassMLP(PCC.Mass(pmc_)[src])
            mlp_j_ = self._MassMLP(PCC.Mass(pmc_)[dst])
            self._i = self._RecurMLP(torch.cat([mlp_i_ - mlp_j_, mlp_i - mlp_j, mlp_i_, self._i], -1))

            #mlp_i_ = self._MassMLP(self._MassMatrix[-1][src, dst].view(-1, 1))
            #mlp_j_ = self._MassMLP(self._MassMatrix[-1][dst, src].view(-1, 1))
            #self._i = self._RecurMLP(torch.cat([mlp_i_, mlp_i_ - mlp_j_, self._i], -1))           
            
            self._msk[msk] *= msk_ == False
            if (msk != self._msk).sum(-1) == 0 or self._msk.sum(-1) == 0:
                break
        
        self.O_edge = self._i 

        #print(to_dense_adj(edge_index, edge_attr = self.O_edge.max(-1)[1])[0]) #* self.O_edge.max(-1)[0])[0])









