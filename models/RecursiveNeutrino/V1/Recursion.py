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

        end = 64

        self._MassMLP = Seq(
                Linear(1, end*4),
                Linear(end*4, end), 
        )

        self.aggr_module_add = aggr_resolver("add")

    def LinkPrediction(self, pred):
        x0 = dense_to_sparse(pred[0].matmul(pred[0].t()))[1].view(-1, 1)
        x1 = dense_to_sparse(pred[1].matmul(pred[1].t()))[1].view(-1, 1)
        return torch.cat([x0, x1], -1)

    def message(self, edge_index, _pmc_i, _pmc_j, Pmc_i, Pmc_j):
        src, dst = edge_index
        nodes = torch.cat([src, dst], -1).max()+1
       
        pmc_i = PCC.Mass(Pmc_j + _pmc_i)
        pmc_j = PCC.Mass(Pmc_i + _pmc_j)

        #pmc_i = PCC.Mass(_pmc_i + Pmc_j)
        print(to_dense_adj(edge_index, edge_attr = pmc_j.view(-1)))
        print(to_dense_adj(edge_index, edge_attr = pmc_j.view(-1)))

        mlp = self._MassMLP(pmc_j)

        sel = self._T[self._msk] 
        sel += 0.0001
        sel = sel.view(-1)

        msk = torch.multinomial(sel, num_samples = len(src.unique()))
        
        idx = edge_index[:, msk]
        msk = to_dense_adj(edge_index)[0]
        msk_ = to_dense_adj(idx, max_num_nodes = nodes)[0]
        msk += msk_ + msk_.t()

        print(msk)
        msk = (dense_to_sparse(msk)[1]  != 1)*(sel > 0.1)
        msk = msk.view(-1, 1)
       
        return mlp, (_pmc_j + Pmc_j + Pmc_i)*msk, msk.view(-1) == 1, src

    def aggregate(self, message, index, Pmc, _pmc):
        (mlp, pmc_j, msk, src), dst = message, index

         


        eij_ = torch.cat([src.view(1, -1), dst.view(1, -1)], 0)[:, msk]
        self._Path = eij_ if self._Path == None else torch.cat([self._Path, eij_], -1) 

        _indx = index.unique()
        _pmc[_indx] += self.aggr_module_add(pmc_j, dst)
        _pmc += Pmc
        m_ij = PCC.Mass(_pmc)
        
        self._MassMatrix.append(to_dense_adj(self._Path, edge_attr = m_ij.view(-1)[self._Path[0]]))
        print(self._MassMatrix[-1])
        
        print("___")



        mlp_ = self._MassMLP(m_ij)


        #mlp_[_indx] += self.aggr_module_add(mlp, index)[_indx]/degree(index)[_indx].view(-1, 1)
        #mlp += mlp_[edge_index[0]]
        
        return _pmc, msk, mlp

    def forward(self, i, num_nodes, batch, edge_index, N_pT, N_eta, N_phi, N_energy, G_met, G_met_phi, E_T_edge):
        pt, eta, phi, E = N_pT/1000, N_eta, N_phi, N_energy/1000
        Pmc = torch.cat([TC.PxPyPz(pt, eta, phi), E.view(-1, 1)], -1)
        src, dst = edge_index
        
        self._T = E_T_edge.clone()
        self._Path = None
        self.O_edge = None
       
        self._msk = src == src
        self._MassMatrix = []

        pmc_ = torch.zeros_like(Pmc)
        while True:
            pmc_, msk, mlp_ = self.propagate(edge_index[:, self._msk], _pmc = pmc_,  Pmc = Pmc)
            
            msk_ = self._msk.clone()
            self._msk[msk_] *= msk == False

            if self.O_edge == None:
                self.O_edge = mlp_

            if (msk_ != self._msk).sum(-1) == 0 or self._msk.sum(-1) == 0:
                break
            self.O_edge[msk_] += mlp_

            sleep(0.5)
        
        exit()
        x0 = to_dense_adj(edge_index, edge_attr = self.O_edge[:, 0])
        x1 = to_dense_adj(edge_index, edge_attr = self.O_edge[:, 1])
        self.O_edge = torch.cat([x0, x1], 0)
        self.O_edge = self.LinkPrediction(self.O_edge)

        print(self.O_edge)
        print(to_dense_adj(edge_index, edge_attr = self.O_edge.max(-1)[1])[0]) #* self.O_edge.max(-1)[0])[0])




    #def _RecursivePath(self, edge_index, Pmc, Pmc_, msk_):
    #    src, dst = edge_index[:, msk_]
    #    _mlp = self._EdgeAggregation(Pmc[src], Pmc_[dst])
    #    _mlp = self._Reduce(torch.cat([Pmc_[src], _mlp, Pmc[dst]], -1))
    #    sel = _mlp.max(-1)[1]

    #    _prob = to_dense_adj(edge_index[:, msk_], None, softmax(_mlp[:, 1], src)*sel, len(Pmc_))[0]
    #    msk = _prob.sum(-1) > 0
    #    if msk.sum(-1) == 0:
    #        return 

    #    aggr_node = _prob[msk].max(-1)[1]
    #    #aggr_node = torch.multinomial(_prob[msk], num_samples = 1).view(-1)
    #    
    #    Pmc_[msk] += Pmc[aggr_node]
    #    self._Path = torch.cat([ self._Path, torch.cat([ self._Nodes[msk].view(1, -1), aggr_node.view(1, -1) ], 0) ], -1)
    #    self._PathMass = torch.cat([ self._PathMass, PCC.Mass(Pmc_[msk]).view(-1) ], -1)
    #    self._K[msk_] += _mlp*(1/ (self._iter+1))

    #    _ss = to_dense_adj(edge_index, edge_attr = msk_)[0].to(dtype = aggr_node.dtype)
    #    _s = torch.zeros_like(_ss)
    #    _ss[msk] -= _s[msk].scatter_(1, aggr_node.view(-1, 1), torch.ones_like(aggr_node).view(-1, 1))

    #    self._iter += 1 
    #    msk_ = (_ss[edge_index[0], edge_index[1]] == 1)
    #    if msk_.sum(-1) == 0:
    #        return 
    #    return self._RecursivePath(edge_index, Pmc, Pmc_, msk_)

    #def forward(self, i, num_nodes, batch, edge_index, N_pT, N_eta, N_phi, N_energy, G_met, G_met_phi, E_T_edge):
    #    pt, eta, phi, E = N_pT/1000, N_eta, N_phi, N_energy/1000
    #    Pmc = torch.cat([TC.PxPyPz(pt, eta, phi), E.view(-1, 1)], -1)
    #    
    #    src, dst = edge_index
    #    msk, self._iter = src == dst, 0

    #    self._K = 

    #    self._Path = edge_index[:, msk]
    #    self._Nodes = src[msk].view(-1, 1)
    #    self._PathMass = PCC.Mass(Pmc).view(-1)

    #    self._RecursivePath(edge_index, Pmc, Pmc.clone(), src != dst)
    #    
    #    edge_, mass = sort_edge_index(self._Path, edge_attr = self._PathMass)
    #    
    #    mpl = self._Mass(mass.view(-1, 1))
    #    node_mass = to_dense_adj(edge_, None, mpl * mpl.max(-1)[1].view(-1, 1), len(Pmc))[0].view(-1, 2)

    #    self.O_edge = self._K #+ node_mass #+ node_mass[src] * node_mass[dst]
    #    print(to_dense_adj(edge_index, edge_attr = self.O_edge.max(-1)[1])[0])















