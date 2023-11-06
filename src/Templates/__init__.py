try: from AnalysisG._cmodules.EventTemplate import EventTemplate
except ModuleNotFoundError: print("ERROR: Missing EventTemplate Compiler...")

try: from AnalysisG._cmodules.ParticleTemplate import ParticleTemplate
except ModuleNotFoundError: print("ERROR: Missing ParticleTemplate Compiler...")

try: from AnalysisG._cmodules.GraphTemplate import GraphTemplate
except ModuleNotFoundError: print("ERROR: Missing GraphTemplate Compiler...")

try: from AnalysisG._cmodules.SelectionTemplate import SelectionTemplate
except ModuleNotFoundError: print("ERROR: Missing SelectionTemplate Compiler...")

from .Features.FeatureAnalysis import FeatureAnalysis
from .Features.FeatureTemplate import ApplyFeatures
