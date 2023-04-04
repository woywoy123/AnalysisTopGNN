from AnalysisTopGNN.Tools import Tools

class _Code(Tools):

    def __init__(self):
        self.Name = None 
        self.Module = None 
        self.Path = None 
        self.Code = None 
        self._File = None

    def DumpCode(self, Instance):
        try:
            self.Name = Instance.__qualname__
        except AttributeError:
            try:
                self.Name = Instance.__name__
            except AttributeError:
                self.Name = type(Instance).__name__
        self.Module = Instance.__module__
        self.Path = self.Module + "." + self.Name
        self.Code = self.GetSourceFile(Instance)
        self._File = self.GetSourceFileDirectory(Instance)
    
    def CopyInstance(self, Instance):
        if callable(Instance):
            try:
                Inst = Instance()
            except:
                Inst = Instance
            Inst = Instance
        if self.Name == None:
            self.DumpCode(Instance)
            
        _, inst = self.GetObjectFromString(self.Module, self.Name)
        return inst

    def __eq__(self, other):
        if self.Code == other.Code:
            return True 
        return False

class _General:

    def __init__(self):
        self.VerboseLevel = 3
        self.chnk = 12
        self.Threads = 12
        self.Tree = None
        self._dump = False
        self._Code = []
        self.EventStart = 0
        self.EventStop = None

        self.ProjectName = "UNTITLED"
        self.SampleContainer = None
        self.OutputDirectory = "./"

class _EventGenerator:

    def __init__(self):
        self.Event = None
        self.InputDirectory = {}
    
class _GraphGenerator:
    
    def __init__(self):
        self.Device = "cpu"
        self.SelfLoop = True 
        self.FullyConnect = True 
        self.EventGraph = None
        self.GraphAttribute = {}
        self.NodeAttribute = {}
        self.EdgeAttribute = {}

class _HDF5:

    def __init__(self):
        self._File = None
        self._ext = ".hdf5"
        self._iter = -1
        self._obj = {}
        self.VerboseLevel = 3
        self.Threads = 12
        self.chnk = 1
        self.Filename = "UNTITLED"
        self.Directory = False

class _Pickle:

    def __init__(self):
        self._ext = ".pkl"
        self.VerboseLevel = 3
        self.Threads = 12
        self.chnk = None

class _TrainingSample:

    def __init__(self):
        self.TrainingSampleName = False
        self.TrainingPercentage = 80

class _Optimization:
    def __init__(self):
        self.SplitSampleByNode = False
        self.kFolds = 10
        self.BatchSize = 10
        self.Model = None
        self.DebugMode = False
        self.ContinueTraining = False
        self.RunName = "UNTITLED"
        self.Epochs = 10
        self.Optimizer = None 
        self.Scheduler = None
        self.Device = "cpu"
        self.VerbosityIncrement = 10 # Might need deprecation...

class _ModelEvaluator:
    
    def __init__(self):
        self._ModelDirectories = {}
        self._ModelSaves = {}
        self.Device = "cpu"
        self.SampleNodes = {}
        self.Training = {}
        self.TestSample = {}
        self.PlotNodeStatistics = False
        self.PlotTrainingStatistics = False
        self.PlotTrainSample = False
        self.PlotTestSample = False
        self.PlotEntireSample = False
        self.PlotEpochDebug = False
        self.PlotModelComparison = False

class _Analysis:

    def __init__(self):
        _General.__init__(self) 
        _EventGenerator.__init__(self)
        _GraphGenerator.__init__(self)
        _TrainingSample.__init__(self)
        _Optimization.__init__(self)
        _ModelEvaluator.__init__(self)
        self._SampleMap = {}
        self._Selection = {}
        self._MSelection = {}
        self._InputValues = []
        self._lst = []
        
        self.EventCache = False
        self.DataCache = False
        self._launch = False
        self._tmp = False
        self.output = None

        self.DumpHDF5 = False
        self.DumpPickle = False
        self.FeatureTest = False

class _Condor:

    def __init__(self):
        self.CondaEnv = False
        self.PythonVenv = "$PythonGNN"
        self.EventCache = None
        self.DataCache = None
        self._dump = True
        self.ProjectName = None
        self.VerboseLevel = 0
        self.Tree = None
        self.OutputDirectory = None

class _CondorScript:

    def __init__(self):
        self.ExecPath = None
        self.ScriptName = "main"
        self.OpSysAndVer = "CentOS7"
        self.Device = None
        self.Threads = None
        self.Time = None
        self.Memory = None
        self.CondaEnv = False
        self.PythonVenv = "$PythonGNN"

