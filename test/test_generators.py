from AnalysisTopGNN.Generators import EventGenerator, GraphGenerator, Analysis
from AnalysisTopGNN.Events import Event, EventGraphChildren
from ExampleSelection import Example, Example2

smpl = "./TestCaseFiles/Sample/"
Files = {smpl + "Sample1" : ["smpl1.root"], smpl + "Sample2" : ["smpl1.root", "smpl2.root", "smpl3.root"]}

def test_eventgenerator():
    EvtGen = EventGenerator(Files)
    EvtGen.EventStop = 3
    EvtGen.EventStart = 1
    EvtGen.Event = Event
    EvtGen.SpawnEvents()
   
    assert len(EvtGen) != 0
    for event in EvtGen:
        assert event == EvtGen[event.Filename]

def _fx(a):
    return 1

def test_eventgraph():
    Ev = EventGenerator(Files)
    Ev.Event = Event 
    Ev.EventStop = 100
    Ev.SpawnEvents()
    
    Gr = GraphGenerator()
    Gr += Ev
    Gr.EventGraph = EventGraphChildren
    Gr.AddGraphFeature(_fx)
    Gr.TestFeatures(len(Ev))
    Gr.CompileEventGraph()
   
    assert len(Gr) == len(Ev)
    for i in Gr:
        assert i.Compiled
        assert Gr.HashToROOT(i.Filename) != None

def test_merge_eventgenerator():
    f = list(Files)
    File0 = {f[0] : [Files[f[0]][0]]}
    File1 = {f[1] : [Files[f[1]][0]]}
    
    _Files = {}
    _Files |= File0
    _Files |= File1

    ev0 = EventGenerator(File0)
    ev0.Event = Event
    ev0.SpawnEvents()
    
    ev1 = EventGenerator(File1)
    ev1.Event = Event
    ev1.SpawnEvents()
  
    combined = EventGenerator(_Files)
    combined.Event = Event
    combined.SpawnEvents()

    Object0 = {}
    for i in ev0:
        Object0[i.Filename] = i
    
    Object1 = {}
    for i in ev1:
        Object1[i.Filename] = i
    
    ObjectSum = {}
    for i in combined:
        ObjectSum[i.Filename] = i

    assert len(ObjectSum) == len(Object0) + len(Object1)
    assert len(combined) == len(ev0) + len(ev1)
    
    for i in Object0:
        assert ObjectSum[i] == Object0[i]

    for i in Object1:
        assert ObjectSum[i] == Object1[i]

    combined = combined + ev0 + ev1
    ObjectSum = {}
    for i in combined:
        ObjectSum[i.Filename] = i
    
    for i in Object0:
        assert ObjectSum[i] == Object0[i]

    for i in Object1:
        assert ObjectSum[i] == Object1[i]


    def EventGen(Dir, Name):
        Ana = Analysis()
        Ana.ProjectName = "TMPProject"
        Ana.InputSample(Name, Dir)
        Ana.EventCache = True
        Ana.Event = Event
        Ana.Threads = 10
        Ana.chnk = 1
        Ana.EventStart = 0
        Ana.EventStop = 10
        Ana.DumpHDF5 = True
        Ana.DumpPickle = True
        Ana.Launch()
        return Ana

    ev = EventGen(File0, "Tops")
    ev += EventGen(File1, "Top")
    
    for i in ev:
        assert ev[i.Filename].Filename == i.Filename
    ev.rm("TMPProject")

def test_analysis():
    AnaE = Analysis()
    AnaE.ProjectName = "Project"
    AnaE.InputSample("Sample1", smpl + "Sample1/" + Files[smpl + "Sample1"][0])
    AnaE.InputSample("Sample2", smpl + "Sample2/" + Files[smpl + "Sample2"][1])
    AnaE.Event = Event
    AnaE.EventCache = True
    AnaE.Threads = 2
    AnaE.EventStop = 100
    AnaE.DumpPickle = True
    AnaE.Launch()
    
    it = 0
    for i in AnaE:
        it += 1
    assert it == len(AnaE) and it != 0

    AnaE.rm("Project")

def test_selection():

    AnaE = Analysis()
    AnaE.ProjectName = "Project"
    AnaE.InputSample("Sample1", smpl + "Sample1/" + Files[smpl + "Sample1"][0])
    AnaE.InputSample("Sample2", smpl + "Sample2/" + Files[smpl + "Sample2"][1])
    AnaE.AddSelection("Example", Example)
    AnaE.AddSelection("Example2", Example2())
    AnaE.MergeSelection("Example")
    AnaE.MergeSelection("Example2")
    AnaE.Event = Event
    AnaE.EventCache = True
    AnaE.DumpPickle = True
    AnaE.Threads = 2
    AnaE.VerboseLevel = 1
    AnaE.Launch()
    
    it = 0
    c = 0
    y = []
    for i in AnaE:
        c += len(i.Trees["nominal"].TopChildren)
        t = Example2()
        t._EventPreprocessing(i)
        y.append(t)
        if it == 10:
            break
        it += 1
    l = len(y) 
    x = sum(y)
    assert l == len(x._TimeStats)
    assert l == x._CutFlow["Success->Example"]
    assert l*4 == len(x.Top["Truth"])
    assert len(x.Children["Truth"]) == c
    AnaE.rm("Project")

