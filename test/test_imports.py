def test_import_anaG():
    import AnalysisG


def test_import_templates():
    from AnalysisG.Templates import ApplyFeatures
    from AnalysisG.Templates import FeatureAnalysis
    from AnalysisG.Templates import ParticleTemplate
    from AnalysisG.Templates import EventTemplate
    from AnalysisG.Tracer import SampleTracer


def test_import_model():
    from AnalysisG.Model import ModelWrapper


def test_import_generator():
    from AnalysisG.Generators import Optimizer
    from AnalysisG.Generators import GraphGenerator
    from AnalysisG.Generators import SelectionGenerator
    from AnalysisG.Generators import Analysis
    from AnalysisG.Generators import RandomSamplers
    from AnalysisG import Analysis
    from AnalysisG.Submission import Condor


def test_import_io():
    from AnalysisG.IO import UpROOT
    from AnalysisG.IO import PickleObject
    from AnalysisG.IO import UnpickleObject


def test_import_tools():
    from AnalysisG.Tools import Threading
    from AnalysisG.Tools import Hash
    from AnalysisG.Tools import Tools
    from AnalysisG.Tools import Code


def test_import_pyc():
    import PyC
    import PyC.Physics.Tensors.Cartesian as TC
    import PyC.Physics.Tensors.Polar as TP
    import PyC.Operators.Tensors as TO
    import PyC.NuSol.Tensors as NuT


def test_import_events():
    from AnalysisG.Events import Event
    from AnalysisG.Events import GraphTops
    from AnalysisG.Events import GraphChildren
    from AnalysisG.Events import GraphTruthJet
    from AnalysisG.Events import GraphJet
