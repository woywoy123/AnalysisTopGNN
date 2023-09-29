from AnalysisG.Templates import GraphTemplate

class SimpleGraph(GraphTemplate):

    # Make sure to add the Event = None argument.
    # The class will be exposed to a pre-compiler 
    # where your event implementation will be injected.
    def __init__(self, Event = None):
        GraphTemplate.__init__(self)

        # The self.Event needs to be set as to provide attribute protection
        self.Event = Event  # <- the self.Event is done on purpose 
        self.Particles = self.Event.Out # <- A list of jets

