from AnalysisG.Templates import GraphTemplate


class DataGraph(GraphTemplate):
    def __init__(self, Event=None):
        GraphTemplate.__init__(self)
        self.Event = Event
        self.Particles += self.Event.Tops
