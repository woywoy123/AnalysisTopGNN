import torch 
from torch_geometric.nn import MessagePassing
from torch.nn import Sequential as Seq, Linear, ReLU, Sigmoid

class ExampleGNN(MessagePassing):

    def __init__(self):
        super().__init__()

        # Declare outputs of GNN: O_<truth attribute> 
        self.O_ResPairs = None

        # Declare loss function: L_<truth attribute>
        self.L_ResPairs = "CEL" # Cross Entropy Loss 

        # Declare whether classification if needed: C_<truth attribute>
        self.C_ResPairs = False # If the output is float, it will be rounded to nearest integer

        # Example MLP 
        end = 10
        self._isPair = Seq(Linear(1, end), 
                           ReLU(), Linear(end, 256), 
                           Sigmoid(), Linear(256, 128), 
                           ReLU(), Linear(128, 2))

    # forward will have inputs 
    # - Node: N_<features>
    # - Edge: E_<features>
    # - Graph: G_<features>
    def forward(self, edge_index, i, N_pt, N_eta, N_phi, N_e, E_mass, G_nJets):   
        self.O_ResPairs = self._isPair(E_mass) 
        return self.O_ResPairs
