from AnalysisG.Notification import _SelectionGenerator
from AnalysisG.Templates import SelectionTemplate
from AnalysisG.IO import PickleObject, UnpickleObject
from AnalysisG.Tools import Code, Threading
from .EventGenerator import EventGenerator
from AnalysisG.Tracer import SampleTracer
from AnalysisG.Settings import Settings
from .Interfaces import _Interface
from typing import Union
from time import sleep
import codecs
import pickle
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
        for i in range(len(inpt)):
            name, sel, event, hash_, ROOT, pth = inpt[i]
            sel.hash = hash_
            sel.ROOTName = ROOT
            sel._EventPreprocessing(event)

            if name not in output:
                output[name] = sel
            else:
                output[name] += sel

            if lock == None:
                bar.update(1)
            else:
                with lock:
                    bar.update(1)
        if lock == None:
            del bar
        for name in output:
            PickleObject(output[name], pth + name + "/" + output[name].hash)
        return []

    def __collect__(self, inpt, key):
        x = {c_name: Code(inpt[c_name]) for c_name in inpt}
        if len(x) != 0:
            self._Code[key] = x

    @property
    def __merge__(self):
        for name in self.Merge:
            if len(self.Merge[name]) == 0:
                continue
            co = self._Code["Selections"][name]
            sys.path.append("/".join(co._File.split("/")[:-1]))
            sm = sum(
                [UnpickleObject(i) for i in self.Merge[name] if not i.endswith(".py")]
            )
            PickleObject(sm._dump, self.OutputDirectory + "/Selections/Merged/" + name)
            for i in self.Merge[name]:
                self.rm(i)
            self.Merge[name] = []

    @property
    def MakeSelection(self):
        self.__collect__(self.Selections, "Selections")
        if self._condor:
            return self._Code
        if len(self.Merge) != 0:
            pass
        elif self.CheckSettings:
            return False
        self.pth = self.OutputDirectory + "/Selections/"
        if "Selections" in self._Code:
            for name in self._Code["Selections"]:
                self.mkdir(self.pth + name)
                self._Code["Selections"][name].purge
                f = open(self.pth + name + ".py", "w")
                f.write(self._encoder(self._Code["Selections"][name]))
                f.close()
                self._Code["Selections"][name] = self._decoder(
                    "".join(open(self.pth + name + ".py", "r").readlines())
                )

        for name in self.Selections:
            inpt = []
            for ev, i in zip(self, range(len(self))):
                if self._StartStop(i) == False:
                    continue
                if self._StartStop(i) == None:
                    break
                if ev.Graph:
                    continue
                sel = self._Code["Selections"][name].clone
                inpt.append([name, sel, ev, ev.hash, ev.ROOT, self.pth])

            if len(inpt) == 0:
                return self.__merge__
            if self.Threads > 1:
                th = Threading(inpt, self.__compile__, self.Threads, self.chnk)
                th.Title = self.Caller + "::" + name
                th.Start
            else:
                self.__compile__(inpt, self._MakeBar(len(inpt)))

        if len(self.Merge) == 0:
            return
        self._Code["Selections"] = {}
        for name in self.Merge:
            self.Merge[name] = [
                self.pth + name + "/" + i for i in self.ls(self.pth + name + "/")
            ]
            self._Code["Selections"][name] = self._decoder("".join(open(self.pth + name + ".py", "r").readlines()))
            self.__merge__
