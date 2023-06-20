from .Notification import Notification


class _EventGenerator(Notification):
    def __init__(self):
        pass

    @property
    def CheckEventImplementation(self):
        if self.Event != None:
            return True
        ex = "Or do: from AnalysisTopGNN.Events import Event"
        self.Failure("=" * len(ex))
        self.Failure("No Event Implementation Provided.")
        self.Failure("var = " + self.Caller.capitalize() + "()")
        self.Failure("var.Event")
        self.Failure("See src/Events/Event.py or 'tutorial'")
        self.Failure("=" * len(ex))
        return False

    @property
    def CheckROOTFiles(self):
        if len(self.MergeListsInDict(self.Files)) != 0:
            return True
        mes = "No .root files found."
        self.Failure("=" * len(mes))
        self.Failure(mes)
        self.Failure("=" * len(mes))
        return False

    @property
    def ObjectCollectFailure(self):
        mess = "Can't Collect Particle Objects in event.Objects..."
        self.Failure("=" * len(mess))
        self.Failure(mess)
        self.Failure("=" * len(mess))
        return False

    @property
    def CheckVariableNames(self):
        if len(self.Event.Trees) != 0:
            return True

        ex = "The Event implementation has an empty self.Trees variable!"
        self.Failure("=" * len(ex))
        self.Failure(ex)
        self.Failure("=" * len(ex))
        return False

    @property
    def CheckSpawnedEvents(self):
        if len(self) == 0:
            self.Warning("No Events were generated...")
            self.Warning("If this is unexpected, double to check")
            return not self.Warning("Your event implementation.")
        return True

    @property
    def CheckSettings(self):
        if self.EventStop == None:
            return
        if self.EventStop > self.EventStart:
            return
        self.Warning("EventStart is larger than EventStop. Switching.")
        self.EventStop, self.EventStart = self.EventStart, self.EventStop
