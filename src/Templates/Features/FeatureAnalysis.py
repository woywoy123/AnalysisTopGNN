from AnalysisG.Notification import _FeatureAnalysis
from AnalysisG.Settings import Settings
from AnalysisG.Tools import Code


class FeatureAnalysis(_FeatureAnalysis, Settings):
    def __init__(self):
        self.Caller = "FEATUREANALYSIS"

    def TestGraphFeature(self, Event, EventGraph, Fx):
        return Fx(EventGraph(Event).Event)

    def TestNodeFeature(self, Event, EventGraph, Fx):
        return [Fx(i) for i in EventGraph(Event).Particles]

    def TestEdgeFeature(self, Event, EventGraph, Fx):
        ev = EventGraph(Event)
        return [Fx(i, j) for i in ev.Particles for j in ev.Particles]

    def TestEvent(self, Event, EventGraph, EventIndex=None):
        if isinstance(Event, list):
            for ev in Event:
                if self.TestEvent(ev, EventGraph, " " + str(ev.index)):
                    return True
            return False

        self.Success("!!!> Test at EventIndex:" + EventIndex)
        count = 0
        for c_name in self.GraphAttribute:
            try:
                self.TestGraphFeature(
                    Event, Code(EventGraph).clone, self.GraphAttribute[c_name]
                )
                self.PassedTest(c_name, "GRAPH")
            except AttributeError:
                self.FeatureFailure(c_name, "GRAPH", EventIndex)
                count += 1

        for c_name in self.NodeAttribute:
            try:
                self.TestNodeFeature(
                    Event, Code(EventGraph).clone, self.NodeAttribute[c_name]
                )
                self.PassedTest(c_name, "NODE")
            except AttributeError:
                self.FeatureFailure(c_name, "NODE", EventIndex)
                count += 1

        for c_name in self.EdgeAttribute:
            try:
                self.TestEdgeFeature(
                    Event, Code(EventGraph).clone, self.EdgeAttribute[c_name]
                )
                self.PassedTest(c_name, "EDGE")
            except AttributeError:
                self.FeatureFailure(c_name, "EDGE", EventIndex)
                count += 1
        if count > 0:
            return self.TotalFailure()
        return False
