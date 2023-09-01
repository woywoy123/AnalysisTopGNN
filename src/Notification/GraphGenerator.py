from .Notification import Notification

class _GraphGenerator(Notification):
    def __init__(self, inpt):
        if inpt is None: return
        if self.is_self(inpt): self += inpt
        else: self.WrongInput()

    def WrongInput(self):
        self.Warning("Input instance is of wrong type. Skipping...")

    def CheckGraphImplementation(self):
        if self.Graph is not None and not self.preiteration(): return True
        ex = "Or do: from AnalysisG.Events import Event"
        self.Failure("=" * len(ex))
        self.Failure("No Graph Implementation Provided.")
        self.Failure("var = " + self.Caller.capitalize() + "()")
        self.Failure("var.Graph")
        self.Failure("See src/Events/Graphs/EventGraphs.py or 'tutorial'")
        self.Failure("=" * len(ex))
        return False

    def CheckSettings(self):
        edge, node, graph = [], [], []
        for i in self.Graph.code:
            if   i.startswith("G_"): graph.append(i[3:])
            elif i.startswith("N_"): node.append(i[3:])
            elif i.startswith("E_"): edge.append(i[3:])

        attrs = 3
        attrs -= (
            1 * self.Warning("NO EDGE FEATURES PROVIDED")
            if not len(edge)
            else 0
        )
        attrs -= (
            1 * self.Warning("NO NODE FEATURES PROVIDED")
            if not len(node)
            else 0
        )
        attrs -= (
            1 * self.Warning("NO GRAPH FEATURES PROVIDED")
            if not len(graph)
            else 0
        )
        if attrs != 0:
            return self.Success("Data being processed on: " + self.Device)

        message = "NO ATTRIBUTES DEFINED!"
        self.Failure("=" * len(message))
        self.Failure(message)
        return self.Failure("=" * len(message))
