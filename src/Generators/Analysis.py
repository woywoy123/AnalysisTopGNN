from AnalysisTopGNN.IO import HDF5, Pickle, PickleObject, UnpickleObject
from AnalysisTopGNN.Samples import SampleTracer
from AnalysisTopGNN.Notification import Analysis_
from AnalysisTopGNN.Tools import Tools
from AnalysisTopGNN.Tools import Threading

from AnalysisTopGNN.Generators.GraphGenerator import GraphFeatures
from AnalysisTopGNN.Generators import EventGenerator, GraphGenerator, Settings
from AnalysisTopGNN.Generators import ModelEvaluator
from AnalysisTopGNN.Generators import Optimization
from AnalysisTopGNN.Templates import Selection

class Interface:

    def __init__(self):
        pass

    def InputSample(self, Name, SampleDirectory = None):
        if self._launch == False:
            self._InputValues.append({"INPUTSAMPLE" : {"Name" : Name, "SampleDirectory" : SampleDirectory}})
            return  

        if isinstance(SampleDirectory, str):
            if SampleDirectory.endswith(".root"):
                SampleDirectory = {"/".join(SampleDirectory.split("/")[:-1]) : SampleDirectory.split("/")[-1]}
            else:
                SampleDirectory = [SampleDirectory] 
        
        if self.AddDictToDict(self._SampleMap, Name) or SampleDirectory == None:
            root = self.OutputDirectory + "/" + self.ProjectName + "/Tracers/"
            tracers = { root + i + "/" + Name : "*" for i in ["DataCache", "EventCache"]}
            tracers = self.ListFilesInDir(tracers, ".pkl")
            if sum([len(i) for i in tracers.values()]) == 0:
                return 
            for t in [UnpickleObject(i + "/" + j) for i in tracers for j in tracers[i]]:
                self.SampleContainer += t

            for i in self.SampleContainer.ROOTFiles:
                directory = "/".join(i.split("/")[:-1])
                self.AddListToDict(self._SampleMap[Name], directory)
                self._SampleMap[Name][directory].append(i.split("/")[-1])
            self.ResetSampleContainer()
            return 

        if isinstance(SampleDirectory, dict):
            self._SampleMap[Name] |= self.ListFilesInDir(SampleDirectory, ".root")
            return 
        self._SampleMap[Name] |= self.ListFilesInDir({i : "*" for i in SampleDirectory}, ".root")
        
        for i in self._SampleMap:
            self.NoSamples(self._SampleMap[i], i)


    def EvaluateModel(self, Directory, ModelInstance = None, BatchSize = None):
        
        Directory = self.abs(self.AddTrailing(Directory, "/"))
        if self._launch == False:
            self._InputValues.append({"EVALUATEMODEL" : {"Directory": Directory, "ModelInstance" : ModelInstance, "BatchSize": BatchSize}})
            return  

        Name = Directory.split("/")[-1]
        if Name in self._ModelDirectories:
            self.ModelNameAlreadyPresent(Name)
            return 

        if len(self.ls(Directory)) == 0:
            self.InvalidOrEmptyModelDirectory()
            return 

        self._ModelDirectories[Name] = [self.abs(Directory + "/" + i) for i in self.ls(Directory) if "Epoch-" in i]
        self._ModelSaves[Name] = {"ModelInstance": ModelInstance} 
        self._ModelSaves[Name] |= {"BatchSize" : BatchSize}

    def AddSelection(self, Name, inpt):
        if "__name__" in inpt.__dict__:
            inpt = inpt()

        if self._launch == False:
            self._InputValues.append({"ADDSELECTION" : {"Name" : Name, "inpt" : inpt}})
            return 

        self._Selection[Name] = inpt
        self.AddedSelection(Name)
    
    def MergeSelection(self, Name):
        if self._launch == False:
            self._InputValues.append({"MERGESELECTION" : {"Name" : Name}})
            return 
        self._MSelection[Name] = True


