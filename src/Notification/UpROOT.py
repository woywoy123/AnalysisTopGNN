from .Notification import Notification

class UpROOT(Notification):

    def __init__(self):
        pass

    def SkippedKey(self, Type, KeyList):
        for i in KeyList:
            self.Warning("SKIPPED: " + Type + "::" + i)
    
    def ReadingFile(self, Name):
        self.Success("!!!(Reading) -> " + Name.split("/")[-1] + 
                     " (" + ", ".join([t + " - " + str(self._Reader[t].num_entries) for t in self.Trees]) + ")")
