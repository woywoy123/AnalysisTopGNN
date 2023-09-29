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
    import pyc
    import pyc.Physics.Cartesian as TC
    import pyc.Physics.Polar as TP
    import pyc.Operators as TO
    import pyc.NuSol as NuT


def test_import_events():
    from AnalysisG.Events import Event
    from AnalysisG.Events import GraphTops
    from AnalysisG.Events import GraphChildren
    from AnalysisG.Events import GraphTruthJet
    from AnalysisG.Events import GraphJet

if __name__ == "__main__":
    test_import_anaG()
    test_import_events()
    test_import_generator()
    test_import_io()
    test_import_model()
    test_import_pyc()
    test_import_templates()
    test_import_tools()
