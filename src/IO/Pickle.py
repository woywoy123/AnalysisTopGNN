from AnalysisG.Tools import Tools, Threading
from AnalysisG.Settings import Settings
import pickle
import sys


class Pickle(Tools, Settings):
    def __init__(self):
        self.Caller = "PICKLER"
        Settings.__init__(self)

    def PickleObject(self, obj, filename, Dir="_Pickle"):
        filename = self.AddTrailing(filename, self._ext)
        direc = self.path(filename)
        direc = self.RemoveTrailing(direc, "/")
        filename = self.filename(filename)

        if self.RemoveTrailing(self.pwd(), "/") == direc:
            direc += "/" + Dir

        self.mkdir(direc)
        f = open(direc + "/" + filename, "wb")
        pickle.dump(obj, f)
        f.close()

    def UnpickleObject(self, filename, Dir="_Pickle"):
        filename = self.AddTrailing(filename, self._ext)
        direc = self.path(filename)
        filename = self.filename(filename)

        if self.RemoveTrailing(self.pwd(), "/") == direc:
            direc += "/" + Dir
        if self.IsFile(direc + "/" + filename) == False:
            return

        f = open(direc + "/" + filename, "rb")
        obj = pickle.load(f)
        f.close()
        return obj

    def MultiThreadedDump(self, ObjectDict, OutputDirectory, Name=None):
        def function(inpt):
            out = []
            for i in inpt:
                self.PickleObject(i[1], i[0], OutputDirectory)
                out.append(i[0])
            return out

        inpo = [[name, ObjectDict[name]] for name in ObjectDict]
        TH = Threading(inpo, function, self.Threads, self.chnk)
        TH.Verbose = self.Verbose
        TH.Title = "DUMPING PICKLES "
        TH.Title += "" if Name == None else "(" + Name + ")"
        TH.Start()

    def MultiThreadedReading(self, InputFiles, Name=None):
        def function(inpt):
            out = []
            for i in inpt:
                out.append(
                    [i.split("/")[-1].replace(self._ext, ""), self.UnpickleObject(i)]
                )
            return out

        #
        InputFiles = [
            InputFiles[i] for i in range(len(InputFiles)) if i not in ClassDef
        ]

        TH = Threading(InputFiles, function, self.Threads, self.chnk)
        TH.Verbose = self.Verbose
        TH.Title = "READING PICKLES "
        TH.Title += "" if Name == None else "(" + Name + ")"
        TH.Start()
        return {i[0]: i[1] for i in TH._lists}


def _UnpickleObject(filename):
    return Pickle().UnpickleObject(filename)


def _PickleObject(obj, filename):
    Pickle().PickleObject(obj, filename)
