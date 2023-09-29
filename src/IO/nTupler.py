from AnalysisG.Generators.Interfaces import _Interface
from AnalysisG.Notification.nTupler import _nTupler
from AnalysisG.Tracer import SampleTracer
from AnalysisG.Tools import Hash, Threading
from typing import Union
import numpy as np
import uproot
import h5py

class container(SampleTracer):

    def __init__(self):
        self.Tree = None
        self.SelectionName = None
        self.Variable = None
        self.FilePath = None
        self._h5 = None
        self.Path = None

    def _strip(self, inpt):
        msg = "Syntax Error! Format is '<selection name> -> <variable> -> <key>' "
        msg += "If you want to get the entire object, use append the '->' to the tree "
        msg += "e.g. 'SelectionName ->  for the whole object to be returned'"
        if "->" not in inpt: return msg
        inpt = inpt.split("->")
        self.SelectionName = inpt.pop(0).strip(" ")
        self.Variable = inpt.pop(0).strip(" ")
        if len(inpt) == 0: return
        self.Path = "/".join(inpt)
        self.Path = self.Path.replace(" ", "")

    def hdf5(self):
        _h5 = h5py.File(self.FilePath, "r")
        try: self._h5 = _h5[self.SelectionName].attrs
        except KeyError: return True
        code_pth = "/".join(self.FilePath.split("/")[:-1]) + "/code/"
        self._rebuild_code(code_pth, self._h5["code"])

    def __eq__(self, other):
        x = self.SelectionName == other.SelectionName
        x *= self.FilePath == other.FilePath
        return x

    def __len__(self):
        return len(self._h5)

    def __iter__(self):
        self._it = iter(self._h5)
        return self

    def __next__(self):
        name = next(self._it)
        if name == "code": name = next(self._it)
        return self._h5[name]

    def get(self):
        return sum([self._decoder(i) for i in self])

class nTupler(_Interface, _nTupler):

    def __init__(self, inpt = None):
        self.Caller = "nTupler"
        self.Verbose = 3
        self.chnk = 1000
        self.Threads = 6
        self.Files = []
        self.__it = None
        self._it = None
        self._DumpThis = {}
        self._Container = []
        if inpt is None: return
        self.InputSelection(inpt)

    def __make_list__(self, inpt, key = None):
        if isinstance(inpt, dict): pass
        elif isinstance(inpt, list): return {key : inpt}
        else: return {key : [inpt]}

        x = {}
        for i in inpt:
            k = key + "/" + i if key is not None else i
            x.update(self.__make_list__(inpt[i], k))
        return x

    def __uproot__(self, out, sel, tree, filepath, output):
        _o = out if out is not None else "/".join(filepath.split("/")[:-1])
        _o = self.AddTrailing(_o, "/") + sel + ".root"
        output = {i.replace("/", "_") : np.array(output[i]) for i in output}

        try: x = uproot.create(_o)
        except OSError: x = uproot.update(_o)

        save = {}
        for i in output:
            spl = i.split("_")
            tr = tree + "_" + spl[0]
            if len(spl) == 1: k = spl[0]
            else: k = "_".join(spl[1:])
            l = output[i].size
            if l not in save: save[l] = {}
            if tr not in save[l]: save[l][tr] = {}
            save[l][tr].update({k : [np.float64, output[i]]})

        for l in save:
            for tr in save[l]:
                x.mktree(tr, {i : save[l][tr][i][0] for i in save[l][tr]})
                x[tr].extend({i : save[l][tr][i][1] for i in save[l][tr]})
        x.close()

    def Write(self, OutDir: Union[str, None] = None):
        contains = self.merged()
        self.output = {}
        for i in self._Container:
            sel = contains[i.SelectionName]
            var = i.Variable
            if sel.Tree != i.Tree: continue
            dct = self.__make_list__(sel.__dict__[var])
            sel = i.SelectionName
            if sel not in self.output:
                self.output[sel] = [OutDir, sel, i.Tree, i.FilePath, {}]

            if i.Path is not None:
                if i.Path not in dct:
                    self._KeyNotFound(var, i.Path, list(dct))
                    continue
                self.output[sel][-1].update({var + "/" + i.Path : dct[i.Path]})
            elif None in dct: self.output[sel][-1].update({var : dct[None]})
            else: self.output[sel][-1].update({var + "/" + i : dct[i] for i in dct})

        for i in self.output: self.__uproot__(*self.output[i])

    def __scrape__(self, file):
        for tree in self._DumpThis:
            for entry in self._DumpThis[tree]:
                self._Container.append(container())
                self._Container[-1].Tree = tree
                self._Container[-1].FilePath = file
                res = self._Container[-1]._strip(entry)
                skip = True
                if res is not None: self.Failure(res)
                else: skip = self._Container[-1].hdf5()
                if skip is True: del self._Container[-1]

    def __Dumps__(self):
        self._Container = []
        files = self.DictToList(self.Files)
        for file in files: self.__scrape__(file)
        if len(self._Container) == 0:
            self.Failure("No selection was found.")
            return
        found = [""]
        found += [i.SelectionName for i in self._Container]
        self.Success("Found Selections" + "\n -> ".join(set(found)))

    @staticmethod
    def function(inpt, _prgbar):
        lock, bar = _prgbar
        seed = inpt.pop(0)
        for i in inpt:
            seed += i
            with lock: bar.update(1)
        return [seed]

    def merged(self):
        o = {}
        for i in self:
            name = i.__class__.__name__
            if name not in o: o[name] = [i]
            else: o[name] += [i]

        for name in o:
            if self.Threads > 1:
                th = Threading(o[name], self.function, self.Threads, self.chnk)
                th.Start()
                o[name] = sum([i for i in th._lists if i is not None])
            else: o[name] = sum(o[name])
        return o

    def __iter__(self):
        self.__Dumps__()
        g = []
        for i in self._Container: g += [i] if i not in g else []
        self._it = iter(g)
        return self

    def __next__(self):
        try:
            if self.__it is None: raise StopIteration
            nxt = next(self.__it)
        except StopIteration:
            self._br = None
            self.__it = next(self._it)
            msg = "nTupler::" + self.__it.SelectionName + " -> " + self.__it.Variable
            _, self._br = self._MakeBar(len(self.__it), msg)
            self.__it = iter(self.__it)
            nxt = next(self.__it)

        self._br.update(1)
        return SampleTracer._decoder(nxt)
