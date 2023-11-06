from AnalysisG import Analysis
from ObjectDefinitions.SimpleDataGraph import SimpleGraph
from ObjectDefinitions.Event import ExampleEvent
from ObjectDefinitions.Features import * # <- Optional, you can define the functions in this script as well.



# In this tutorial we will go through how to generate PyTorch Geometric graph objects
example_sample = "../test/samples/sample1/"

# // ========= Using the Graph Compiler =========== //
# Sample 1: see test/samples/sample1/smpl1.root 
Ana = Analysis()
Ana.ProjectName = "ExampleGraphs"
Ana.InputSample("sample1", example_sample)
Ana.Event = ExampleEvent # < link the event definition to the framework
Ana.Graph = SimpleGraph # < link the graph implementation tom the framework
Ana.EventCache = False # < Don't create a cache
Ana.DataCache = True # <Optional, but saves the graphs and allows for much faster loading
Ana.Threads = 1 # < how many CPU threads to utilize 
Ana.EventStop = 100 # < how many events to generate 

# Add Truth to the Graph 
Ana.AddGraphTruthFeature(signal) # <- If no name has been specified, the function name will be used

# Add Observable Attributes to Graph, i.e. things we train the GNN on.
# Graph Feature
Ana.AddGraphFeature(nJets, "njets")

# Node features
Ana.AddNodeFeature(pt)
Ana.AddNodeFeature(eta)
Ana.AddNodeFeature(phi)
Ana.AddNodeFeature(energy, "e")
Ana.AddNodeFeature(Mass, "mass")

# Edge features
Ana.AddEdgeFeature(delta_pt, "dpt")
Ana.AddEdgeFeature(delta_eta, "deta")
Ana.AddEdgeFeature(delta_phi, "dphi")
Ana.AddEdgeFeature(delta_energy, "de")
Ana.AddEdgeFeature(EdgeMass, "mass")
Ana.AddEdgeFeature(deltaR, "dR")
Ana.Launch() # < compile the graphs

for gr in Ana:
    print(gr.E_dpt) # < notice E implying edge
    print(gr.G_T_signal) # < notice G (graph) T (truth) signal (attribute)

    print(gr.num_nodes) # < attributes from PyTorch Geometric's API !!!
    print(gr.is_directed()) # < function from PyTorch Geometric!
    print(gr.to(device = "cpu")) # < clone the object entirely into GPU/CPU

# This implies, we have still benefit from PyTorch Geometric's API calls, without having to re-read them 
# into yet another framework.