class _JobsSpecification:

    def __init__(self):
        self.Job = None
        self.Time = None
        self.Memory = None
        self.Device = None
        self.Name = None
        self.EventCache = None
        self.DataCache = None
        self.CondaEnv = False
        self.PythonVenv = "$PythonGNN"
 
class _File:

    def __init__(self):
        self.StepSize = 5000
        self.VerboseLevel = 3

class _Selection:

    def __init__(self):
        self.Tree = None
        self._OutDir = False
        self._hash = None
        self._Residual = []
        self._CutFlow = {}
        self._TimeStats = []
        self._AllEventWeights = []
        self._SelectionEventWeights = []
 
class Settings(_General):
    
    def __init__(self):
        if self.Caller == "CONDOR":
            _Condor.__init__(self)
            return 

        if self.Caller == "FILE":
            _File.__init__(self)
            return

        if self.Caller == "CONDORSCRIPT":
            _CondorScript.__init__(self)
            return 

        if self.Caller == "JOBSPECS":
            _JobsSpecification.__init__(self)
            return 
        
        if self.Caller == "PICKLER":
            _Pickle.__init__(self)
            return 
        
        if self.Caller == "SELECTION":
            _Selection.__init__(self)
            return 

        _General.__init__(self)
        if self.Caller == "EVENTGENERATOR":
            _EventGenerator.__init__(self)
        
        if self.Caller == "GRAPHGENERATOR":
            _GraphGenerator.__init__(self)

        if self.Caller == "HDF5":
            _HDF5.__init__(self)

        if self.Caller == "OPTIMIZATION":
            _Optimization.__init__(self)

        if self.Caller == "MODELEVALUATOR":
            _ModelEvaluator.__init__(self)

        if self.Caller == "ANALYSIS":
            _Analysis.__init__(self)
        
    def DumpSettings(self):
        return self.__dict__ 
    
    def ExportAnalysisScript(self):
        def Hash(obj):
            return str(hex(id(self.AddCode(obj))))

        dic = self.DumpSettings()
        exclude = ["Caller", "_Code", "SampleContainer", "_dump"]
        code = ["Event", "EventGraph", "GraphAttribute", "NodeAttribute", "EdgeAttribute", "Model", "_InputValues"] 
        ana_tmp = _Analysis()
            
        out = []
        for i in dic:
            if i in exclude:
                continue
            if dic[i] == ana_tmp.__dict__[i]:
                continue

            if i in code:
                if i == "Event":
                    Event = self.CopyInstance(dic[i])
                    ev = {k : Hash(Event.Objects[k]) for k in Event.Objects}
                    continue

                elif i == "_InputValues":
                    for k in self._InputValues:
                        if "INPUTSAMPLE" in k:
                            continue
                        elif "EVALUATEMODEL" in k:
                            k["EVALUATEMODEL"]["ModelInstance"] = Hash(k["EVALUATEMODEL"]["ModelInstance"])
                        elif "ADDSELECTION" in k:
                            k["ADDSELECTION"]["inpt"] = Hash(k["ADDSELECTION"]["inpt"])
                else: 
                    dic[i] = {k : Hash(dic[i][k]) for k in dic[i]} if isinstance(dic[i], dict) else Hash(dic[i])

            inst = str(dic[i]) if isinstance(dic[i], int) else ""
            inst = "'" + dic[i] + "'" if isinstance(dic[i], str) else inst
            inst = str(dic[i]) if isinstance(dic[i], list) else inst
            inst = str(dic[i]) if dic[i] == None else inst
            inst = str(dic[i]) if isinstance(dic[i], dict) else inst

            out += ["<*AnalysisName*>." + i + " = " + inst] 
        return out
   
    def CheckSettings(self):
        S = Settings
        S.Caller = self.Caller
        S = S()
        S.Caller = self.Caller
        invalid = []
        for i in self.__dict__:
            if i not in S.__dict__:
                invalid.append(i)
        return invalid

    def RestoreSettings(self, inpt):
        for i in self.__dict__:
            if i not in inpt:
                continue
            if i == "_Code" or i == "SampleContainer" or i == "Caller":
               continue
            self.__dict__[i] = inpt[i]

    def AddCode(self, Instance):
        _c = _Code()
        _c.DumpCode(Instance)
        if _c not in self._Code:
            self._Code.append(_c)
        return self._Code[self._Code.index(_c)]

    def CopyInstance(self, Instance):
        _c = self.AddCode(Instance)
        return _c.CopyInstance(Instance) 
    
    def GetCode(self, inpt):
        for _c in inpt._Code:
            if _c in self._Code:
                continue
            self._Code.append(_c)
 
