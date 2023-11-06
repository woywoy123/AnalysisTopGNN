from AnalysisG.Tools import Tools
from typing import Union, Dict, List
from tqdm import tqdm


class _Interface(Tools):
    def __init__(self):
        pass

    def InputSelection(self, val: Union[str]):
        self.Files = self.ListFilesInDir(val, ".hdf5")

    def InputSamples(self, val: Union[Dict, List, str, None]):
        self.Files = self.ListFilesInDir(val, ".root")

    def InputSample(
        self,
        Name: Union[str] = None,
        SampleDirectory: Union[str, Dict, List, None] = None,
    ):
        self.Files = None
        self.InputSamples(SampleDirectory)
        if Name is None: Name = ""

        add = {}
        add[Name] = []
        for i in self.Files: add[Name] += [i + "/" + j for j in self.Files[i]]
        self.SampleMap = add

    def _StartStop(self, it: Union[int]):
        if self.EventStart > it and self.EventStart != -1: return False
        if self.EventStop != None and self.EventStop - 1 < it: return None
        return True

    def _MakeBar(
        self, inpt: Union[int], CustTitle: Union[None, str] = None, Leave=False
    ):
        _dct = {}
        _dct["desc"] = f"Progress {self.Caller}" if CustTitle is None else CustTitle
        _dct["leave"] = Leave
        _dct["colour"] = "GREEN"
        _dct["dynamic_ncols"] = True
        _dct["total"] = inpt
        return (None, tqdm(**_dct))

    # Define the observable features
    def AddGraphFeature(self, fx, name=""):
        if self.SetAttribute(fx, "G_F_" + name): return
        self.Warning("Found Duplicate Graph " + name + " Attribute")

    def AddNodeFeature(self, fx, name=""):
        if self.SetAttribute(fx, "N_F_" + name): return
        self.Warning("Found Duplicate Node " + name + " Attribute")

    def AddEdgeFeature(self, fx, name=""):
        if self.SetAttribute(fx, "E_F_" + name): return
        self.Warning("Found Duplicate Edge " + name + " Attribute")

     # Define the truth features used for supervised learning
    def AddGraphTruthFeature(self, fx, name=""):
        if self.SetAttribute(fx, "G_T_" + name): return
        self.Warning("Found Duplicate Graph Truth " + name + " Attribute")

    def AddNodeTruthFeature(self, fx, name=""):
        if self.SetAttribute(fx, "N_T_" + name): return
        self.Warning("Found Duplicate Node Truth " + name + " Attribute")

    def AddEdgeTruthFeature(self, fx, name=""):
        if self.SetAttribute(fx, "E_T_" + name): return
        self.Warning("Found Duplicate Edge Truth " + name + " Attribute")

    def AddPreSelection(self, fx, name=""):
        if self.SetAttribute(fx, "P_F_" + name): return
        self.Warning("Found Duplicate Pre-Selection " + name + " Function")

    def AddTopology(self, fx, name=""):
        if self.SetAttribute(fx, "T_F_" + name): return
        self.Warning("Found Duplicate Topology " + name + " Function")

     # Selection generator
    def AddSelection(self, function):
        self.Selections = function

    def This(self, path: Union[str], tree: Union[str]):
        if tree not in self._DumpThis: self._DumpThis[tree] = []
        if path in self._DumpThis[tree]: return self.Warning("'" + path + "' is already in list")
        self._DumpThis[tree].append(path)
