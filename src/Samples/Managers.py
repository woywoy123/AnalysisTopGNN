from .SampleContainer import SampleContainer

class SampleTracer:

    def __init__(self):
        self.SampleContainer = SampleContainer()

    def ResetSampleContainer(self):
        self.SampleContainer = SampleContainer()

    def AddROOTFile(self, Name, Event):
        if self.SampleContainer == None:
            self.SampleContainer = SampleContainer()
        self.SampleContainer.AddEvent(Name, Event) 
    
    def HashToROOT(self, _hash):
        return self.SampleContainer.HashToROOT(_hash)

    def GetROOTContainer(self, Name):
        return self.SampleContainer.ROOTFiles[Name]
    
    def list(self):
        return self.SampleContainer.list()

    def dict(self):
        return self.SampleContainer.dict()

    def __len__(self):
        self.__iter__()
        return len(self._lst)
    
    def __contains__(self, key):
        return key in self.SampleContainer

    def __iter__(self):
        if self.Caller == "EVENTGENERATOR":
            self._lst = self.list()
        elif self.Caller == "GRAPHGENERATOR":
            self._lst = [i for i in self.list() if i.Compiled]
        else:
            self._lst = self.list()
        return self

    def __next__(self):
        if len(self._lst) == 0:
            raise StopIteration()
        return self._lst.pop(0)
    
    def __getitem__(self, key):
        return self.SampleContainer[key]

    def __add__(self, other):
        self.SampleContainer += other.SampleContainer
        return self
        
    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)
    
