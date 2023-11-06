from AnalysisG.Notification import _EventGenerator
from AnalysisG.SampleTracer import SampleTracer
from AnalysisG.IO.UpROOT import UpROOT
from AnalysisG.Tools import Threading
from .Interfaces import _Interface
from typing import Union
from time import sleep
import pickle


class EventGenerator(_EventGenerator, _Interface, SampleTracer):
    def __init__(self, val=None):
        SampleTracer.__init__(self)
        self.Caller = "EVENTGENERATOR"
        self.InputSamples(val)

    @staticmethod
    def _CompileEvent(inpt, _prgbar):
        lock, bar = _prgbar
        try: code = pickle.loads(inpt[0][0]).code
        except AttributeError: code = None
        ev = pickle.loads(inpt[0][0]).clone()

        tracer = SampleTracer()
        for i in range(len(inpt)):
            _, vals = inpt[i]
            res = ev.__compiler__(vals)
            inpt[i] = None
            for k in res:
                k.CompileEvent()
                if code is not None: setattr(k, "code", code)
                tracer.AddEvent(k, vals["MetaData"])
            if bar is None: continue
            elif lock is None: bar.update(1)
            else:
                with lock: bar.update(1)
        return [tracer.__getstate__()]

    def MakeEvents(self, SampleName = None, sample = None):
        if SampleName is None: SampleName = ""
        if not self.CheckEventImplementation(): return False
        if len(self.ShowEvents) > 0: pass
        else: return self.ObjectCollectFailure()
        if not self.CheckROOTFiles(): return False
        if not self.CheckVariableNames(): return False

        ev = self.Event
        ev.__getleaves__()

        io = UpROOT(self.Files, True)
        io.Verbose = self.Verbose
        io.Trees = ev.Trees
        io.Leaves = ev.Leaves
        io.EnablePyAMI = self.EnablePyAMI
        io.metacache_path = self.OutputDirectory + self.ProjectName + "/metacache/"

        chnks = self.Threads * self.Chunks * self.Threads
        command = [[], self._CompileEvent, self.Threads, self.Chunks]

        i = -1
        step, itx = chnks, 1
        ev = pickle.dumps(ev)

        chnks = self.Threads * self.Chunks * self.Threads
        if sample is not None: pass
        else: sample = self

        for v in io:
            i += 1
            if self._StartStop(i) == False: continue
            if self._StartStop(i) == None: break
            v["MetaData"].sample_name = SampleName
            command[0].append([ev, v])
            if not i >= step: continue
            itx += 1
            step = itx*chnks
            th = Threading(*command)
            th.Start()
            for x in th._lists:
                if x is None: continue
                smpl = SampleTracer()
                smpl.__setstate__(x)
                sample += smpl
                del smpl
            command[0] = []
            del th

        if len(command[0]):
            th = Threading(*command)
            th.Start()
            for x in th._lists:
                if x is None: continue
                smpl = SampleTracer()
                smpl.__setstate__(x)
                sample += smpl
                del smpl
            command[0] = []
            del th
        if not self.is_self(sample, EventGenerator): return True
        else: return sample.CheckSpawnedEvents()

    def preiteration(self):
        if not len(self.Tree):
            try: self.Tree = self.ShowTrees[0]
            except IndexError: return True
        if not len(self.EventName):
            try: self.EventName = self.ShowEvents[0]
            except IndexError: return True
            self.GetEvent = True
        return False
