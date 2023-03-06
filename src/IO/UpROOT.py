from AnalysisTopGNN.Notification.UpROOT import UpROOT
from AnalysisTopGNN.Generators.Settings import Settings
from AnalysisTopGNN.Tools import Threading
import uproot 

class File(UpROOT, Settings):
    def __init__(self, ROOTFile):
        self.Caller = "FILE"
        Settings.__init__(self)
        self.Trees = []
        self.Branches = []
        self.Leaves = []
        self.ROOTFile = ROOTFile
        self._Reader =  uproot.open(self.ROOTFile)
        self._State = None
   
    def _CheckKeys(self, List, Type):
        TMP = []

        t = []
        for i in [k for k in self._State.keys() if "/" not in k]:
            if ";" in i:
                i = i.split(";")[0]
            t.append(i)

        for i in List:
            if i not in t:
                continue
            TMP.append(i)
            
        return TMP
    
    def _GetKeys(self, List1, List2, Type):
        TMP = []
        for i in List1:
            self._State = self._Reader[i]
            TMP += [i + "/" + j for j in self._CheckKeys(List2, Type)]
             
        for i in TMP:
            if i.split("/")[-1] in List2:
                List2.pop(List2.index(i.split("/")[-1]))
        
        if len(List1) == 0:
            return []
        self.SkippedKey(Type, List2) 
        return TMP

    def _GetBranches(self):
        return self._GetKeys(self.Trees, self.Branches, "BRANCH")
    
    def _GetLeaves(self):
        leaves = []
        leaves += self._GetKeys(self.Branches, self.Leaves, "LEAF")
        leaves += self._GetKeys(self.Trees, self.Leaves, "LEAF")
        return leaves 
    
    def ValidateKeys(self):
        self.Leaves = list(set(self.Leaves))
        self.Branches = list(set(self.Branches))
        self.Trees = list(set(self.Trees))
        self._State = self._Reader 
        self.Trees = self._CheckKeys(self.Trees, "TREE")
        self.Branches = self._GetBranches()
        self.Leaves = self._GetLeaves() 
    
    def __len__(self):
        self.ReadingFile(self.ROOTFile)
        return self._Reader[self.Trees[-1]].num_entries

    def __iter__(self):
        self.ReadingFile(self.ROOTFile)
        All = [b.split("/")[-1] for b in self.Branches] + [l.split("/")[-1] for l in self.Leaves]
        self._iter = {Tree : self._Reader[Tree].iterate(All, library = "np", step_size = self.StepSize) for Tree in self.Trees}
        self.Iter = {Tree : {key : [] for key in All} for Tree in self.Trees}
        return self

    def __next__(self):
        if sum([sum([len(self.Iter[Tree][br]) for br in self.Iter[Tree]]) for Tree in self.Trees]) == 0:
            self.Iter = {Tree : next(self._iter[Tree]) for Tree in self._iter}
            self.Iter = {Tree : {key : val.tolist() for key, val in zip(self.Iter[Tree], self.Iter[Tree].values())} for Tree in self.Iter}
        return {Tree : {key : val.pop() for key, val in zip(self.Iter[Tree], self.Iter[Tree].values())} for Tree in self.Iter}
