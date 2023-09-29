from AnalysisG.Generators.Interfaces import _Interface
from AnalysisG.Notification import _UpROOT
from AnalysisG.Settings import Settings
from uproot.exceptions import KeyInFileError
import signal
import uproot
import json
import warnings

try:
    import pyAMI.client
    import pyAMI.atlas.api as atlas
except ModuleNotFoundError:
    pass


class MetaData(object):
    def __init__(self):
        self._vars = {
            "version": "version",
            "DatasetName": "logicalDatasetName",
            "nFiles": "nFiles",
            "total_events": "totalEvents",
            "cross_section": "crossSection",
            "generator_tune": "generatorTune",
            "keywords": "keywords",
            "subcampaign": "subcampaign",
            "short": "physicsShort",
            "isMC": "isMC",
            "Files": "inputFiles",
            "DAOD": "DAOD",
            "eventNumber": "eventNumber",
        }
        self._index = {}
        self.thisDAOD = ""
        self.thisSet = ""
        self.ROOTName = ""
        self.init = False

    def add(self, data):
        for i in self._vars:
            key = self._vars[i]
            if key not in data: continue
            setattr(self, i, data[key])

    def MakeIndex(self):
        try:
            next(iter(self.DAOD))
            next(iter(self.Files))
            next(iter(self.eventNumber))
        except StopIteration:
            return

        _nevents = 0
        _index = {}
        for i in self.Files:
            fname, ix = i[0].split("/")[-1], i[1]
            if fname not in self.DAOD:
                _nevents += ix
                continue
            if fname.endswith(".1"):
                fname = fname[:-2]
            _index |= {
                self.eventNumber[idx]: fname for idx in range(_nevents, _nevents + ix)
            }
            _nevents += ix
        self._index = _index
        self.init = True
        self.Files = [f[0] for f in self.Files]

    def GetDAOD(self, val):
        try:
            self.thisDAOD = self._index[val]
            self.thisSet = self.DatasetName
        except KeyError: pass
        return (self.thisDAOD, self.thisSet)

    def MatchROOTName(self, val):
        if self.thisSet not in val: return False
        try:
            for i in self.inputFiles:
                if i not in val: continue
                return True
            return False
        except: return self.thisDAOD in val


class AMI:
    def __init__(self):
        self.cfg = True
        self._client = None
        try: self.init()
        except: self.cfg = False

    def init(self):
        warnings.filterwarnings("ignore")
        self._client = pyAMI.client.Client("atlas")

    def search(self, pattern, amitag=False):
        def _sig(signum, frame): return ""

        if self._client is None: return {}
        signal.signal(signal.SIGALRM, _sig)
        signal.alarm(10)
        warnings.filterwarnings("ignore")
        try:
            res = atlas.list_datasets(
                self._client, dataset_number=[pattern], type="DAOD_TOPQ1"
            )
        except: return False

        if len(res) == 0: return {}
        warnings.filterwarnings("ignore")
        try:
            if amitag:
                tags = set(amitag.split("_"))
                name = []
                for i in res:
                    l = [t for t in tags if t in i["ldn"]]
                    if len(l) != len(tags): continue
                    name += [i["ldn"]]
                if len(name) == 0: pass
                else: res = name[0]
            else: res = res[0]["ldn"]
            out = dict(atlas.get_dataset_info(self._client, res)[0])
            this = atlas.list_files(self._client, out["logicalDatasetName"])
            this = [ i["LFN"] for i in this ]
            out.update({"DAOD": this})
            return out
        except: return {}


