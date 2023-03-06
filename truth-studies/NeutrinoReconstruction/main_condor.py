from mtt_reconstruction import *
from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Events import Event
import os
import time
from AnalysisTopGNN.Tools import Threading
from tqdm import tqdm
import sys

sample_path = sys.argv[1]
print(sample_path)

Ana = Analysis()
Ana.InputSample("bsm1000", sample_path)
Ana.Event = Event
#Ana.EventStop = 100
Ana.ProjectName = "Dilepton" + (f"_EventStop{Ana.EventStop}" if Ana.EventStop else "") 
Ana.EventCache = True
Ana.DumpPickle = True 
Ana.Launch()

DileptonAnalysis_withNeutrinoReco(Ana)


