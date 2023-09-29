from AnalysisG.Templates import SelectionTemplate


class Example(SelectionTemplate):
    def __init__(self):
        SelectionTemplate.__init__(self)
        self.Top = {"Truth": []}
        self.Children = {"Truth": []}

    def Strategy(self, event):
        self.Top["Truth"] += [t.Mass for t in event.Tops]
        self.Children["Truth"] += [c.Mass for c in event.Children]
        return "Success->Example"


class Example2(SelectionTemplate):
    def __init__(self):
        SelectionTemplate.__init__(self)
        self.Top = {"Truth": []}
        self.Children = {"Truth": []}
        self.AllowFailure = True

    def Strategy(self, event):
        self.Top["Truth"] += [t.Mass for t in event.Tops]
        self.Children["Truth"] += [c.Mass for c in event.Children]
        self.Children["Test"] = {}
        self.Children["Test"]["t"] = [1]
        self.Out # call missing attribute.
        return "Success->Example"