class UpROOT(_UpROOT, Settings, _Interface):
    def __init__(self, ROOTFiles=None):
        self.Caller = "Up-ROOT"
        Settings.__init__(self)
        self.InputSamples(ROOTFiles)
        ROOTFile = [i + "/" + k for i in self.Files for k in self.Files[i]]
        self.File = {i: uproot.open(i) for i in ROOTFile}
        if len(self.File) == 0:
            self.InvalidROOTFileInput()
            self.File = False
            return
        self.Keys = {}
        self.MetaData = {}
        self._dsid_meta = {}
        self._it = False

    def _StartIter(self):
        if self._it: return
        self._it = iter(list(self.File))

    def ScanKeys(self):
        if not self.File: return False

        def Recursion(inpt, k_, keys):
            for i in keys:
                k__ = k_ + "/" + i
                try:
                    k_n = inpt[k__].keys()
                    self._struct[k__] = None
                except AttributeError: continue
                try: Recursion(inpt, k__, k_n)
                except RecursionError: continue
        self._StartIter()
        try: fname = next(self._it)
        except StopIteration:
            self._it = False
            return

        f = self.File[fname]
        self._struct = {}
        self._missed = {"TREE": [], "BRANCH": [], "LEAF": []}

        Recursion(f, "", f.keys())
        found = {}
        for i in self.Trees:
            found.update({k: self._struct[k] for k in self._struct if i in k})
        self.CheckValidKeys(self.Trees, found, "TREE")
        found = {}

        for i in self.Branches:
            found.update(
                {k: self._struct[k] for k in self._struct if i in k.split("/")}
            )
        self.CheckValidKeys(self.Branches, found, "BRANCH")

        for i in self.Leaves:
            found.update(
                {k: self._struct[k] for k in self._struct if i in k.split("/")}
            )
        self.CheckValidKeys(self.Leaves, found, "LEAF")
        self.Keys[fname] = {"found": found, "missed": self._missed}
        self.AllKeysFound(fname)

        self.ScanKeys()

    def GetAmiMeta(self):
        meta = {}
        ami = AMI()
        if not ami.cfg: self.FailedAMI()
        for i in self.File:
            command = {
                    "files" : i + ":sumWeights",
                    "expressions" : ["dsid", "AMITag", "generators"], 
                    "how" : dict, 
                    "library" : "np"
            }
            try: data = [k for k in uproot.iterate(**command)]
            except KeyInFileError: data = []
            data = {} if len(data) == 0 else data[0]
            command["files"] = i + ":AnalysisTracking"
            command["expressions"] = ["jsonData"]
            command["step_size"] = 100

            try: tracker = [k for k in uproot.iterate(**command)]
            except KeyInFileError: tracker = []
            tracker = "" if len(tracker) == 0 else tracker[0]["jsonData"].tolist()[0]
            tracker = "\n".join(
                        [ k for k in tracker.split("\n") if "BtagCDIPath" not in k ]
                    ) # Some files have a weird missing ","
            if len(tracker) != 0: tracker = json.loads(tracker)
            lst = ["inputConfig", "inputFiles", "configSettings"]
            data.update({ i : tracker[i] for i in lst if i in tracker })

            command["files"] = i + ":truth"
            command["expressions"] = ["eventNumber"]
            del command["step_size"]

            try: evnt = [k for k in uproot.iterate(**command)]
            except KeyInFileError: evnt = []
            if len(evnt) == 0: pass
            else: evnt = evnt[0]
            x = "eventNumber"
            if x in evnt: data[x] = evnt[x].tolist()

            meta[i] = MetaData()
            if self.DisablePyAMI: continue
            if "dsid" not in data: continue
            dsid = str(data["dsid"].tolist()[0])
            if "generators" in data:
                gen = data["generators"]
                gen = gen.tolist()[0]
                get = gen.replace("+", "")
            else: gen = False

            if "AMITag" in data: tag = data["AMITag"].tolist()[0]
            else: tag = False
            if tag: _tags = dsid + "-" + ".".join(set(tag.split("_")))
            else: _tags = dsid

            meta[i].add(data["inputConfig"])
            meta[i].add(data)
            meta[i]._vars.update(data["configSettings"])
            meta[i].add(data["configSettings"])
            if i in self.MetaData: continue
            if not ami.cfg: continue
            if _tags not in self._dsid_meta:
                self._dsid_meta[_tags] = ami.search(dsid, tag)
            if self._dsid_meta[_tags] == False:
                ami.cfg = False
                self.NoVOMSAuth()
                continue
            elif len(self._dsid_meta[_tags]) == 0:
                continue
            self.FoundMetaData(i, _tags, gen)
            meta[i].add(self._dsid_meta[_tags])
            meta[i].MakeIndex()

        self.MetaData.update(meta)
        return self.MetaData

    def __len__(self):
        self.__iter__()
        v = {
            tr: sum([uproot.open(r + ":" + tr).num_entries for r in self._t[tr]])
            for tr in self._get
        }
        return max(list(v.values()))

    def __iter__(self):
        if len(self.Keys) != len(self.File): self.ScanKeys()
        keys = self.Keys[list(self.File)[0]]["found"]
        self._t = {}
        self._get = {}
        self.GetAmiMeta()
        tr = []
        tmp = [j for z in keys for j in z.split("/")]
        for i in self.Trees:
            for k in tmp: tr += [k] if i in k else []

        for T in set(tr):
            for r in self.File:
                if T in self.Keys[r]["missed"]["TREE"]: continue
                if T not in self._t: self._t[T] = []
                self._t[T] += [r]
                self._get[T] = [i.split("/")[-1] for i in keys if T in i]

        dct = {
            tr: {
                "files": {r: tr for r in self._t[tr]},
                "library": "np",
                "step_size": self.StepSize,
                "report": True,
                "how": dict,
                "expressions": self._get[tr],
            }
            for tr in self._get
        }
        self._root = {tr.split(";")[0]: uproot.iterate(**dct[tr]) for tr in dct}
        self._r = {}
        self._tracking = {}
        self._curr = (None, None)
        self._EventIndex = 0
        return self

    def __next__(self):
        if len(self._root) == 0: raise StopIteration
        if len(self._r) == 0:
            r = {tr : next(self._root[tr]) for tr in self._root}
            for tree in r:
                val = r[tree][0]
                val = { tree + "/" + key : val[key].tolist() for key in val}
                self._r.update(val)
                self._tracking[tree] = r[tree][1]

        r = {}
        for key in self._r:
            if len(self._r[key]) == 0: continue
            tr = key.split("/")[0]
            r[key] = self._r[key].pop(0)

        if len(r) == 0:
            self._r = r
            return self.__next__()

        self._EventIndex += 1
        fname_p = self._tracking[tr].file_path
        meta, _fname = self._curr
        r.update(
            { "MetaData" : meta, "ROOT" : _fname, "EventIndex" : self._EventIndex}
        )

        if _fname == fname_p: return r
        self._EventIndex = 0
        x = {tr: uproot.open(fname_p + ":" + tr).num_entries for tr in self._tracking}
        x = " ".join([tr + " - " + str(x[tr]) for tr in x])
        fname_n = fname_p.split("/")[-1]
        self.Success("READING -> " + fname_n + " (Trees: " + x + ")")
        meta = self.MetaData[fname_p]
        meta.thisDAOD = fname_n
        meta.ROOTName = fname_p
        meta.thisSet  = "/".join(fname_p.split("/")[:-1])
        self._curr = (meta, fname_p)
        r.update(
            { "MetaData" : meta, "ROOT" : fname_p, "EventIndex" : self._EventIndex}
        )
        return r
