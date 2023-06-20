class _General:
    def __init__(self):
        self.Caller = "" if "Caller" not in self.__dict__ else self.Caller.upper()
        self.Verbose = 3
        self.Threads = 6
        self.chnk = 10
        self._Code = {}
        self.EventStart = -1
        self.EventStop = None
        self.SampleName = ""
        self._Device = "cpu"
        self._condor = False
        self.OutputDirectory = None


class _UpROOT:
    def __init__(self):
        self.StepSize = 1000
        self.Trees = []
        self.Branches = []
        self.Leaves = []
        self.Files = {}


class _EventGenerator:
    def __init__(self):
        self.Event = None
        self.Files = {}


class _GraphGenerator:
    def __init__(self):
        self.EventGraph = None
        self.SelfLoop = True
        self.FullyConnect = True
        self.GraphAttribute = {}
        self.NodeAttribute = {}
        self.EdgeAttribute = {}


class _SelectionGenerator:
    def __init__(self):
        self.Selections = {}
        self.Merge = {}
        self.OutputDirectory = "./"


class _RandomSampler:
    def __init__(self):
        self.nEvents = 10
        self.TrainingSize = False
        self.BatchSize = 1
        self.Shuffle = True
        self.kFolds = False


class _FeatureAnalysis:
    def __init__(self):
        self.GraphAttribute = {}
        self.NodeAttribute = {}
        self.EdgeAttribute = {}
        self.TestFeatures = False


class _Analysis:
    def __init__(self):
        _UpROOT.__init__(self)
        _Pickle.__init__(self)
        _EventGenerator.__init__(self)
        _GraphGenerator.__init__(self)
        _SelectionGenerator.__init__(self)
        _RandomSampler.__init__(self)
        _FeatureAnalysis.__init__(self)
        _Optimizer.__init__(self)
        _General.__init__(self)
        self._cPWD = None
        self.ProjectName = "UNTITLED"
        self.SampleMap = {}
        self.EventCache = False
        self.DataCache = False
        self.PurgeCache = False


class _Pickle:
    def __init__(self):
        self._ext = ".pkl"


class _Plotting:
    def __init__(self):
        self.Style = None
        self.ATLASData = False
        self.ATLASYear = None
        self.ATLASLumi = None
        self.ATLASCom = None
        self.Color = None
        self.Colors = []
        self.NEvents = None
        self.LaTeX = True

        self.FontSize = 10
        self.LabelSize = 12.5
        self.TitleSize = 10
        self.LegendSize = 10

        self.Logarithmic = False
        self.xScaling = 1.25
        self.yScaling = 1.25
        self.DPI = 250

        self.Title = None
        self.Filename = None
        self.OutputDirectory = "Plots"

        # --- Histogram Cosmetic Styles --- #
        self.Texture = False
        self.Alpha = 0.5
        self.FillHist = "fill"

        # --- Data Display --- #
        self.Normalize = None
        self.IncludeOverflow = False

        # --- Cosmetic --- #
        self.LineStyle = None
        self.LineWidth = 1
        self.Marker = None
        self.DoStatistics = False
        self.MakeStaticHistograms = False
        self.Lines = []
        self.LegendOn = True


class _Condor:
    def __init__(self):
        self.CondaEnv = None
        self.PythonVenv = None
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
        self.CondaEnv = None
        self.PythonVenv = None


class _JobSpecification:
    def __init__(self):
        self.Job = None
        self.Time = None
        self.Memory = None
        self.Device = None
        self.Name = None
        self.CondaEnv = None
        self.PythonVenv = None


class _Optimizer:
    def __init__(self):
        self.ProjectName = "UNTITLED"

        self.Optimizer = None
        self.Scheduler = None
        self.SchedulerParams = {}
        self.OptimizerParams = {}

        self.RunName = "RUN"
        self.Epoch = None
        self.Epochs = 10
        self.kFold = None
        self.DebugMode = False
        self.TrainingName = "Sample"

        self.Model = None
        self.ContinueTraining = False
        self.SortByNodes = False
        self.BatchSize = 1
        self.EnableReconstruction = False


class Settings:
    def __init__(self, caller=False):
        if caller:
            self.Caller = caller
        _General.__init__(self)
        if self.Caller == "UP-ROOT":
            _UpROOT.__init__(self)
        if self.Caller == "PICKLER":
            _Pickle.__init__(self)
        if self.Caller == "EVENTGENERATOR":
            _EventGenerator.__init__(self)
        if self.Caller == "GRAPHGENERATOR":
            _GraphGenerator.__init__(self)
        if self.Caller == "SELECTIONGENERATOR":
            _SelectionGenerator.__init__(self)
        if self.Caller == "RANDOMSAMPLER":
            _RandomSampler.__init__(self)
        if self.Caller == "FEATUREANALYSIS":
            _FeatureAnalysis.__init__(self)
        if self.Caller == "OPTIMIZER":
            _Optimizer.__init__(self)
        if self.Caller == "ANALYSIS":
            _Analysis.__init__(self)
        if self.Caller == "CONDOR":
            _Condor.__init__(self)
        if self.Caller == "JOBSPECS":
            _JobSpecification.__init__(self)
        if self.Caller == "CONDORSCRIPT":
            _CondorScript.__init__(self)
        if self.Caller == "PLOTTING":
            _Plotting.__init__(self)

    @property
    def Device(self):
        return self._Device

    @Device.setter
    def Device(self, val):
        import torch

        if val == None:
            self._Device = "cpu"
            return
        self._Device = val if "cuda" in val and torch.cuda.is_available() else "cpu"

    def ImportSettings(self, inpt):
        if not issubclass(type(inpt), Settings):
            return
        s = Settings(self.Caller)
        for i in s.__dict__:
            try:
                setattr(self, i, getattr(inpt, i))
            except AttributeError:
                continue

    @property
    def DumpSettings(self):
        default = Settings(self.Caller)
        default.__dict__["Device"] = "cpu"
        out = {}
        for i in default.__dict__:
            if i.startswith("_"):
                continue
            try:
                getattr(self, i) == default.__dict__[i]
            except KeyError:
                continue
            if getattr(self, i) == default.__dict__[i]:
                continue
            out[i] = getattr(self, i)
        return out
