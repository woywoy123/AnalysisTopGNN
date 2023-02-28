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
            if len(self._SampleMap[Name]) == 0:
                smple = UnpickleObject(self.OutputDirectory + "/" + self.ProjectName + "/Tracers/" + Name)
                if smple == None:
                    return 
                self._SampleMap[Name] = {}
                for f in smple.ROOTFiles:
                    fdir = "/".join(f.split("/")[:-1])
                    self.AddListToDict(self._SampleMap[Name], fdir)
                    self._SampleMap[Name][fdir].append(f.split("/")[-1])
            return 
        if isinstance(SampleDirectory, dict):
            self._SampleMap[Name] |= self.ListFilesInDir(SampleDirectory, ".root")
            return 
        self._SampleMap[Name] |= self.ListFilesInDir({i : "*" for i in SampleDirectory}, ".root")

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
        if self.DumpPickle or self.DumpHDF5 or self.TrainingSampleName or len(self._MSelection) > 0 or len(self._Selection) > 0:
            self.mkdir(self.OutputDirectory + "/" + self.ProjectName)
            self.output = self.OutputDirectory + "/" + self.ProjectName
            self.cd(self.output)
        self.output = "." 


    def __GenerateEvents(self, InptMap, name):
        if self.DumpHDF5 or self.DumpPickle:
            self.ResetSampleContainer()  
 
        ec = self.__SearchAssets("EventCache", name)
        dc = self.__SearchAssets("DataCache", name)
        if self.EventCache and ec == None:
            pass
        elif self.DataCache and dc == None:
            pass
        else:
            return 

        _r = ""
        for f in self.DictToList(InptMap):
            tmp = f.split("/")
            if _r != tmp[-2]:
                _r = self.ReadingFileDirectory(tmp[-2])
            if self.EventCache and ec == None:
                if self.Event == None:
                    self.NoEventImplementation()
                    continue
                self.__EventGenerator(name, tmp)
            
            if self.DataCache and dc == None:
                if f not in self.SampleContainer:
                    self.EventCache = True 
                    self.__SearchAssets("EventCache", name)
                
                if f not in self.SampleContainer and self.Event == None:
                    self.NoEventImplementation()

                if f not in self.SampleContainer:
                    self.__EventGenerator(name, tmp)

                if self.EventGraph == None:
                    self.NoEventGraphImplementation()
                    continue
                self.__GraphGenerator(name, tmp)


    def __EventGenerator(self, name, filedir):
        if self.Event == None:
            return 

        ev = EventGenerator()
        ev.Caller = self.Caller
        ev.RestoreSettings(self.DumpSettings())
        ev.InputDirectory = {"/".join(filedir[:-1]) : filedir[-1]}
        ev.SpawnEvents()
        self.GetCode(ev)
        self += ev 
        
        if self.EventCache == False:
            return 

        self.__DumpCache(ev, name, filedir[-1], False)
            
    def __GraphGenerator(self, name, filedir):
        if self.EventGraph == None:
            return 
        
        direc = "/".join(filedir)
        gr = GraphGenerator()
        gr.SampleContainer.ROOTFiles[direc] = self.GetROOTContainer(direc)
        gr.RestoreSettings(self.DumpSettings())
        gr.CompileEventGraph()
        self.GetCode(gr)
        self += gr 
        if self.DataCache == False:
            return 

        self.__DumpCache(gr, name, filedir[-1], True)

    def __DumpCache(self, instance, name, fdir, Compiled):
        
        if Compiled == False:
            export = {ev.Filename : ev for ev in instance if self[ev.Filename] != ""}
        else:
            export = {ev.Filename : ev for ev in instance if self[ev.Filename].Compiled == Compiled}
        
        if self.DumpHDF5 == False and self.DumpPickle == False:
            return 
        
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
        
        out = self.output + "/Tracers/"
        out += "DataCache/" if Compiled else "EventCache/"
        PickleObject(self.SampleContainer.ClearEvents(), out + name) 
    
    def __GenerateTrainingSample(self):
        def MarkSample(smpl, status):
            for i in smpl:
                obj = self[i]
                obj.Train = status
       
        if not self.TrainingSampleName:
            return 
        
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
        if isinstance(Name, list):
            for i in Name:
                self.__SearchAssets(CacheType, i)
            return 
        
        if CacheType == "EventCache" and self.EventCache == False:
            return 
        if CacheType == "DataCache" and self.DataCache == False:
            return 

        tr = self.output + "/Tracers/" + CacheType + "/" + Name + ".pkl"
        if self.IsFile(tr) == False:
            if self.DumpPickle == False and self.DumpHDF5 == False:
                self.MissingTracer(tr)
            return 
        SampleContainer = UnpickleObject(tr)
        root = self.output + "/" + CacheType + "/" + Name 
        SampleDirectory = [root + "/" + i for i in self.ls(root)]

        _pkl = self.DictToList(self.ListFilesInDir({i : "*" for i in SampleDirectory}, ".pkl"))
        if len(_pkl) != 0:
            pkl = Pickle()
            pkl.Caller = self.Caller
            pkl.VerboseLevel = 0
            events = pkl.MultiThreadedReading(_pkl, Name)

            self.SampleContainer += SampleContainer
            self.SampleContainer.RestoreEvents(events)
            return True

        _hdf = self.DictToList(self.ListFilesInDir({i : "*" for i in SampleDirectory}, ".hdf5"))
        if len(_hdf) != 0:
            hdf = HDF5()
            hdf.Caller = self.Caller
            hdf.VerboseLevel = 0
            hdf.MultiThreadedReading(_hdf)
            events = {_hash : ev for _hash, ev in hdf._names}
            
            self.SampleContainer += SampleContainer
            self.SampleContainer.RestoreEvents(events)
            return True
       
        else:
            self.NoCache(root)
            return 
    
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
            out = []
            for k in inpt:
                t = pkl.UnpickleObject(k)
                out.append(Selection().RestoreSettings(t))
                self.rm(k)
            inpt = sum(out)
            inpt = inpt if isinstance(inpt, list) else [inpt]
            out = [""]*(len(out)-len(inpt)) + inpt
            return out
        
        if not self.__SwitchTable():
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
            th._lists = [k for k in th._lists if isinstance(k, str) == False]
            pkl.PickleObject(sum(th._lists), i, self.output + "/Selections/Merged/")
   
    def __SwitchTable(self):
        if self.TrainingSampleName:
            return True 
        if self.Event == None and self.EventGraph == None:
            return True 
        if self.FeatureTest: 
            return True 
        if len(self._Selection) > 0:
            return True 
        if len(self._MSelection) > 0:
            return True 
        return False

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
            self.NoSamples(self._SampleMap[i], i)
            self.__GenerateEvents(self._SampleMap[i], i)
            if self.__SwitchTable():
                search = "EventCache" if self.EventCache else False
                search = "DataCache" if self.DataCache else search
                if search == False and self.TrainingSampleName: 
                    self.CantGenerateTrainingSample()
                self.__SearchAssets(search, i)
                continue
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
