from .Notification import Notification


class _Plotting(Notification):
    def __init__(self):
        pass

    def InvalidVariableKey(self, key):
        if key not in self.__dict__:
            self.Warning("Provided variable '" + key + "' not found.")
            return True
        return False

    def NoDataGiven(self):
        self.Warning("NO VALID DATA GIVEN ... Skipping: " + self.Title)

    def SavingFigure(self, output):
        self.Success("!!SAVING FIGURE AS +-> " + output)
