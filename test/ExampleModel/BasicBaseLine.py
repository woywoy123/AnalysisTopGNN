import torch 
from torch_geometric.nn import MessagePassing
from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid, Tanh
import torch.nn.functional as F
import PyC.Transform.Tensors as Tt
import PyC.Physics.Tensors.Polar as PtP
import PyC.Physics.Tensors.Cartesian as PtC
from torch_geometric.utils import to_dense_adj, add_remaining_self_loops, dense_to_sparse

torch.set_printoptions(4, profile = "full", linewidth = 100000)

class BasicBaseLineRecursion(MessagePassing):

    def __init__(self):
        super().__init__(aggr = None, flow = "target_to_source")
        self.O_edge = None
        self.L_edge = "CEL"
        self.C_edge = True

        end = 64
        self._isEdge = Seq(Linear(end*4, end), ReLU(), Linear(end, 256), Sigmoid(), Linear(256, 128), ReLU(), Linear(128, 2))
        self._isMass = Seq(Linear(1, end), Linear(end, end))
        self._it = 0

    def forward(self, i, edge_index, N_pT, N_eta, N_phi, N_energy, N_mass, E_T_edge):
        if self._it == 0:
            self.device = N_pT.device
            self.edge_mlp = torch.zeros((edge_index.shape[1], 2), device = self.device)
            self.node_count = torch.ones((N_pT.shape[0], 1), device = self.device)
            self.index_map = to_dense_adj(edge_index)[0] 
            self.index_map[self.index_map != 0] = torch.arange(self.index_map.sum(), device = self.device)
            self.index_map = self.index_map.to(dtype = torch.long)
        Pmu = torch.cat([N_pT, N_eta, N_phi, N_energy], dim = 1)
        Pmc = torch.cat([Tt.PxPyPz(N_pT, N_eta, N_phi), N_energy], dim = -1)
        edge_index_new, Pmu, N_mass = self.propagate(edge_index, Pmc = Pmc, Pmu = Pmu, Mass = N_mass, E_T_edge = E_T_edge)
        if torch.sum(self.index_map[edge_index_new]) != torch.sum(self.index_map[edge_index]):
            self._it += 1 
            return self.forward(i, edge_index_new, Pmu[:, 0:1], Pmu[:, 1:2], Pmu[:, 2:3], Pmu[:, 3:4], N_mass, E_T_edge = E_T_edge)
        self._it = 0
        self.O_edge = self.edge_mlp
        return self.O_edge

    def message(self, edge_index, Pmc_i, Pmc_j, Pmu_i, Pmu_j, Mass_i, Mass_j, E_T_edge):
        e_dr = PtP.DeltaR(Pmu_i[:, 1], Pmu_j[:, 1], Pmu_i[:, 2], Pmu_j[:, 2])
        e_mass = PtC.Mass(Pmc_i + Pmc_j)

        e_mass_mlp = self._isMass(e_mass/1000)
        ni_mass = self._isMass(Mass_i/1000)
        nj_mass = self._isMass(Mass_j/1000)

        mlp = self._isEdge(torch.cat([e_mass_mlp, torch.abs(ni_mass-nj_mass), torch.abs(e_mass_mlp - ni_mass - nj_mass), e_mass_mlp + ni_mass + nj_mass], dim = 1))
        return edge_index[1], mlp, Pmc_j

    def aggregate(self, message, index, Pmc, Pmu, Mass):
        edge_index, mlp_mass, Pmc_j = message
        edge = mlp_mass.max(dim = 1)[1]
        
        max_c = (edge == 1).nonzero().view(-1)
        idx = self.index_map[index[max_c], edge_index[max_c]]
        idx_all = self.index_map[index, edge_index]

        max_c = max_c[index[max_c] != edge_index[max_c]]

        idx_i, idx_j = index[max_c], edge_index[max_c] # Get the index of the current node and the incoming node
        Pmc_idx_j = Pmc[idx_j] # Get the four vectors of non zero edges for incoming edge
        node_c_j = self.node_count[idx_j].view(-1, 1) # Node j count

        Pmc_i = Pmc.clone() # Collect the node's own four vector
        Pmc_i.index_add_(0, idx_i, Pmc_idx_j*node_c_j)
        
        self.node_count[index[max_c]] = 0
        self.node_count[edge_index[max_c]] = 0
        
        self.edge_mlp[idx_all] += mlp_mass
        edge_index = torch.cat([index[edge == 0].view(1, -1), edge_index[edge == 0].view(1, -1)], dim = 0)
        edge_index = add_remaining_self_loops(edge_index, num_nodes = Pmu.shape[0])[0]

        return edge_index, torch.cat([Tt.PtEtaPhi(Pmc_i), Pmc_i[:3]], dim = -1), PtC.Mass(Pmc_i)
