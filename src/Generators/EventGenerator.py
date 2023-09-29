from AnalysisG.Notification import _EventGenerator
from AnalysisG.Tools import Code, Threading
from AnalysisG.Tracer import SampleTracer
from AnalysisG.Settings import Settings
from AnalysisG.IO import UpROOT
from .Interfaces import _Interface
from typing import Union
from time import sleep
import pickle


class EventGenerator(_EventGenerator, Settings, SampleTracer, _Interface):
    def __init__(self, val=None):
        self.Caller = "EVENTGENERATOR"
        Settings.__init__(self)
        SampleTracer.__init__(self)
        self.InputSamples(val)

    @staticmethod
    def _CompileEvent(inpt, _prgbar):
        lock, bar = _prgbar
        for i in range(len(inpt)):
            vals, ev = inpt[i]
            ev = pickle.loads(ev)
            inpt[i] = {}
            try:
                res = ev.__compiler__(vals)
                for k in res: k.CompileEvent()
            except: continue
            for k in list(res):
                inpt[i][k.hash] = {}
                inpt[i][k.hash]["pkl"] = pickle.dumps(k)
                inpt[i][k.hash]["index"] = k.index
                inpt[i][k.hash]["Tree"] = k.Tree
                inpt[i][k.hash]["ROOT"] = (
                    vals["MetaData"].thisSet + "/" + vals["MetaData"].thisDAOD
                )
                inpt[i][k.hash]["Meta"] = vals["MetaData"]
                del k
            del ev
            if lock is None:
                bar.update(1)
                continue
            with lock: bar.update(1)
        return inpt

    def MakeEvents(self):
        if not self.CheckEventImplementation():
            return False
        self.CheckSettings()

        self._Code["Event"] = Code(self.Event)
        try:
            dc = self.Event.Objects
            if not isinstance(dc, dict):
                raise AttributeError
        except AttributeError:
            self.Event = self.Event()
        except TypeError:
            self.Event = self.Event()
        except:
            return self.ObjectCollectFailure()
        self._Code["Particles"] = {
            i: Code(self.Event.Objects[i]) for i in self.Event.Objects
        }
        if self._condor: return self._Code
        if not self.CheckROOTFiles(): return False
        if not self.CheckVariableNames(): return False

        ev = self.Event
        ev.__interpret__

        io = UpROOT(self.Files)
        io.Verbose = self.Verbose
        io.Trees = ev.Trees
        io.Leaves = ev.Leaves
        io.DisablePyAMI = self.DisablePyAMI

        inpt = []
        ev = pickle.dumps(ev)
        i = -1
        for v in io:
            i += 1
            if self._StartStop(i) == False: continue
            if self._StartStop(i) == None: break
            inpt.append([v, ev])
        if self.Threads > 1:
            th = Threading(inpt, self._CompileEvent, self.Threads, self.chnk)
            th.Start()
        out = (
            th._lists
            if self.Threads > 1
            else self._CompileEvent(inpt, self._MakeBar(len(inpt)))
        )
        ev = {}
        for i in out:
            ev.update(i)
        self.AddEvent(ev)
        return self.CheckSpawnedEvents()
