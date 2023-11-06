from AnalysisG.Events import Event
from AnalysisG import Analysis
import os

smpls = os.environ["Samples"] + "ttZ-1000/DAOD_TOPQ1.21955751._000019.root"
ana = Analysis()
ana.InputSample(None, smpls)
ana.Event = Event
ana.Launch()
x = []
for i in ana: x += i.Electrons
assert len(x)
