from AnalysisG.Notification import _FeatureAnalysis
from AnalysisG.SampleTracer import SampleTracer

class FeatureAnalysis(_FeatureAnalysis, SampleTracer):
    def __init__(self):
        SampleTracer.__init__(self)
        self.Caller = "FEATURE-ANALYSIS"
        self.GraphAttribute = {}
        self.NodeAttribute  = {}
        self.EdgeAttribute  = {}

    def TestGraphFeature(self, Event, EventGraph, Fx):
        Fx(EventGraph(Event).Event)

    def TestNodeFeature(self, Event, EventGraph, Fx):
        [Fx(i) for i in EventGraph(Event).Particles]

    def TestEdgeFeature(self, Event, EventGraph, Fx):
        x = EventGraph(Event).Particles
        [Fx(i, j) for i in x for j in x]

    def TestEvent(self, Event, EventGraph, EventIndex=None):
        if isinstance(Event, list):
            for ev in Event:
                self.TestEvent(ev, EventGraph, ev.index)
            return False

        EventIndex = " " + str(EventIndex)
        self.Success("!!!> Test at EventIndex:" + EventIndex)
        count = 0
        for c_name, code in self.GraphAttribute.items():
            try:
                self.TestGraphFeature(Event, EventGraph, code)
                self.PassedTest(c_name, "GRAPH")
            except KeyError:
                self.FeatureFailure(c_name, "GRAPH", EventIndex)
                count += 1

        for c_name, code in self.NodeAttribute.items():
            try:
                self.TestNodeFeature(Event, EventGraph, code)
                self.PassedTest(c_name, "NODE")
            except KeyError:
                self.FeatureFailure(c_name, "NODE", EventIndex)
                count += 1

        for c_name, code in self.EdgeAttribute.items():
            try:
                self.TestEdgeFeature(Event, EventGraph, code)
                self.PassedTest(c_name, "EDGE")
            except KeyError:
                self.FeatureFailure(c_name, "EDGE", EventIndex)
                count += 1
        if count > 0: return self.TotalFailure()
        self.WhiteSpace()
        return False
