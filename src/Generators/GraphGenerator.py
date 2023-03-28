import torch
from AnalysisTopGNN.Tools import Threading
from AnalysisTopGNN.Notification import GraphGenerator_
from AnalysisTopGNN.Samples import SampleTracer
from AnalysisTopGNN.Tools import RandomSamplers
from AnalysisTopGNN.Features import FeatureAnalysis
from AnalysisTopGNN.Generators import Settings

class GraphFeatures(FeatureAnalysis, RandomSamplers):
    
    def __init__(self):
        pass

    def SetAttribute(self, c_name, fx, container):
        if c_name == "P_" or c_name == "T_":
            c_name += fx.__name__ 
        elif c_name == "":
            c_name += fx.__name__ 

        if c_name not in container:
            container[c_name] = fx
        else:
            self.Warning("Found Duplicate " + c_name + " Attribute")
   
    # Define the observable features
    def AddGraphFeature(self, fx, name = ""):
        self.SetAttribute(name, fx, self.GraphAttribute)

    def AddNodeFeature(self, fx, name = ""):
        self.SetAttribute(name, fx, self.NodeAttribute)

    def AddEdgeFeature(self, fx, name = ""):
        self.SetAttribute(name, fx, self.EdgeAttribute)

    
    # Define the truth features used for supervised learning 
    def AddGraphTruth(self, fx, name = ""):
        self.SetAttribute("T_" + name, fx, self.GraphAttribute)

    def AddNodeTruth(self, fx, name = ""):
        self.SetAttribute("T_" + name, fx, self.NodeAttribute)

    def AddEdgeTruth(self, fx, name = ""):
        self.SetAttribute("T_" + name, fx, self.EdgeAttribute)

    
    # Define any last minute changes to attributes before adding to graph
    def AddGraphPreprocessing(self, name, fx):
        self.SetAttribute("P_" + name, fx, self.GraphAttribute)

    def AddNodePreprocessing(self, name, fx):
        self.SetAttribute("P_" + name, fx, self.NodeAttribute)

    def AddEdgePreprocessing(self, name, fx):
        self.SetAttribute("P_" + name, fx, self.EdgeAttribute)

    def SetDevice(self):
        if self.Device:
            self.Device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def TestFeatures(self, SamplingSize = 100):
        self.SetDevice()
        self.CheckSettings()
        if self.Caller == "ANALYSIS":
            self.FeatureTest = True
            self.Launch()
        Events = self.RandomEvents(self.SampleContainer.list(), SamplingSize)
        self.TestEvent(Events, self.EventGraph)
 

class GraphGenerator(GraphGenerator_, SampleTracer, Settings, GraphFeatures):
    
    def __init__(self):
        
        self.Caller = "GRAPHGENERATOR"
        Settings.__init__(self)
        SampleTracer.__init__(self)
        self._Test = False
 
    def __MakeGraph(self, event, smplidx):
        evobj = self.CopyInstance(self.EventGraph)

        if self._Test == False:
            smpl = len(self.SampleContainer.list())
            self.TestFeatures( 10 if smpl > 10 else smpl )
            self._Test = True
        try:
            ev = evobj(event)
        except AttributeError:
            
            ev = evobj.Escape(evobj)
            ev.Event = event
            ev.Particles = []
        ev.iter = smplidx
        ev.SelfLoop = self.SelfLoop
        ev.FullyConnect = self.FullyConnect
        ev.EdgeAttr |= self.EdgeAttribute
        ev.NodeAttr |= self.NodeAttribute
        ev.GraphAttr |= self.GraphAttribute
        return ev

    def AddSamples(self, Events, Tree):
        
        for ev in Events:
            if Tree == None:
                ev.Trees |= {tr : self.__MakeGraph(ev.Trees[tr], ev.EventIndex) for tr in ev.Trees}
            else:
                ev.Trees |= {Tree : self.__MakeGraph(ev.Trees[Tree], ev.EventIndex)}

    def CompileEventGraph(self):
        self.AddCode(self.EventGraph)
        
        Features = {c_name : self.AddCode(self.GraphAttribute[c_name]) for c_name in self.GraphAttribute}
        Features = {c_name : self.AddCode(self.NodeAttribute[c_name]) for c_name in self.NodeAttribute}   
        Features = {c_name : self.AddCode(self.EdgeAttribute[c_name]) for c_name in self.EdgeAttribute}

        if self._dump:
            return self

        self.SetDevice()
        self.CheckSettings()
        self.AddSamples(self.SampleContainer.list()[self.EventStart : self.EventStop], self.Tree)
        def function(inpt):
            return [i.MakeGraph() if i != None else True for i in inpt]

        TH = Threading(self.SampleContainer.list(), function, self.Threads, self.chnk)
        TH.VerboseLevel = self.VerboseLevel
        TH.Start()
        for i in TH._lists:
            if i.Compiled == False:
                continue
            self.SampleContainer[i.Filename] = i

        self.EdgeAttribute = {}
        self.GraphAttribute = {}
        self.NodeAttribute = {}
