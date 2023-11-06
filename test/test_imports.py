def test_import_anaG():
    import AnalysisG

def test_cimports():
    from AnalysisG._cmodules.SelectionTemplate import SelectionTemplate
    from AnalysisG._cmodules.ParticleTemplate import ParticleTemplate
    from AnalysisG._cmodules.EventTemplate import EventTemplate
    from AnalysisG._cmodules.GraphTemplate import GraphTemplate
    from AnalysisG._cmodules.cWrapping import OptimizerWrapper
    from AnalysisG._cmodules.SampleTracer import SampleTracer
    from AnalysisG._cmodules.cPlots import TH1F, TH2F, TLine
    from AnalysisG._cmodules.cWrapping import ModelWrapper
    from AnalysisG._cmodules.cOptimizer import cOptimizer
    from AnalysisG._cmodules.cPlots import BasePlotting
    from AnalysisG._cmodules.MetaData import MetaData
    from AnalysisG._cmodules.SampleTracer import Event
    from AnalysisG._cmodules.code import Code

def test_import_events():
    from AnalysisG.Events import Event
    from AnalysisG.Events import GraphTops
    from AnalysisG.Events import GraphChildren
    from AnalysisG.Events import GraphTruthJet
    from AnalysisG.Events import GraphJet

def test_import_templates():
    from AnalysisG.Templates import ParticleTemplate
    from AnalysisG.Templates import GraphTemplate
    from AnalysisG.Templates import SelectionTemplate
    from AnalysisG.Templates import EventTemplate
    from AnalysisG.Templates import ApplyFeatures
    from AnalysisG.Templates import FeatureAnalysis

def test_import_generator():
    from AnalysisG.Generators import Optimizer
    from AnalysisG.Generators import GraphGenerator
    from AnalysisG.Generators import SelectionGenerator
    from AnalysisG.Generators import Analysis
    from AnalysisG.Generators import RandomSamplers
    from AnalysisG.SampleTracer import MetaData
    from AnalysisG.SampleTracer import SampleTracer

def test_import_io():
    from AnalysisG.IO import UpROOT
    from AnalysisG.IO import PickleObject
    from AnalysisG.IO import UnpickleObject


def test_import_model():
    from AnalysisG.Model import Model

def test_import_pyc():
    import pyc
    import pyc.Physics.Cartesian as TC
    import pyc.Physics.Polar as TP
    import pyc.Operators as TO
    import pyc.NuSol as NuT

def test_import_tools():
    from AnalysisG.Tools import Threading
    from AnalysisG.Tools import Tools
    from AnalysisG.Tools import Code


if __name__ == "__main__":
    test_import_anaG()
    test_cimports()
    test_import_events()
    test_import_templates()
    test_import_generator()
    test_import_io()
    test_import_model()
    test_import_pyc()
    test_import_tools()