class OldRecursion(MessagePassing):
    def __init__(self):
        super().__init__()
    
        self.O_edge = None 
        self.L_edge = "CEL"
        self.C_edge = True

        end = 32
        self._Mass = Seq(
                Linear(1, end, bias = False),
                Tanh(), ReLU(), 
                Linear(end, 2)
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
        Node = Pmc_[dst]*(src != dst) if self._it != 0 else Pmc_*0
        mass_mlp = self._EdgeAggregation(Pmc[src], Node.view(-1, 1))
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
        self._PathMass[msk, self._it] = PCC.Mass(Pmc_)
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
        self._PathMass = to_dense_adj(edge_index)[0].fill_(-1).to(dtype = edge_index[0].dtype)

        self._RecursivePath(edge_index, Pmc, Pmc.clone())
        
        edge_, attr = dense_to_sparse(self._Path * to_dense_adj(edge_index)[0])
        attr = attr.to(dtype = edge_index[0].dtype)
        msk = attr > 0
        mass = self._Mass(PCC.Mass(Pmc[edge_[0]][msk] + Pmc[attr[msk]]))
        _edge, mlp = sort_edge_index(torch.cat([edge_[0][msk].view(1, -1), attr[msk].view(1, -1)], 0), edge_attr = mass)
         
        self.O_edge = F.softmax(self._G, -1)*self._G
        print(to_dense_adj(edge_index, edge_attr = self.O_edge.max(-1)[1])[0])
        #print(to_dense_adj(edge_index, edge_attr = E_T_edge.view(-1))[0])
        #print("---")
        # Add path to sort.
