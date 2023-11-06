from .Notification import Notification

class _nTupler(Notification):

    def __init__(self):
        pass

    def _MissingSelectionTreeSample(self, combi):
        combi = combi.split(".")
        msg = "Selection Name (" + combi[1] + ") "
        msg += "with the given Tree (" + combi[0] + ") "
        msg += "was not found in the loaded samples. "
        msg += "Skipping this combination"
        self.Warning(msg)

    def _MissingSelectionName(self, selection):
        msg = "Selection name: " + selection + " not found. Use the following syntax:"
        msg += "\n<var> = nTupler \n <var>.This('SelectionName -> variable', 'tree')"
        self.Warning(msg)
        self.Warning("OPTIONS ARE LISTED BELOW:")
        self.Warning("\n-> ".join([""] + self.ShowSelections))

    def _FoundSelectionName(self, selection):
        msg = "!!Selection name: " +  selection + " found."
        self.Success(msg)
