import torch
from torch.nn import Sequential as Seq, Linear, ReLU, Tanh
from torch_geometric.nn import MessagePassing
from torch_geometric.utils import to_dense_adj, sort_edge_index, dense_to_sparse, softmax, scatter
import PyC.Transform.CUDA as TC
import PyC.Physics.CUDA.Cartesian as PCC

class PathNet(MessagePassing):

    def __init__(self):
        super().__init__(flow = "source_to_target")
        self.O_edge = None 
        self.L_edge = "CEL"
        self.C_edge = True
   
        end = 32
        self._MLP = Seq(
                Linear(1, end), Tanh(), ReLU(), 
                Linear(end, end), Tanh(), ReLU(), 
                Linear(end, 2)
        )

    def Factorial(self, n, k):
        def Fact(n):
            if n == 0:
                return 1
            return n*Fact(n-1)
        return Fact(n)/(Fact(k)*Fact(n-k))

    def forward(self, edge_index, batch, N_pT, N_eta, N_phi, N_energy):
        pt, eta, phi, E = N_pT/1000, N_eta, N_phi, N_energy/1000
        Pmc = torch.cat([TC.PxPyPz(pt, eta, phi), E.view(-1, 1)], -1)
    
        self._Path = []

        self._MLP(PCC.Mass(Pmc))



        exit()
        

