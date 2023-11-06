from AnalysisG.Events import SSML
from AnalysisG import Analysis
import os


smpls = os.environ["Samples"] + "../../user.bdong.34335888._000191.output.root"
ana = Analysis()
ana.InputSample(None, smpls)
ana.Event = SSML
ana.Launch()
x = []
for i in ana: x += i.Detector; break
assert len(x)
