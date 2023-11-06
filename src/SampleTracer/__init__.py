try: from AnalysisG._cmodules.MetaData import MetaData
except ModuleNotFoundError: print("ERROR: Missing MetaData Compiler...")

try: from AnalysisG._cmodules.SampleTracer import SampleTracer
except ModuleNotFoundError: print("ERROR: Missing SampleTracer Compiler...")
