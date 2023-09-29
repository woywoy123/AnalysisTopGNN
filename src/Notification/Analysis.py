from .Notification import Notification
from time import sleep
import h5py


class _Analysis(Notification):
    def __init__(self):
        pass

    def _WarningPurge(self):
        self.Warning("'PurgeCache' enabled! You have 10 seconds to cancel.")
        self.Warning("Directory (DataCache/EventCache): " + self.OutputDirectory)
        _, bar = self._MakeBar(10, "PURGE-TIMER")
        for i in range(10):
            sleep(1)
            bar.update(1)
        self.rm(self.OutputDirectory + "/EventCache")
        self.rm(self.OutputDirectory + "/DataCache")
        self.rm(self.OutputDirectory + "/Tracer")
        self.rm(self.OutputDirectory + "/Training/DataSets")

    def _BuildingCache(self):
        if self.EventCache:
            self.mkdir(self.OutputDirectory + "/EventCache")
            self.Success("Created EventCache under: " + self.OutputDirectory)
        if self.DataCache:
            self.mkdir(self.OutputDirectory + "/DataCache")
            self.Success("Created DataCache under: " + self.OutputDirectory)

    def _CheckForTracer(self):
        f = self.ls(self.OutputDirectory + "/Tracer/")
        if len(f) == 0 and (self.EventCache or self.DataCache):
            return not self.Warning("Tracer directory not found. Generating")
        elif len(f) == 0:
            return not self.Warning(
                "No Tracer directory found... Generating just samples without cache!"
            )
        f = [
            t + "/" + i
            for t in f
            for i in self.ls(self.OutputDirectory + "/Tracer/" + t)
        ]
        tracers = {
            i: [
                t
                for t in h5py.File(self.OutputDirectory + "/Tracer/" + i)[
                    "MetaData"
                ].attrs
            ]
            for i in f
            if i.endswith(".hdf5")
        }
        f = ["!Tracers Found:"] if len(tracers) > 0 else ["No Tracers Found"]
        for tr in tracers:
            f += [" (" + tr + ") -> " + i for i in tracers[tr]]
        msg = "\n".join(f)
        msg += ""
        if len(tracers) > 0:
            self.Success("!" + msg)
        else:
            self.Warning(msg)
        self.WhiteSpace()
        return len(tracers) > 0

    def EmptySampleList(self):
        if self.len != 0:
            return False
        string = "No samples found in cache. Checking again..."
        self.Failure("=" * len(string))
        self.Failure(string)
        self.Failure("=" * len(string))
        return True

    def StartingAnalysis(self):
        string1 = "---" + " Starting Project: " + self.ProjectName + " ---"
        string = ""
        string += (
            " > EventGenerator < :: "
            if self.Event != None
            else ("> EventCache < :: " if self.EventCache else "")
        )
        string += (
            " > GraphGenerator < :: "
            if self.EventGraph != None
            else ("> DataCache < :: " if self.DataCache else "")
        )
        string += "> SampleGenerator < :: " if self.kFolds else ""
        string += "> Optimization < :: " if self.Model != None else ""
        string += " > Selections < :: " if len(self.Selections) != 0 else ""
        string += " > Merging Selections < :: " if len(self.Merge) != 0 else ""

        l = len(string) if len(string1) < len(string) else len(string1)
        self.Success("=" * l)
        self.Success(string1)
        self.Success(string)
        self.Success("=" * l)
