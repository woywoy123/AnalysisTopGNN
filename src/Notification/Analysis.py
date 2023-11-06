from .Notification import Notification
from time import sleep
import h5py


class _Analysis(Notification):
    def __init__(self):
        pass

    def _WarningPurge(self):
        self.Warning("'PurgeCache' enabled! You have 10 seconds to cancel.")
        self.Warning("Directory (DataCache/EventCache): " + self.WorkingPath)
        _, bar = self._MakeBar(10, "PURGE-TIMER")
        for i in range(10):
            sleep(1)
            bar.update(1)
        self.rm(self.WorkingPath + "EventCache")
        self.rm(self.WorkingPath + "GraphCache")
        self.rm(self.WorkingPath + "Tracer")
        self.rm(self.WorkingPath + "Training/DataSets")

    def _BuildingCache(self):
        if self.EventCache:
            self.mkdir(self.WorkingPath + "EventCache")
            self.Success("Created EventCache under: " + self.WorkingPath)
        if self.DataCache:
            self.mkdir(self.WorkingPath + "GraphCache")
            self.Success("Created GraphCache under: " + self.WorkingPath)

    def _CheckForTracer(self):
        tracers = self.ListFilesInDir(self.WorkingPath + "Tracer/*", ".hdf5")
        if len(tracers) == 0 and (self.EventCache or self.DataCache):
            message = "Tracer directory not found. Generating"
            return not self.Warning(message)
        elif len(tracers) == 0:
            message = "No Tracer directory found... Generating just samples without cache!"
            return not self.Warning(message)
        if len(tracers) > 0: self.Success("!Found Tracers")
        else: self.Warning("Missing Tracers")
        self.WhiteSpace()
        return tracers

    def EmptySampleList(self):
        if len(self): return False
        string = "No samples found in cache."
        self.Failure("=" * len(string))
        self.Failure(string)
        self.Failure("=" * len(string))
        return True

    def StartingAnalysis(self):
        string1 = "---" + " Starting Project: " + self.ProjectName + " ---"
        string = []
        key = " > EventGenerator < ::"
        if self.Event is not None: string += [key]
        elif self.EventCache: string += [" > EventCache < ::"]

        key = " > GraphGenerator < ::"
        if self.Graph is not None: string += [key]
        elif self.DataCache: string += [" > DataCache < ::"]

        key = " > SampleGenerator ("
        if self.kFolds: string += [key + str(self.kFolds) + "-Fold) < ::"]
        if self.TrainingSize: string += [key + str(self.TrainingSize) + "%) < ::"]

        key = " > SelectionGenerator ("
        for k in self.Selections: string += [key + k + ") < ::"]
        if self.SelectionName: string += [key + self.SelectionName + ") < ::"]

        key = "> Optimization ("
        if self.Model is None: pass
        else: string += [key + self.Model.code["class_name"].decode("UTF-8") + ") < ::"]

        l = max([len(i) for i in string] + [len(string1)])
        self.Success("=" * l)
        self.Success(string1)
        for i in string: self.Success(i)
        self.Success("=" * l)
        if len(string): return True

        msg = "Nothing Selected..."
        self.Failure(len(msg)*"=")
        self.FailureExit(msg)
