from AnalysisG.Generators.Interfaces import _Interface
from AnalysisG._cmodules.MetaData import MetaData
from AnalysisG.Notification import _UpROOT
from uproot.exceptions import KeyInFileError
import uproot

class settings:
    def __init__(self):
        self.Verbose = 3
        self.StepSize = 1000
        self.EnablePyAMI = True
        self.Threads = 12
        self.Trees = []
        self.Branches = []
        self.Leaves = []
        self.Files = {}
        self.OnlyMeta = False
        self.metacache_path = "./"


class UpROOT(_UpROOT, settings, _Interface):
    def __init__(self, ROOTFiles=None, EventGenerator = None):
        settings.__init__(self)
        self.Caller = "UP-ROOT"
        if EventGenerator is None: self.InputSamples(ROOTFiles)
        else: self.Files = ROOTFiles
        ROOTFile = [i + "/" + k for i in self.Files for k in self.Files[i]]
        self.File = {i: None for i in ROOTFile}
        if not len(self.File): self.InvalidROOTFileInput()
        self.Keys = {}

        try: self.MetaData
        except AttributeError: self.MetaData = {}

    def __len__(self):
        if len(self.MetaData) == 0: self.ScanKeys()
        out = {}
        for x in self.MetaData:
            dc = self.MetaData[x].GetLengthTrees
            for key in dc:
                if key not in out: out[key] = 0
                out[key] += dc[key]
        return max(list(out.values())) if len(out) else 0

    def GetAmiMeta(self):
        if len(self.MetaData) == 0: self.ScanKeys()
        return self.MetaData

    def ScanKeys(self):
        def recursion(inpt, thiskey):
            try:
                lst = inpt[thiskey].keys()
                try: self._getthis["num"].append(inpt[thiskey].num_entries)
                except AttributeError: pass
            except KeyInFileError: return thiskey
            except TypeError: return thiskey
            except AttributeError: return thiskey
            for i in lst:
                key = thiskey + "/" + i
                self._getthis["keys"].append(recursion(inpt[key], key))

        if self.metacache_path is None: pass
        else: self.mkdir(self.metacache_path)

        for i in list(self.File):
            if i in self.MetaData: continue
            meta = MetaData(i, scan_ami = self.EnablePyAMI, metacache_path = self.metacache_path)
            self.MetaData[i] = meta
            self.MetaData[i].Trees = self.Trees
            self.MetaData[i].Branches = self.Branches
            self.MetaData[i].Leaves = self.Leaves
            if not meta.loaded and self.EnablePyAMI:
                self.NoVOMSAuth()
                self.FailedAMI()
                self.EnablePyAMI = False
            elif meta.loaded and self.EnablePyAMI:
                if meta.is_cached: key = i + " (cached)"
                else: key = i + " (fetched)"
                self.FoundMetaData(key, meta.dsid, meta.generators)
                if self.OnlyMeta: continue
            self.File[i] = uproot.open(i)

            for tr in self.File[i].keys():
                self._getthis = {"num" : [], "keys" : []}
                recursion(self.File[i], tr)
                if not len(self._getthis["num"]): continue
                meta.ProcessKeys(self._getthis)

            meta._findmissingkeys()
            self._missed = {
                    "Trees"   : meta.MissingTrees,
                    "Brances" : meta.MissingBranches,
                    "Leaves"  : meta.MissingLeaves
            }
            self.Keys[i] = {}
            self.Keys[i]["missed"] = self._missed
            self.CheckValidKeys(self.Trees, meta.Trees, "Trees")
            self.CheckValidKeys(self.Branches, meta.Branches, "Branches")
            self.CheckValidKeys(self.Leaves, meta.Leaves, "Leaves")
            self.AllKeysFound(i.split("/")[-1])

    def __iter__(self):
        if len(self.File) != len(self.MetaData): self.ScanKeys()
        meta = self.MetaData
        self.__root = {}
        self.__tracing = {}
        self.__index = {}

        for f in meta:
            gets = meta[f]._MakeGetter()
            tr_l = meta[f].GetLengthTrees
            meta[f].event_index = 0

            for tr in gets:
                if tr_l[tr]: pass
                else: continue

                if tr not in self.__root:
                    self.__root[tr] = {"files" : {}, "library" : "np", "step_size" : self.StepSize}
                    self.__root[tr].update({"how" : dict, "expressions" : []})
                    self.__tracing[tr] = []
                    self.__index[tr] = []

                self.__root[tr]["files"][f] = tr
                self.__root[tr]["expressions"] += gets[tr]

                self.__tracing[tr] += [f]
                self.__index[tr] += [tr_l[tr]]

        for tr in self.__root:
            self.__root[tr] = uproot.iterate(**self.__root[tr])
            self.__tracing[tr] = iter(self.__tracing[tr])
            self.__index[tr] = iter(self.__index[tr])
        self._event_index = 0
        self._trk = {}
        self._c = {}
        return self

    def __next__(self):
        if not len(self.__index): raise StopIteration

        trees = [] if len(self._c) else list(self.__root)
        for tr in trees:
            try: dc = next(self.__root[tr])
            except StopIteration: continue

            dc = {key : c.tolist() for key, c in dc.items() if c.size > 0}
            keys = {tr + "/" + key : c for key, c in dc.items()}
            self._c.update(keys)

        self._c  = {keys : c for keys, c in self._c.items() if len(c) > 0}
        if not len(self._c) and len(trees): raise StopIteration

        out = {keys : c.pop(0) for keys, c in self._c.items()}
        if not len(out): return self.__next__()

        msg = ""
        index = [tr for tr, x in self._trk.items() if x[1] > self._event_index]
        for tr in self.__root:
            if len(index) != 0: break
            self._event_index = 0
            try: file, indx = next(self.__tracing[tr]), next(self.__index[tr])
            except StopIteration: continue
            self._trk[tr] = (file, indx)
            msg += tr + " -> " + str(self._trk[tr][1]) + ", "
        if not len(index): self.Success("READING -> " + self._trk[tr][0] + " (Trees: " + msg[:-2] + ")")
        for tr in self._trk:
            file = self._trk[tr][0]
            out["MetaData"] = self.MetaData[file]
            out["ROOT"] = file
            out["EventIndex"] = self._event_index
        self._event_index += 1
        self.MetaData[file].event_index =+ 1
        return out
