from AnalysisG.Notification import _SelectionGenerator
from AnalysisG.Templates import SelectionTemplate
from AnalysisG.IO import PickleObject, UnpickleObject
from AnalysisG.Tools import Code, Threading, Hash
from .EventGenerator import EventGenerator
from AnalysisG.Tracer import SampleTracer
from AnalysisG.Settings import Settings
from .Interfaces import _Interface
from typing import Union
import h5py
import sys

class SelectionGenerator(_SelectionGenerator, Settings, SampleTracer, _Interface):
    def __init__(self, inpt: Union[EventGenerator, None] = None):
        self.Caller = "SELECTIONGENERATOR"
        Settings.__init__(self)
        SampleTracer.__init__(self)
        _Interface.__init__(self)
        _SelectionGenerator.__init__(self, inpt)

    @staticmethod
    def __compile__(inpt, _prgbar):
        lock, bar = _prgbar
        output = {}
        code = {}
        fname = ""
        for i in range(len(inpt)):
            name, sel_, event, pth = inpt[i]
            sel = SampleTracer._decoder(sel_).clone()
            sel.hash = event.hash
            sel.ROOTName = event.ROOT
            sel.index = event.index
            sel.Tree = event.Tree
            sel._EventPreprocessing(event)
            fname = Hash(fname + sel.hash)
            if name not in output: output[name] = []
            output[name].append(sel)
            try: code[name]
            except KeyError: code[name] = [sel_]
            if lock is not None: bar.update(1)

        for name in output:
            f = h5py.File(pth + name + "/" + fname + ".hdf5", "w")
            ref = f.create_dataset(name, (1), dtype = h5py.ref_dtype)
            for sel in output[name]: ref.attrs[sel.hash] = SampleTracer._encoder(sel)

            try: ref.attrs["code"] = next(iter(code[name]))
            except KeyError: pass

            f.close()
        return []

    def __collect__(self, inpt, key):
        x = {c_name: Code(inpt[c_name]) for c_name in inpt}
        if len(x) != 0: self._Code[key] = x

    def __merge__(self):
        for name in self.Merge:
            if len(self.Merge[name]) == 0: continue
            self.mkdir(self.OutputDirectory + "/Selections/Merged/")
            fo = h5py.File(self.OutputDirectory + "/Selections/Merged/" + name + ".hdf5", "w")
            ref = fo.create_dataset(name, (1), dtype = h5py.ref_dtype)
            for h in self.Merge[name]:
                f = h5py.File(h, "r")
                f_ = f[name]
                for key in f_.attrs: ref.attrs[key] = f_.attrs[key]
                f.close()
                self.rm(h)
            fo.close()
            self.Merge[name] = []
            self.rm(self.OutputDirectory + "/Selections/" + name)

    def MakeSelection(self):
        self.__collect__(self.Selections, "Selections")
        if self._condor: return self._Code
        if len(self.Merge) != 0: pass
        elif self.CheckSettings(): return False

        self.pth = self.OutputDirectory + "/Selections/"
        for name in self.Selections:
            self.mkdir(self.pth + name)
            sel = self._encoder(self._Code["Selections"][name])
            inpt = []
            for ev, i in zip(self, range(len(self))):
                if self._StartStop(i) == False: continue
                if self._StartStop(i) == None: break
                if ev.Graph: continue
                inpt.append([name, sel, ev, self.pth])

            if len(inpt) == 0: return self.__merge__()
            if self.Threads > 1:
                th = Threading(inpt, self.__compile__, self.Threads, self.chnk)
                th.Title = self.Caller + "::" + name
                th.Start()
            else: self.__compile__(inpt, (None, None))

        if len(self.Merge) == 0: return
        self._Code["Selections"] = {}
        for name in self.Merge:
            pths = self.pth + name + "/"
            self.Merge[name] = [
                 pths + i for i in self.ls(pths) if i.endswith(".hdf5")
            ]
            self.__merge__()
