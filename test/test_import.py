def test_analysisgnn():
    import AnalysisTopGNN

def test_event_template():
    from AnalysisTopGNN.Templates import Event

def test_eventgraph_template():
    from AnalysisTopGNN.Templates import EventGraph

def test_particle_template():
    from AnalysisTopGNN.Templates import ParticleTemplate
 
def test_selection_template():
    from AnalysisTopGNN.Templates import Selection

def test_hdf5():
    from AnalysisTopGNN.IO import HDF5
 
def test_uproot():
    from AnalysisTopGNN.IO import File
 
def test_uproot():
    from AnalysisTopGNN.IO import Pickle
 
def test_model():
    from AnalysisTopGNN.Model import Model

def test_optimizer():
    from AnalysisTopGNN.Model import Optimizer

def test_scheduler():
    from AnalysisTopGNN.Model import Scheduler
 
def test_histograms():
    from AnalysisTopGNN.Plotting import TH1F, TH2F, CombineTH1F, TH1FStack 

def test_lines():
    from AnalysisTopGNN.Plotting import TLine, CombineTLine, TLineStack
 
def test_condor():
    from AnalysisTopGNN.Submission import Condor

def test_tools():
    from AnalysisTopGNN.Tools import Threading, RandomSamplers, Tools, Tables

def test_generators():
    from AnalysisTopGNN.Generators import EventGenerator, GraphGenerator

def test_vector():
    from AnalysisTopGNN.Vectors import Px, Py, Pz, PT, Phi, Eta, PxPyPzEMass, deltaR, energy, IsIn

def test_torch_extensions_transform_cpu():
    from PyC.Transform.Floats import Px, Py, Pz, PxPyPz, PT, Phi, Eta, PtEtaPhi
    from PyC.Transform.Tensors import Px, Py, Pz, PxPyPz, PT, Phi, Eta, PtEtaPhi

def test_torch_extensions_operators_cpu():
    from PyC.Operators.Tensors import Dot, CosTheta, SinTheta, Rx, Ry, Rz

def test_torch_extensions_physics_cpu():
    from PyC.Physics.Tensors.Cartesian import P2, P, Beta2, Beta, M2, M, Mass, Mt2, Mt, Theta, DeltaR
    from PyC.Physics.Tensors.Polar import P2, P, Beta2, Beta, M2, M, Mass, Mt2, Mt, Theta, DeltaR

def test_torch_extensions_nusol_cpu():
    from PyC.NuSol.Tensors import NuPtEtaPhiE, NuPxPyPzE
    from PyC.NuSol.Tensors import NuDoublePtEtaPhiE, NuDoublePxPyPzE
    from PyC.NuSol.Tensors import NuListPtEtaPhiE, NuListPxPyPzE
    from PyC.NuSol.Tensors import NuNuPtEtaPhiE, NuNuPxPyPzE
    from PyC.NuSol.Tensors import NuNuDoublePtEtaPhiE, NuNuDoublePxPyPzE
    from PyC.NuSol.Tensors import NuNuListPtEtaPhiE, NuNuListPxPyPzE
