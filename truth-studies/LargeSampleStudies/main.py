from ObjectDefinitions.Event import Event 
from AnalysisTopGNN import Analysis 

Ana = Analysis()
Ana.InputSample("test", "./TestSample/output.root")
Ana.Event = Event 
Ana.Threads = 1
Ana.EventStop = 2
Ana.Launch()
