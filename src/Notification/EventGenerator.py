from .Notification import Notification

class EventGenerator(Notification):

    def __init__(self):
        pass
    
    def CheckEventImplementation(self):
        if self.Event == None:
            ex = "Or do: from AnalysisTopGNN.Events import Event"
            self.Failure("="*len(ex))
            self.Failure("No Event Implementation Provided.")
            self.Failure("var = " + self.Caller.capitalize() + "()")
            self.Failure("var.Event")
            self.Failure("See src/EventTemplates/Event.py or 'tutorial'")
            self.FailureExit(ex)
      
    def CheckROOTFiles(self):
        if len(self.MergeListsInDict(self.Files)) == 0:
            mes = "No .root files found."
            self.Failure("="*len(mes))
            self.FailureExit(mes)

    def CheckSettings(self):
        if self.EventStop == None:
            return 
        if self.EventStop < self.EventStart:
            self.Warning("EventStart is larger than EventStop. Switching.")
            tmp = self.EventStop
            tmp2 = self.EventStart
            self.EventStop = tmp2
            self.EventStart = tmp
    
    def CheckSpawnedEvents(self):
        if len(self.SampleContainer) == 0:
            self.Warning("No Events were generated...")

    def CheckVariableNames(self, Obj):
        if len(Obj.Trees) == 0:
            ex = "The Event implementation has an empy self.Trees variable!"
            self.Failure("="*len(ex))
            self.FailureExit(ex)

    def FoundFiles(self, Files, i = None):
        if self.Caller == "ANALYSIS":
            return 
        for i in Files:
            self.Success("!!Files Found in Directory: " + i + "\n -> " + "\n -> ".join(Files[i]))
