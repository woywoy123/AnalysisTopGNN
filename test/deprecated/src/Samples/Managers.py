from .SampleContainer import SampleContainer
import copy


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
        self._lst = list(set(self.dict()))
        return len(self._lst)

    def __contains__(self, key):
        return key in self.SampleContainer

    def __iter__(self):
        if self.Caller == "EVENTGENERATOR":
            self._lst = self.list()
        elif self.Caller == "GRAPHGENERATOR":
            self._lst = [i for i in self.list() if i.Compiled]
        elif self.Caller == "OPTIMIZATION":
            self._lst = [
                i for i in self.list() if i.Compiled and (i.Train or i.Train == None)
            ]
        else:
            self._lst = self.list()
        return self

    def __next__(self):
        if len(self._lst) == 0:
            raise StopIteration()
        return self._lst.pop(0)

    def __getitem__(self, key):
        return self.SampleContainer[key]

    def __radd__(self, other):
        if other == 0:
            return self
        self.__add__(other)

    def __add__(self, other):
        smpl = copy.deepcopy(self)
        smpl.SampleContainer += other.SampleContainer
        return smpl

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)
