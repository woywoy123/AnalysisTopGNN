from AnalysisG.Notification import _GraphGenerator
from AnalysisG._cmodules.SampleTracer import Event
from AnalysisG.SampleTracer import SampleTracer
from AnalysisG.Templates import GraphTemplate
from AnalysisG.Tools import Threading
from .Interfaces import _Interface
from typing import Union
import pickle
from time import sleep

class GraphGenerator(_GraphGenerator, SampleTracer, _Interface):
    def __init__(self, inpt = None):
        SampleTracer.__init__(self)
        _GraphGenerator.__init__(self, inpt)
        self.Caller = "GRAPHGENERATOR"
        _Interface.__init__(self)

    @staticmethod
    def _CompileGraph(inpt, _prgbar):
        lock, bar = _prgbar
        if not len(inpt): return [None]
        for i in range(len(inpt)):
            ev = pickle.loads(inpt[i][0])
            code, graph = inpt[i][1]
            code  = pickle.loads(code)
            graph = pickle.loads(graph)
            gr = graph(ev)
            grx = graph()
            grx.Import(code["__state__"])
            grx.ImportCode(code)
            grx.Event = gr.Event
            grx.Particles = [p.get() for p in gr.Particles]
            grx.Build()
            inpt[i] = grx.__getstate__()
            grx.code_owner = True
            del gr, graph, grx, code, ev
            if bar is None: continue
            elif lock is None: bar.update(1)
            else:
                with lock: bar.update(1)
        return inpt

    def MakeGraphs(self, sample = None):
        if sample is not None: pass
        else: sample = self

        if not self.CheckGraphImplementation(): return False
        if not self.CheckSettings(): return False

        code = pickle.dumps(self.Graph.code)
        graph = pickle.dumps(self.Graph)
        self.preiteration(sample)

        itx = 1
        chnks = self.Threads * self.Chunks
        step = chnks

        command = [[], self._CompileGraph, self.Threads, self.Chunks]

        path = sample.Tree + "/" + sample.EventName
        try: itr = sample.ShowLength[path]
        except KeyError: itr = 0
        if not itr: return True
        _, bar = self._makebar(itr, self.Caller + "::Preparing Graphs")
        for ev, i in zip(sample, range(itr)):
            if sample._StartStop(i) == False: continue
            if sample._StartStop(i) == None: break
            bar.update(1)

            if ev.Graph: continue
            if not ev.Event: continue

            command[0].append([pickle.dumps(ev.release_event()), (code, graph)])
            if not i >= step: continue
            itx += 1
            step = itx*chnks
            th = Threading(*command)
            th.Start()

            for x in th._lists: sample.AddGraph(x)
            command[0] = []
            del th

        if not len(command[0]): return True
        th = Threading(*command)
        th.Start()
        for i in th._lists: sample.AddGraph(i)
        del th
        return True

    def preiteration(self, inpt = None):
        if inpt is not None: pass
        else: inpt = self

        if not len(inpt.ShowLength): return True
        if not len(inpt.ShowTrees): return True

        if not len(inpt.Tree):
            try: inpt.Tree = inpt.ShowTrees[0]
            except IndexError: return True

        if not len(inpt.EventName):
            try: inpt.EventName = inpt.ShowEvents[0]
            except IndexError: inpt.EventName = None
            self.GetEvent = True

        if not len(inpt.GraphName):
            try: inpt.GraphName = inpt.ShowGraphs[0]
            except IndexError: inpt.GraphName = None
            self.GetGraph = True
        return False
