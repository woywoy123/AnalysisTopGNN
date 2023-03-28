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
                SampleDirectory = {"/".join(SampleDirectory.split("/")[:-1]) : [SampleDirectory.split("/")[-1]]}
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
    
    def __BuildRootStructure(self): 
        self.OutputDirectory = self.RemoveTrailing(self.OutputDirectory, "/")
        if self._tmp:
            return 
        self._tmp = self.pwd()
        if (self.DumpPickle or self.DumpHDF5) or self.TrainingSampleName or (len(self._MSelection) > 0 or len(self._Selection) > 0):
            self.mkdir(self.OutputDirectory + "/" + self.ProjectName)
            self.cd(self.OutputDirectory)
        self.output = self.ProjectName

    def __GenerateEvents(self, InptMap, name):
       
        rem = []
        reE, reD = False, False
        if self.EventCache:
            reE = self.__SearchAssets("EventCache", name)
        
        if self.DataCache:
            reD = self.__SearchAssets("DataCache", name)
        
        if self.EventCache and reE == False and self.DumpPickle == False and self.DumpHDF5 == False:
            self.DumpPickle = True
        if self.DataCache and reD == False and self.DumpPickle == False and self.DumpHDF5 == False:
            self.DumpPickle = True
   
        if self.NoSamples(InptMap, name):
            return 

        files = self.DictToList(InptMap)
        it = iter(files)
        _r = ""
        while True:
            f = next(it)
            tmp = f.split("/")
            if f not in self:
                _r = self.ReadingFileDirectory(tmp[-2]) if _r != tmp[-2] else _r
            
            if self.Event != None and f not in self:
                self.SampleContainer += self.__EventGenerator(name, tmp).SampleContainer
            
            if self.EventGraph != None and reD == False:
                if f not in self:
                    self.__SearchAssets("EventCache", name)
                if f not in self:
                    if self.Event == None:
                        self.NoEventImplementation()
                        continue
                    self.SampleContainer += self.__EventGenerator(name, tmp).SampleContainer
                if self.EventGraph == None:
                    self.NoEventImplementation()
                    continue
                self.SampleContainer += self.__GraphGenerator(name, tmp).SampleContainer

            if files[-1] == f:
                break

        if (self.DumpPickle or self.DumpHDF5) and self.Model == None:
            self.ResetSampleContainer()

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

        tr = self.output + "/Tracers/" + CacheType + "/" + Name
        smpls = self.output + "/" + CacheType + "/" + Name
        tracers = set([ tr + "/" + i + ".pkl" for i in self.ls(smpls) ] + [ tr + "/" + i  for i in self.ls(tr) ])
        samples = set([ smpls + "/" + i for i in self.ls(smpls) ] + [ smpls + "/" + i.replace(".pkl", "")  for i in self.ls(tr) ])
        if len(tracers) == 0:
            self.MissingTracer(Name)
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

        for i in self._Selection:
            self.mkdir(self.output + "/Selections/" + i)
            th = Threading([[self._Selection[i], k, i] for k in self], _select, self.Threads, self.chnk)
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

        self.Finished()
        self.WhiteSpace()
        self.cd(self._tmp)
        self._tmp = False

    def __iter__(self):
        Dumped = self.DumpPickle or self.DumpHDF5
        CacheType = "EventCache" if self.EventCache else None
        CacheType = "DataCache" if self.DataCache else CacheType
            
        smpls = {i["INPUTSAMPLE"]["Name"] : None for i in self._InputValues if "INPUTSAMPLE" in i}
        self._lst = { "Data" : iter(self.SampleContainer.list()), "Tracers" : None, "Current" : []}
        if len(smpls) != 0 and CacheType != None and Dumped:
            self.ResetSampleContainer()
            
            cache = "/Tracers/" + CacheType + "/"
            if self._tmp == False:
                self.__BuildRootStructure()
                cache = self.pwd() + "/" + self.output + cache
                self.cd(self._tmp)
                self._tmp = False
            else:
                cache = self.output + cache
            self._lst["Tracers"] = [ cache + i + "/" + j for i in smpls for j in self.ls(cache + i) ]
            self._lst["Data"] = [ i.replace("/Tracers", "").replace(".pkl", "") for i in self._lst["Tracers"] ]
            self._lst["Data"] = iter([ [i + "/" + j for j in self.ls(i)] for i in self._lst["Data"] ])
            self._lst["Tracers"] = iter(self._lst["Tracers"])
        
        if self._lst["Tracers"] == None and self._launch == False:
            self.Launch()
            return self.__iter__()

        self.Lumi = 0
        return self

    def __next__(self):
        event = next(self._lst["Data"]) if len(self._lst["Current"]) == 0 else self._lst["Current"].pop(0) 
        if isinstance(event, list):
            events = { i.split("/")[-1].replace(".hdf5", "").replace(".pkl", "") : i for i in event }
            hdf5 = [ i for i in events.values() if i.endswith(".hdf5") ]
            Pkl = [ i for i in events.values() if i.endswith(".pkl") ]
            SampleContainer = UnpickleObject(next(self._lst["Tracers"]))
            events = {}
            if len(Pkl) != 0:
                pkl = Pickle()
                pkl.Caller = self.Caller
                pkl.VerboseLevel = 0
                pkl.Threads = self.Threads
                events |= pkl.MultiThreadedReading(Pkl)
           
            if len(hdf5) != 0:
                hdf = HDF5()
                hdf.Caller = self.Caller
                hdf.VerboseLevel = 0
                hdf.MultiThreadedReading(hdf5)
                events |= {_hash : ev for _hash, ev in hdf._names}
            
            SampleContainer.RestoreEvents(events, self.Threads, self.chnk)
            self._lst["Current"] = SampleContainer.list()
            self.SampleContainer += SampleContainer

            event = self._lst["Current"].pop(0)

        if self.Tree == None:
            self.Tree = list(event.Trees)[0]
        self.Lumi += float(event.Trees[self.Tree].Lumi)
        
        return event