class Analysis(Interface, Analysis_, Settings, SampleTracer, GraphFeatures, Tools):

    def __init__(self):
        Interface.__init__(self)
        self.Caller = "ANALYSIS"
        Settings.__init__(self) 
        SampleTracer.__init__(self)
    
    @property
    def _TempDisableCache(self):
        self.__Cache = (self.DumpPickle, self.DumpHDF5)
        self.DumpPickle, self.DumpHDF5 = False, False
    
    @property
    def _TempEnableCache(self):
        self.DumpPickle, self.DumpHDF5 = self.__Cache 

    def __BuildRootStructure(self): 
        self.OutputDirectory = self.RemoveTrailing(self.OutputDirectory, "/")
        if self._tmp:
            return 
        self._tmp = self.pwd()
        if (self.DumpPickle or self.DumpHDF5) or self.TrainingSampleName or (len(self._MSelection) > 0 or len(self._Selection) > 0):
            self.mkdir(self.OutputDirectory + "/" + self.ProjectName)
            self.output = self.OutputDirectory + "/" + self.ProjectName
            self.cd(self.output)
        self.output = "." 

    def __GenerateEvents(self, InptMap, name):
        
        rem = []
        reE = self.__SearchAssets("EventCache", name) if self.EventCache else None
        rem += [f for f in self.DictToList(InptMap) if f not in self or reE == False] if self.EventCache else []
        
        reD = self.__SearchAssets("DataCache", name) if self.DataCache else None
        rem += [f for f in self.DictToList(InptMap) if f in self or reD == False] if self.DataCache else []
        if len(rem) == 0:
            return 
        
        _r = ""
        for f in set(rem):
            tmp = f.split("/")
            _r = self.ReadingFileDirectory(tmp[-2]) if _r != tmp[-2] else _r
           
            if self.EventCache and f not in self or reE == False:
                if self.Event == None:
                    self.NoEventImplementation()
                    continue
                self += self.__EventGenerator(name, tmp)
            
            if self.DataCache:
                if reE == None and reD == False and self.EventCache == False:
                    self.EventCache = True 
                    self.__SearchAssets("EventCache", name)
                    self.EventCache = False
                
                if reD == False and self.EventCache == False and f not in self:
                    self._TempDisableCache
                    self += self.__EventGenerator(name, tmp)
                    self._TempEnableCache

                if self.EventGraph == None:
                    self.NoEventGraphImplementation()
                    continue

                if f not in self or reD == False:
                    self += self.__GraphGenerator(name, tmp)
            

    def __EventGenerator(self, name, filedir):
        ev = EventGenerator()
        ev.Caller = self.Caller
        ev.RestoreSettings(self.DumpSettings())
        ev.InputDirectory = {"/".join(filedir[:-1]) : filedir[-1]}
        ev.SpawnEvents()
        self.GetCode(ev)
        if self.EventCache:
            self.__DumpCache(ev, name, filedir[-1], False)
        return ev 

    def __GraphGenerator(self, name, filedir):

        direc = "/".join(filedir)
        gr = GraphGenerator()
        gr.SampleContainer.ROOTFiles[direc] = self.GetROOTContainer(direc)
        gr.RestoreSettings(self.DumpSettings())
        gr.CompileEventGraph()
        self.GetCode(gr)
        if self.DataCache:
            self.__DumpCache(gr, name, filedir[-1], True)
        return gr
    
    def __DumpCache(self, instance, name, fdir, Compiled):
        def QuickExportEvent(inpt, _prgbar):
            lock, bar = _prgbar
            out = []
            for i in inpt:
                if i not in self:
                    out.append([i, True])
                elif self[i] != "":
                    out.append([i, True])
                else:
                    out.append([i, False])
                with lock:
                    bar.update(1)
            return out
        
        if self.DumpHDF5 == False and self.DumpPickle == False:
            return 
        if Compiled == False:
            th = Threading([ev.Filename for ev in instance], QuickExportEvent, self.Threads, self.chnk)
            th.Title = "QUICKSEARCHEVENT"
            th.Start()
            instance.SampleContainer.dict()
            export = {hsh : instance.SampleContainer._Hashes[hsh] for hsh, ev in th._lists if ev}
            del th
        else:
            lst = [i.split(".")[0] for i in self.ls(self.output + "/DataCache/" + name + "/" + fdir + "/")]
            export = {ev.Filename : ev for ev in instance if ev.Filename not in lst}
        if len(export) == 0:
            return 
        out = self.output + "/Tracers/"
        out += "DataCache/" if Compiled else "EventCache/"
        out += name + "/" + fdir
        PickleObject(instance.SampleContainer.ClearEvents(), out) 

        out = self.output + "/"
        out += "DataCache/" if Compiled else "EventCache/"
        out += name + "/" + fdir 
        self.mkdir(out)
        if self.DumpHDF5:
            hdf = HDF5()
            hdf.RestoreSettings(self.DumpSettings())
            hdf.MultiThreadedDump(export, out)
        
        if self.DumpPickle:
            pkl = Pickle()
            pkl.RestoreSettings(self.DumpSettings())
            pkl.PickleObject([ i._File for i in self._Code ], "ClassDef", out)
            pkl.MultiThreadedDump(export, out)

    def __GenerateTrainingSample(self):
        def MarkSample(smpl, status):
            for i in smpl:
                obj = self[i]
                obj.Train = status
       
        if not self.TrainingSampleName:
            return 
       
        search = False
        search = "EventCache" if self.EventCache else search
        search = "DataCache" if self.DataCache else search
        if search == False and self.TrainingSampleName: 
            self.CantGenerateTrainingSample()

        self.EmptySampleList()
        if self.Training == False:
            self.CheckPercentage()
            inpt = {i.Filename : i for i in self}
            hashes = self.MakeTrainingSample(inpt, self.TrainingPercentage)
            
            hashes["train_hashes"] = {hsh : self.HashToROOT(hsh) for hsh in hashes["train_hashes"]}
            hashes["test_hashes"] = {hsh : self.HashToROOT(hsh) for hsh in hashes["test_hashes"]}
            hashes["SampleMap"] = self._SampleMap
            Name = self.TrainingSampleName if self.TrainingSampleName else "UNTITLED"
            PickleObject(hashes, self.output + "/Tracers/TrainingSample/" + Name)
            self.Training = hashes

        MarkSample(self.Training["train_hashes"], True)
        MarkSample(self.Training["test_hashes"], False)

    def __Optimization(self):
        if self.Model == None:
            return
        op = Optimization()
        op += self
        self.cd(self._tmp)
        op.RestoreSettings(self.DumpSettings())
        op.Launch()
        self.GetCode(op)
        self.cd(self._tmp)

    def __ModelEvaluator(self):
        if len(self._ModelDirectories) == 0 and self.PlotNodeStatistics == False:
            return 
        me = ModelEvaluator()
        me += self
        me.RestoreSettings(self.DumpSettings())
        me.Compile()

    def __SearchAssets(self, CacheType, Name):
        def function(tracers, _prgbar):
            out = []
            lock, bar = _prgbar
            for i in tracers:
                if self.IsFile(i) == False:
                    out.append([i, False])
                else:
                    out.append([i, UnpickleObject(i)])
                with lock:
                    bar.update(1)
            return out

        if isinstance(Name, list):
            for i in Name:
                self.__SearchAssets(CacheType, i)
            return 
        
        tr = self.output + "/Tracers/" + CacheType + "/" + Name
        smpls = self.output + "/" + CacheType + "/" + Name
        tracers = set([ tr + "/" + i + ".pkl" for i in self.ls(smpls) ] + [ tr + "/" + i  for i in self.ls(tr) ])
        samples = set([ smpls + "/" + i for i in self.ls(smpls) ] + [ smpls + "/" + i.replace(".pkl", "")  for i in self.ls(tr) ])
        if len(tracers) == 0:
            return False
        th = Threading([i for i in tracers if i.split("/")[-1].replace(".pkl", "") not in self], function, self.Threads, int(len(tr)/self.chnk)+1) 
        th.Title = "READING TRACERS - " + CacheType + " - " + Name
        th.VerboseLevel = self.VerboseLevel
        th.Start()
        for i in th._lists:
            if i[1] == False:
                self.MissingTracer(i[0])
                continue
            self.SampleContainer += i[1] 

        _pkl = self.DictToList(self.ListFilesInDir({i : "*" for i in samples}, ".pkl"))
        if len(_pkl) != 0:
            if len(_pkl) <= 1:
                return False
            pkl = Pickle()
            pkl.Caller = self.Caller
            pkl.VerboseLevel = 0
            pkl.Threads = self.Threads
            events = pkl.MultiThreadedReading(_pkl, Name)
            self.SampleContainer.RestoreEvents(events, self.Threads, self.chnk)
            return True

        _hdf = self.DictToList(self.ListFilesInDir({i : "*" for i in samples}, ".hdf5"))
        if len(_hdf) != 0:
            hdf = HDF5()
            hdf.Caller = self.Caller
            hdf.VerboseLevel = 0
            hdf.MultiThreadedReading(_hdf)
            events = {_hash : ev for _hash, ev in hdf._names}
            self.SampleContainer.RestoreEvents(events, self.Threads, self.chnk)
            return True 
        else:
            self.NoCache(root)
            return False

    def __Selection(self):
        def _select(inpt):
            out = []
            for k in inpt:
                tmp = k[0]()
                tmp._OutDir = self.output + "/Selections/" + k[2]
                tmp._EventPreprocessing(k[1])
                out.append(tmp)
            return out 
        
        def _rebuild(inpt):
            out = None
            for k in inpt:
                t = pkl.UnpickleObject(k)
                self.rm(k)
                
                t = Selection().RestoreSettings(t)
                out = t if out == None else out + t
            return [out]

        if len(self._Selection) > 0:
            pass 
        elif len(self._MSelection) > 0:
            pass
        else:
            return 
        
        pkl = Pickle()
        pkl.Caller = self.Caller
        pkl.VerboseLevel = 0

        s = self.list()
        for i in self._Selection:
            self.mkdir(self.output + "/Selections/" + i)
            th = Threading([[self._Selection[i], k, i] for k in s], _select, self.Threads, self.chnk)
            th.Title = "EXECUTING SELECTION (" + i + ")"
            th.VerboseLevel = self.VerboseLevel
            th.Start()
        
        for i in self._MSelection:
            l = [self.output + "/Selections/" + i + "/" + k for k in self.ls(self.output + "/Selections/" + i)]
            th = Threading(l, _rebuild, self.Threads, self.chnk)
            th.Title = "MERGING SELECTION (" + i + ")"
            th.VerboseLevel = self.VerboseLevel
            th.Start()
            pkl.PickleObject(sum([k for k in th._lists if k != None]), i, self.output + "/Selections/Merged/")
   
    def Launch(self):
        self.__CheckSettings()
        self._launch = True 
        for i in self._InputValues:
            name = list(i)[0]
            if name == "INPUTSAMPLE":
                self.InputSample(**i[name])
            elif name == "EVALUATEMODEL":
                self.EvaluateModel(**i[name])
            elif name == "ADDSELECTION": 
                self.AddSelection(**i[name])
            elif name == "MERGESELECTION": 
                self.MergeSelection(**i[name])
        self.StartingAnalysis()
        self.__BuildRootStructure()
        
        self.Training = False
        if self.TrainingSampleName:
            fDir = self.output + "/Tracers/TrainingSample/" + self.TrainingSampleName + ".pkl" 
            self.Training = UnpickleObject(fDir) if self.IsFile(fDir) else False
            self._SampleMap = self.Training["SampleMap"] if self.Training else self._SampleMap

        if self.Model != None:
            self.DataCache = True 
        if len(self._ModelDirectories) != 0 or self.PlotNodeStatistics:
            self.DataCache = True 
        self.EventImplementationCommit() 
        
        for i in self._SampleMap:
            self.__GenerateEvents(self._SampleMap[i], i)

        self.__GenerateTrainingSample()
        self.__Optimization() 
        self.__ModelEvaluator()
        self.__Selection()

        self.WhiteSpace()
        self.output = self.pwd()
        self.cd(self._tmp)
        self._tmp = False

    def __iter__(self):
        if self.SampleContainer._locked or self._launch == False:
            ec = self.ls(self.output + "/EventCache")
            dc = self.ls(self.output + "/DataCache")
            if len(self._SampleMap) != 0:
                ec = [i for i in self._SampleMap if i in ec]
                dc = [i for i in self._SampleMap if i in dc]
            
            trig = False
            if self.EventCache and len(ec) != 0:
                typ, dx = "EventCache", ec
                trig = True
            if self.DataCache and len(dc) != 0:
                typ, dx = "DataCache", dc
                trig = True
            if trig == False:
                typ, dx = ("DataCache", dc) if len(dc) > len(ec) else ("EventCache", ec)
            self.__SearchAssets(typ, dx)
        
        self._lst = [i for i in self.SampleContainer.list() if i != ""]
        if len(self._lst) == 0:
            self.NothingToIterate()
            return self

        if self.Tree == None:
            self.Tree = list(self._lst[0].Trees)[0]
        self.Lumi = 0
        return self

    def __next__(self):
        if len(self._lst) == 0:
            raise StopIteration()
        evnt = self._lst.pop(0)
        self.Lumi += float(evnt.Trees[self.Tree].Lumi)
        return evnt
