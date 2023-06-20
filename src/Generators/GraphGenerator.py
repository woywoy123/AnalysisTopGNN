from AnalysisG.Generators.EventGenerator import EventGenerator
from AnalysisG.Notification import _GraphGenerator
from AnalysisG.Tools import Code, Threading
from AnalysisG.Tracer import SampleTracer
from AnalysisG.Settings import Settings
from .Interfaces import _Interface
from typing import Union
from time import sleep
import pickle


class GraphGenerator(_GraphGenerator, Settings, SampleTracer, _Interface):
    def __init__(self, inpt: Union[EventGenerator, None] = None):
        self.Caller = "GRAPHGENERATOR"
        Settings.__init__(self)
        SampleTracer.__init__(self)
        _Interface.__init__(self)
        _GraphGenerator.__init__(self, inpt)

    @staticmethod
    def _CompileGraph(inpt, _prgbar):
        lock, bar = _prgbar
        for i in range(len(inpt)):
            hash_, gr_ = inpt[i]
            gr_ = pickle.loads(gr_)
            try:
                gr_.ConvertToData()
            except:
                pass
            if lock == None:
                bar.update(1)
            else:
                with lock:
                    bar.update(1)

            try:
                gr_ = gr_.purge
                num_nodes = gr_.num_nodes.item()
                gr_ = pickle.dumps(gr_)
            except:
                gr_ = None
                num_nodes = 0
            inpt[i] = [hash_, gr_, num_nodes]
        if lock == None:
            del bar
        return inpt

    def __collect__(self, inpt, key):
        x = {c_name: Code(inpt[c_name]) for c_name in inpt}
        if len(x) != 0:
            self._Code[key] = x

    @property
    def MakeGraphs(self):
        if not self.CheckGraphImplementation:
            return False
        if not self.CheckSettings:
            return False

        self._Code["EventGraph"] = Code(self.EventGraph)
        self.__collect__(self.GraphAttribute, "GraphAttribute")
        self.__collect__(self.NodeAttribute, "NodeAttribute")
        self.__collect__(self.EdgeAttribute, "EdgeAttribute")
        if self._condor:
            return self._Code

        inpt = []
        s = len(self)
        _, bar = self._MakeBar(s, "PREPARING GRAPH COMPILER")
        for ev, i in zip(self, range(s)):
            if self._StartStop(i) == False:
                continue
            if self._StartStop(i) == None:
                break
            bar.update(1)
            if ev.Graph:
                continue

            gr = self._Code["EventGraph"].clone
            try:
                gr = gr(ev)
            except AttributeError:
                gr = gr(None)
            gr.GraphAttr.update(self.GraphAttribute)
            gr.NodeAttr.update(self.NodeAttribute)
            gr.EdgeAttr.update(self.EdgeAttribute)
            gr.index = ev.index
            gr.SelfLoop = self.SelfLoop
            gr.FullyConnect = self.FullyConnect
            inpt.append([ev.hash, pickle.dumps(gr)])

        if len(inpt) == 0:
            return True
        if self.Threads > 1:
            th = Threading(inpt, self._CompileGraph, self.Threads, self.chnk)
            th.Title = self.Caller
            th.Start
        out = (
            th._lists
            if self.Threads > 1
            else self._CompileGraph(inpt, self._MakeBar(len(inpt)))
        )
        self.AddGraph(out)
        return True
