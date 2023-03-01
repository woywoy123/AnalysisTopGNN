from .Miscellaneous import *
from AnalysisTopGNN.Tools.IO import IO

class Tools(IO):

    def __init__(self):
        IO.__init__(self)
    
    def GetSourceCode(self, obj):
        return GetSourceCode(obj)
    
    def GetObjectFromString(self, module, name):
        return StringToObject(module, name)
    
    def GetSourceFile(self, obj):
        return GetSourceFile(obj)

    def GetSourceFileDirectory(self, obj):
        return GetSourceFileDirectory(obj)

    def MergeListsInDict(self, inpt):
        if isinstance(inpt, list):
            return inpt

        out = []
        for i in inpt:
            out += self.MergeListsInDict(inpt[i])
        return self.MergeNestedList(out)
    
    def DictToList(self, inpt, key = None):
        if isinstance(inpt, str) and key != None:
            return key + "/" + inpt
        if isinstance(inpt, list) and key != None:
            return [self.DictToList(i, key) for i in inpt]
        if isinstance(inpt, dict) and key != None:
            return [self.DictToList(inpt[i], i) for i in inpt]
        if key == None: 
            out = []
            for i in inpt:
                out += self.DictToList(inpt[i], i)
            return out 
        
    def AddDictToDict(self, Dict, key):
        if key not in Dict:
            Dict[key] = {}
            return False
        else:
            return True
    
    def AddListToDict(self, Dict, key):
        if key not in Dict:
            Dict[key] = []
            return False
        else:
            return True

    def MergeNestedList(self, inpt):
        if isinstance(inpt, list) == False:
            return [inpt]

        out = []
        for i in inpt:
            out += self.MergeNestedList(i)
        return out
    
    def MergeData(self, ob2, ob1):
        if isinstance(ob1, dict) and isinstance(ob2, dict):
            l1, l2 = list(ob1), list(ob2)
            out= {}
            for i in set(l1 + l2):
                if isinstance(ob1[i] if i in l1 else ob2[i], dict):
                    out[i] = self.MergeData(ob1[i], ob2[i])
                elif isinstance(ob1[i] if i in l1 else ob2[i], list):
                    out[i] = self.MergeData(ob1[i], ob2[i])
                else:
                    out[i] = ob1[i] + ob2[i]
            return out
        if isinstance(ob1, list) and isinstance(ob2, list):
            l1, l2 = len(ob1), len(ob2)
            out = []
            for i in range(l1 if l1 > l2 else l2):
                if isinstance(ob1[i] if i >= l2 else ob2[i], dict):
                    out[i] = self.MergeData(ob1[i], ob2[i])
                if isinstance(ob1[i] if i >= l2 else ob2[i], list):
                    out[i] = self.MergeData(ob1[i], ob2[i])
                else: 
                    return ob1 + ob2
            return out

