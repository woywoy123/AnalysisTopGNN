from AnalysisG.Tools.IO import IO


class Tools(IO):
    def __init__(self):
        IO.__init__(self)

    def MergeListsInDict(self, inpt):
        if isinstance(inpt, list):
            return inpt

        out = []
        for i in inpt:
            out += self.MergeListsInDict(inpt[i])
        return self.MergeNestedList(out)

    def DictToList(self, inpt, key=None):
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
        return True

    def AddListToDict(self, Dict, key):
        if key not in Dict:
            Dict[key] = []
            return False
        return True

    def Quantize(self, inpt, size):
        for i in range(0, len(inpt), size):
            yield inpt[i : i + size]

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
            out = {}
            for i in set(l1 + l2):
                if isinstance(ob1[i] if i in l1 else ob2[i], dict):
                    ob1[i] = {} if i not in l1 else ob1[i]
                    ob2[i] = {} if i not in l2 else ob2[i]
                    out[i] = self.MergeData(ob1[i], ob2[i])
                elif isinstance(ob1[i] if i in l1 else ob2[i], list):
                    ob1[i] = [] if i not in l1 else ob1[i]
                    ob2[i] = [] if i not in l2 else ob2[i]
                    out[i] = self.MergeData(ob1[i], ob2[i])
                else:
                    o = ob1[i] + ob2[i] if i in ob1 and i in ob2 else None
                    if o == None:
                        o = ob1[i] if o == None and i in ob1 else o
                        o = ob2[i] if o == None and i in ob2 else o
                    out[i] = o
            return out
        if isinstance(ob1, list) and isinstance(ob2, list):
            l1, l2 = len(ob1), len(ob2)
            out = []
            for i in range(l1 if l1 > l2 else l2):
                if isinstance(ob1[i] if i >= l2 else ob2[i], dict):
                    out.append(self.MergeData(ob1[i], ob2[i]))
                if isinstance(ob1[i] if i >= l2 else ob2[i], list):
                    out.append(
                        self.MergeData(
                            ob1[i] if l1 > i else [], ob2[i] if l2 > i else []
                        )
                    )
                else:
                    return ob1 + ob2
            return out

        if isinstance(ob1, int) and isinstance(ob2, int):
            return ob1 + ob2
        if isinstance(ob1, float) and isinstance(ob2, float):
            return ob1 + ob2
