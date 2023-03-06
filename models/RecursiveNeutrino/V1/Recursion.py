import torch
from torch_geometric.nn import MessagePassing
from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid, Tanh
import torch.nn.functional as F
import PyC.NuSol.CUDA as NuC
import PyC.Transform.CUDA as TC
import PyC.Physics.CUDA.Cartesian as PCC
from torch_geometric.utils import to_dense_adj, dense_to_sparse

torch.set_printoptions(4, profile = "full", linewidth = 100000)

class Recursion(MessagePassing):

    def __init__(self):
        super().__init__()
    
        self.O_edge = None 
        self.L_edge = "CEL"

        #self.O_res = None 
        #self.L_res = "CEL"

        #self.O_signal = None 
        #self.L_signal = "CEL"
        
        end = 64
        self._isTopMass = Seq(
                        Linear(1, end), 
                        ReLU(), Linear(end, 256), 
                        ReLU(), Linear(256, 64), 
                        ReLU(), Linear(64, 2), Sigmoid()
        )

        self._it = 0

    def _PrefEdge(self, Px_i, Px_j, Py_i, Py_j, Pz_i, Pz_j, E_i, E_j):
        mass = PCC.M(Px_i + Px_j, Py_i + Py_j, Pz_i + Pz_j, E_i + E_j)
        return mass, self._isTopMass(mass)


    def _RecursivePathMass(self, edge_index, Px, Py, Pz, E):
        src, dst = edge_index
        mass, mass_mlp = self._PrefEdge(Px[src], Px[dst], Py[src], Py[dst], Pz[src], Pz[dst], E[src], E[dst])
        
        p_no_edge, p_edge = mass_mlp[:, 0], mass_mlp[:, 1]

        # Do something here.... 


        _, mass_ = mass_mlp.max(-1)
       
        self._adjPx[src, dst] += (Px[dst] * mass_) * self._adjCount[src, dst]
        self._adjPy[src, dst] += (Py[dst] * mass_) * self._adjCount[src, dst]
        self._adjPz[src, dst] += (Pz[dst] * mass_) * self._adjCount[src, dst]
        self._adjE[src, dst]  += ( E[dst] * mass_) * self._adjCount[src, dst]
        self._adjCount[src, dst] -= mass_ * self._adjCount[src, dst]
       
        # Add the self loops on the diagonal in case they were not selected in by the MLP
        tmp = torch.diag(torch.diag(self._adjCount) == 1).to(torch.int)
        self._adjPx += tmp*Px
        self._adjPy += tmp*Py
        self._adjPz += tmp*Pz
        self._adjE += tmp*E
        self._adjCount -= tmp

        self._adjMLP[src, dst] += mass_mlp[:, 1] * (self._adjCount[src, dst] == 0)
        self._adjMLP_[src, dst] += mass_mlp[:, 0] * (self._adjCount[src, dst] == 1)
        
        Px_ = self._adjPx.sum(-1).view(-1, 1)
        Py_ = self._adjPy.sum(-1).view(-1, 1)
        Pz_ = self._adjPz.sum(-1).view(-1, 1)
        E_  =  self._adjE.sum(-1).view(-1, 1)
        Mass = PCC.M(Px_, Py_, Pz_, E_)
       
        self._adjCount = self._adjCount > 0
        edge_index = dense_to_sparse(self._adjCount)[0]
        
        return edge_index, Mass 

    def forward(self, i, edge_index, N_pT, N_eta, N_phi, N_energy, G_met, G_met_phi):
        pt, eta, phi, E = N_pT/1000, N_eta, N_phi, (N_energy/1000).view(-1)
        PxPyPz = TC.PxPyPz(pt, eta, phi)
        Px, Py, Pz = PxPyPz[:, 0], PxPyPz[:, 1], PxPyPz[:, 2]

        self._device = N_pT.device
        self._adjMLP = to_dense_adj(edge_index).zero_()[0]
        self._adjMLP_ = to_dense_adj(edge_index).zero_()[0]

        self._adjCount = to_dense_adj(edge_index)[0]
        self._adjPx = to_dense_adj(edge_index).zero_()[0]
        self._adjPy = to_dense_adj(edge_index).zero_()[0]
        self._adjPz = to_dense_adj(edge_index).zero_()[0]
        self._adjE = to_dense_adj(edge_index).zero_()[0]
        
        edge_index_, Mass = self._RecursivePathMass(edge_index, Px, Py, Pz, E)
        src, dst = edge_index
        
        self.O_edge = torch.cat([self._adjMLP_[src, dst].view(-1, 1), self._adjMLP[src, dst].view(-1, 1)], -1)
