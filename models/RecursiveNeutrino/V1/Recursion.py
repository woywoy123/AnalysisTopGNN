import torch
from torch_geometric.nn import MessagePassing
from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid, Tanh, Softmax 
import torch.nn.functional as F
import PyC.NuSol.CUDA as NuC
import PyC.Transform.CUDA as TC
import PyC.Physics.CUDA.Cartesian as PCC
from torch_geometric.utils import to_dense_adj, sort_edge_index, dense_to_sparse, softmax

torch.set_printoptions(4, profile = "full", linewidth = 100000)
torch.autograd.set_detect_anomaly(True)


class Recursion(MessagePassing):
    def __init__(self):
        super().__init__()
    
        self.O_edge = None 
        self.L_edge = "CEL"
        self.C_edge = True

        end = 32
        self._Mass = Seq(
                Linear(1, end, bias = False),
                Linear(end, 2, bias = False)
        )
        self._Reduce = Seq(
                Linear(4 + 4 + 4, end, bias = False),
                Tanh(), ReLU(), 
                Linear(end, 2), 
        )

    def _EdgeAggregation(self, Pmc, Pmc_):
        M_i, M_j = PCC.Mass(Pmc), PCC.Mass(Pmc_)
        Pmc_ = Pmc_ + Pmc_
        M_ij = PCC.Mass(Pmc_)
        _mpl = self._Mass(M_ij)
        return _mpl

    def _RecursivePath(self, edge_index, Pmc, Pmc_):
        src, dst = edge_index
        mass_mlp = self._EdgeAggregation(Pmc[src], Pmc_[dst]*(src != dst).view(-1, 1))
        mmlp0, mmlp1, sel = mass_mlp[:, 0], mass_mlp[:, 1], mass_mlp.max(-1)[1].view(-1, 1)
        
        _edges = self._remaining_edges == 1
        self._G[_edges] += self._Reduce(torch.cat([self._G[_edges], Pmc_[src], Pmc[dst], mass_mlp], -1)) + mass_mlp
        if len(self._G[:, 1][_edges]) == 0:
            return 
        
        _prob = to_dense_adj(edge_index, edge_attr = softmax(self._G[:, 1][_edges], src)*sel.view(-1), max_num_nodes = len(Pmc))[0]
        msk = (_prob.sum(-1) > 0).view(-1)
        if msk.sum(-1) == 0:
            return 
    
        aggr_node = torch.multinomial(_prob[msk], num_samples = 1)
        self._Path[msk, self._it] = aggr_node.view(-1)
        self._it += 1

        # Update adjacency matrix
        _s = torch.zeros_like(_prob).to(dtype = aggr_node.dtype)
        _s[msk] = _s[msk].scatter_(1, aggr_node, torch.ones_like(aggr_node))
        _s = _s + to_dense_adj(self._edge_index, edge_attr = self._remaining_edges)[0]
        self._remaining_edges = dense_to_sparse(_s)[1]
        edge_index = self._edge_index[:, self._remaining_edges == 1]
        
        Pmc_[msk] += Pmc[aggr_node.view(-1)]
        return self._RecursivePath(edge_index, Pmc, Pmc_)
    
    def forward(self, i, num_nodes, batch, edge_index, N_pT, N_eta, N_phi, N_energy, G_met, G_met_phi, E_T_edge):
        pt, eta, phi, E = N_pT/1000, N_eta, N_phi, N_energy/1000
        Pmc = torch.cat([TC.PxPyPz(pt, eta, phi), E.view(-1, 1)], -1)
        
        self._it = 0
        self._edge_index = edge_index
        self._remaining_edges = torch.ones_like(edge_index[0]) 
        self.E_T_edge = E_T_edge.view(-1, 1)
            
        src, dst = edge_index
        self._G = self._EdgeAggregation(Pmc[src], Pmc[dst]*(src != dst).view(-1, 1))
        self._Path = to_dense_adj(edge_index)[0].fill_(-1).to(dtype = edge_index[0].dtype)

        self._RecursivePath(edge_index, Pmc, Pmc.clone())
        
        edge_, attr = dense_to_sparse(self._Path * to_dense_adj(edge_index)[0])
        attr = attr.to(dtype = edge_index[0].dtype)
        msk = attr > 0
        mass = self._Mass(PCC.Mass(Pmc[edge_[0]][msk] + Pmc[attr[msk]]))
        print(sort_edge_index(torch.cat([edge_[0][msk].view(1, -1), attr[msk].view(1, -1)], 0), edge_attr = mass))
         

        self.O_edge = F.softmax(self._G, -1)*self._G
        print(to_dense_adj(edge_index, edge_attr = self.O_edge.max(-1)[1])[0])
        #print(to_dense_adj(edge_index, edge_attr = E_T_edge.view(-1))[0])
        #print("---")
        # Add path to sort.
