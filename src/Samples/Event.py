from .Hashing import Hashing

class EventContainer(Hashing):

    def __init__(self):
        self.Trees = {}
        self.EventIndex = 0
        self.Filename = None
        self.Compiled = False
        self.Train = None

    def MakeEvent(self, ClearVal):
        for i in self.Trees:
            self.Trees[i]._Compile(ClearVal)
            self.Filename = self.MD5(self.Filename + "/" + str(self.EventIndex))
    
    def MakeGraph(self):
        if self.Compiled: 
            return self
        for i in self.Trees:
            try:
                self.Trees[i] = self.Trees[i].ConvertToData()
            except AttributeError:
                return self
        self.Compiled = True
        return self

    def __add__(self, other):
        if other == "":
            return self

        if self.Filename != other.Filename:
            return [self, other]
        
        if isinstance(other, str):
            return self
        
        if other.Compiled and self.Compiled == False:
            self.Trees = self.Trees | other.Trees
            self.Compiled = True
        else:
            self.Trees = {tr : other.Trees[tr] if tr in other.Trees else self.Trees[tr] for tr in other.Trees}
        return self

    def __eq__(self, other):
        if type(other) != type(self): return False

        same = True if self.Filename == other.Filename else False
        same = True if self.Compiled == other.Compiled and same else False
       
        return same

    def UpdateIndex(self, index):
        self.EventIndex = index
        return self
