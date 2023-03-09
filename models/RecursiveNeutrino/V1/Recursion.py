import torch
from torch_geometric.nn import MessagePassing
from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid, Tanh
import torch.nn.functional as F
import PyC.NuSol.CUDA as NuC
import PyC.Transform.CUDA as TC
import PyC.Physics.CUDA.Cartesian as PCC
from torch_geometric.utils import to_dense_adj, dense_to_sparse, softmax

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
        self._Mass = Seq(
                        Linear(2, end), 
                        ReLU(), Linear(end, 256), 
                        ReLU(), Linear(256, 64), 
                        ReLU(), Linear(64, 2), Sigmoid()
        )

    def _ProbabilityMap(self, edge_index, probability):
        edge, prob = dense_to_sparse(to_dense_adj(edge_index, edge_attr = probability)[0]*self._sigP[self._iter])
        _msk = prob > 0
        prob = softmax(prob[_msk], edge[:, _msk][0])
        return to_dense_adj(edge, edge_attr = prob, max_num_nodes = self._N.sum(-1))[0]

    def _Bayesian(self, next_node, prob_map):
        # ------ Bayesian Part ------ #
        # P( +(-) | e_i ) = gamma[:, 1][i]
        #p_e_i = 
        return torch.gather(prob_map, 1, next_node)

        # P(e_i) = 1/((nodes-1) - iteration) 
        e_i = 1/(n_ - self._iter)

        # P( +(-) | e/_i ) = 1 - \sum_{j != i} P( + | e_j )
        p_ne_i = torch.sum(prob_map, dim = -1, keepdim = True) - e_i
        
        # P( e/_i ) = 1 - P(e_i)
        ne_i = (1 - e_i)

        # P(e_i | +(-)) = ( P(+(-) | e_i) x P(e_i) )/( P(+(-) | e_i) x P(e_i) + P(+(-) | ne_i) x P(ne_i) )
        return (p_e_i * e_i) / ( p_e_i * e_i + p_ne_i * ne_i )

    def _SelectEdges(self, edge_index, Px_i, Py_i, Pz_i, E_i, Px_j, Py_j, Pz_j, E_j):
        Px_ij, Py_ij, Pz_ij, E_ij = Px_i + Px_j, Py_i + Py_j, Pz_i + Pz_j, E_i + E_j,
        M_i , M_j ,  M_ij = PCC.M(Px_i, Py_i, Pz_i, E_i), PCC.M(Px_j, Py_j, Pz_j, E_j), PCC.M(Px_ij, Py_ij, Pz_ij, E_ij)
        gamma = self._Mass(torch.cat([M_ij, abs(M_i - M_j)], -1))
        gamma = F.softmax(gamma, dim = -1)
        p0, p1 = gamma[:, 0], gamma[:, 1]
        
        prob_map_ = self._ProbabilityMap(edge_index, p0)
        prob_map = self._ProbabilityMap(edge_index, p1)
        msk = prob_map.sum(-1) > 0
        next_node = torch.unique(edge_index[0]).view(-1, 1).fill_(-1)
        n_ = next_node.size()[0]
        next_node[msk] = torch.multinomial(prob_map[msk], num_samples = 1)
        
        self._iter += 1
        n_sigP = self._sigP[self._iter - 1].clone()


        print(next_node[msk])

        n_sigP.scatter_(1, next_node[msk], torch.zeros_like(next_node[msk]).to(dtype = n_sigP.dtype))
        print(n_sigP.sum(-1, keepdim = True))


        self._sigP = torch.cat([self._sigP, n_sigP.view(1, n_, n_)], 0)
        
        self._PSel_[msk, self._iter] = self._Bayesian(next_node[msk], prob_map_[msk]).view(-1)
        self._PSel[msk, self._iter] = self._Bayesian(next_node[msk], prob_map[msk]).view(-1)
        self._PMap[:, self._iter] = next_node.view(-1)
        self._PathMass[msk, self._iter] = torch.gather(to_dense_adj(edge_index, edge_attr = M_ij.view(-1))[0][msk], 1, next_node[msk]).view(-1)

        Pmc = torch.zeros_like(next_node).to(dtype = Px_i.dtype)
        Pmc = torch.cat([Pmc, Pmc, Pmc, Pmc], -1)
        Pmc[msk, 0] = torch.gather(to_dense_adj(edge_index, edge_attr = Px_ij)[0][msk], 1, next_node[msk]).view(-1)
        Pmc[msk, 1] = torch.gather(to_dense_adj(edge_index, edge_attr = Py_ij)[0][msk], 1, next_node[msk]).view(-1)
        Pmc[msk, 2] = torch.gather(to_dense_adj(edge_index, edge_attr = Pz_ij)[0][msk], 1, next_node[msk]).view(-1)
        Pmc[msk, 3] = torch.gather(to_dense_adj(edge_index, edge_attr = E_ij)[0][msk], 1, next_node[msk]).view(-1)
        return Pmc[:, 0], Pmc[:, 1], Pmc[:, 2], Pmc[:, 3]
         
    def _RecursivePathMass(self, edge_index, Px, Py, Pz, E, Px_, Py_, Pz_, E_):
        
        src, dst = edge_index
        Px_j, Py_j, Pz_j, E_j = Px[dst], Py[dst], Pz[dst], E[dst]
        Px_i, Py_i, Pz_i, E_i = Px_[src], Py_[src], Pz_[src], E_[src]
        Px_, Py_, Pz_, E_ = self._SelectEdges(edge_index, Px_i, Py_i, Pz_i, E_i, Px_j, Py_j, Pz_j, E_j)
       
        print(self._sigP[self._iter])
        if self._sigP[self._iter].sum(-1).sum(-1) == 0:
            self._iter = 0
            return True
        return self._RecursivePathMass(edge_index, Px, Py, Pz, E, Px_, Py_, Pz_, E_) 

    def forward(self, i, batch, edge_index, N_pT, N_eta, N_phi, N_energy, G_met, G_met_phi):
        pt, eta, phi, E = N_pT/1000, N_eta, N_phi, (N_energy/1000)
        PxPyPz = TC.PxPyPz(pt, eta, phi)
        Px, Py, Pz, E = PxPyPz[:, 0], PxPyPz[:, 1], PxPyPz[:, 2], E.view(-1)

        self._device = N_pT.device
        self._iter = 0
       
        _, self._N = batch.unique(return_counts = True)
        self._Batch = batch
        
        # Tracks the overall paths traversed 
        self._PMap = to_dense_adj(edge_index)[0].zero_().to(dtype = edge_index[0].dtype)
        self._PMap[:, self._iter] = torch.unique(edge_index[0])

        # Tracks which nodes have already been used for path derivation 
        self._sigP = (torch.ones_like(self._PMap).fill_diagonal_(0)*to_dense_adj(edge_index)[0]).view(1, N_pT.size()[0], N_pT.size()[0])

        # Tracks the path mass 
        OwnMass = PCC.M(Px, Py, Pz, E)
        self._PathMass = torch.zeros_like(self._PMap).to(dtype = N_phi.dtype) 
        self._PathMass[:, self._iter] = OwnMass.view(-1)

        # Tracks the probability of (not)selecting an edge at each iteration
        self._PSel_ = torch.zeros_like(self._PMap).to(dtype = N_phi.dtype) 
        self._PSel = torch.zeros_like(self._PMap).to(dtype = N_phi.dtype)
        
        _P = self._Mass(torch.cat([OwnMass, abs(OwnMass - OwnMass)], -1))
        self._PSel_[:, self._iter] = _P[:, 0]
        self._PSel[:, self._iter] = _P[:, 1]
        
        self._RecursivePathMass(edge_index, Px, Py, Pz, E, Px, Py, Pz, E)
        
        # Correctly map the output
        print(self._PMap)
        remapped = dense_to_sparse(self._PMap.to(dtype = edge_index[0].dtype)+1)[1]-1
        indx, rev_map = remapped.view(-1, N_phi.size()[0]).sort(-1)
        

        print(self._PSel)
        p0 = torch.gather(self._PSel_.view(-1, N_phi.size()[0]), 1, rev_map)
        p1 = torch.gather(self._PSel.view(-1, N_phi.size()[0]), 1, rev_map)
        self.O_edge = torch.cat([p0.view(-1, 1), p1.view(-1, 1)], -1) 
        #self.O_edge = self.O_edge[to_dense_adj(edge_index).view(-1) == 1]


        exit()
        return self.O_edge