def _template( default = True):
    AnaE = Analysis()
    AnaE.ProjectName = "Project"
    if default == True:
        AnaE.InputSample("Sample1", smpl + "Sample1/" + Files[smpl + "Sample1"][0])
        AnaE.InputSample("Sample2", smpl + "Sample2/" + Files[smpl + "Sample2"][1])
    else:
        AnaE.InputSample(**default)

    AnaE.Threads = 2
    AnaE.VerboseLevel = 1
    return AnaE
 
def test_eventgen_nocache():
    
    AnaE = _template()
    AnaE.Event = Event 
    AnaE.Launch()

    assert len([i for i in AnaE]) != 0

def test_eventgen_nocache_nolaunch():
    
    AnaE = _template()
    AnaE.Event = Event 

    assert len([i for i in AnaE]) != 0

def test_eventgen_cache():
    
    AnaE = _template()
    AnaE.Event = Event 
    AnaE.EventCache = True
    AnaE.Launch()

    assert len([i for i in AnaE]) != 0

    AnaE = _template()
    AnaE.Event = Event
    AnaE.EventCache = True
    AnaE.Launch()

    assert len([i for i in AnaE]) != 0

    AnaE.rm("Project")


def test_eventgen_cache_diff_sample():
    
    Ana1 = _template({"Name" : "Sample2", "SampleDirectory" : smpl + "Sample2/" + Files[smpl + "Sample2"][1]})
    Ana1.Event = Event 
    Ana1.EventCache = True
    Ana1.Launch()

    assert len([i for i in Ana1]) != 0

    Ana2 = _template({"Name" : "Sample1", "SampleDirectory" : smpl + "Sample1/" + Files[smpl + "Sample1"][0]})
    Ana2.Event = Event
    Ana2.EventCache = True
    Ana2.Launch()

    assert len([i for i in Ana2]) != 0

    AnaE = _template()
    AnaE.Event = Event 
    AnaE.EventCache = True

    AnaS = Ana2 + Ana1
    assert len([i for i in AnaE if i.Filename not in AnaS]) == 0
    AnaE.rm("Project")

def test_datagen_nocache():

    AnaE = _template()
    AnaE.AddGraphFeature(_fx)
    AnaE.Event = Event 
    AnaE.EventGraph = EventGraphChildren
    AnaE.Launch()
    
    assert len([i for i in AnaE if i.Compiled]) != 0

def test_datagen_nocache_nolaunch():

    AnaE = _template()
    AnaE.AddGraphFeature(_fx)
    AnaE.Event = Event 
    AnaE.EventGraph = EventGraphChildren

    assert len([i for i in AnaE if i.Compiled]) != 0

def test_datagen_cache():
    
    AnaE = _template()
    AnaE.DataCache = True
    AnaE.AddGraphFeature(_fx)
    AnaE.EventGraph = EventGraphChildren
    AnaE.Event = Event 
    AnaE.Launch()

    assert len([i for i in AnaE]) != 0

    AnaE = _template()
    AnaE.DataCache = True
    AnaE.Launch()

    assert len([i for i in AnaE if i.Compiled]) != 0

    AnaE = _template()
    AnaE.DataCache = True
    AnaE.AddGraphFeature(_fx)
    AnaE.EventGraph = EventGraphChildren
    AnaE.Event = Event 
    AnaE.Launch()

    assert len([i for i in AnaE]) != 0
    AnaE.rm("Project")

def test_datagen_cache_diff_sample():
    
    Ana1 = _template({"Name" : "Sample2", "SampleDirectory" : smpl + "Sample2/" + Files[smpl + "Sample2"][1]})
    Ana1.Event = Event 
    Ana1.EventGraph = EventGraphChildren
    Ana1.AddGraphFeature(_fx)
    Ana1.DataCache = True
    Ana1.Launch()

    assert len([i for i in Ana1]) != 0

    Ana2 = _template({"Name" : "Sample1", "SampleDirectory" : smpl + "Sample1/" + Files[smpl + "Sample1"][0]})
    Ana2.Event = Event
    Ana2.EventGraph = EventGraphChildren
    Ana2.AddGraphFeature(_fx)
    Ana2.DataCache = True
    Ana2.Launch()

    assert len([i for i in Ana2]) != 0

    AnaE = _template()
    AnaE.DataCache = True
    AnaE.Launch()

    AnaS = Ana2 + Ana1
    assert len([i for i in AnaS if i.Filename not in AnaE]) == 0
    AnaE.rm("Project")

def test_data_evnt_cache_diff_sample():
    
    Ana1 = _template({"Name" : "Sample2", "SampleDirectory" : smpl + "Sample2/" + Files[smpl + "Sample2"][1]})
    Ana1.Event = Event 
    Ana1.EventCache = True
    Ana1.Launch()

    assert len([i for i in Ana1]) != 0

    Ana1 = _template({"Name" : "Sample2"})
    Ana1.EventGraph = EventGraphChildren
    Ana1.AddGraphFeature(_fx)
    Ana1.DataCache = True
    Ana1.DumpHDF5 = True
    Ana1.Launch()

    assert len([i for i in Ana1 if i.Compiled]) != 0

    Ana2 = _template({"Name" : "Sample1", "SampleDirectory" : smpl + "Sample1/" + Files[smpl + "Sample1"][0]})
    Ana2.Event = Event 
    Ana2.EventCache = True
    Ana2.Launch()

    assert len([i for i in Ana2]) != 0

    Ana2 = _template({"Name" : "Sample1"})
    Ana2.EventGraph = EventGraphChildren
    Ana2.AddGraphFeature(_fx)
    Ana2.DataCache = True
    Ana2.Launch()

    assert len([i for i in Ana2 if i.Compiled]) != 0

    Ana2.rm("Project")

