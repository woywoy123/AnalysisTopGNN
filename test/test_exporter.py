from AnalysisTopGNN.Generators import EventGenerator, GraphGenerator
from AnalysisTopGNN.IO import UnpickleObject, PickleObject, HDF5
from AnalysisTopGNN.Events import Event, EventGraphChildren

smpl = "./TestCaseFiles/Sample/"
Files = {smpl + "Sample1" : ["smpl1.root"], smpl + "Sample2" : ["smpl1.root", "smpl2.root", "smpl3.root"]}

def test_EventGenerator():
    File1 = [list(Files)[0] + "/" + i for i in Files[list(Files)[0]]]
    File2 = [list(Files)[1] + "/" + i for i in Files[list(Files)[1]]]

    Ev = EventGenerator(File1) 
    Ev.Event = Event
    Ev.chnk = 1000
    Ev.Threads = 1
    Ev.SpawnEvents()
    PickleObject(Ev, "TMP1")

    T = EventGenerator(File2) 
    T.Event = Event
    T.chnk = 1000
    T.Threads = 12
    T.SpawnEvents()
    PickleObject(T, "TMP2")

    T = EventGenerator(Files) 
    T.Event = Event
    T.chnk = 1000
    T.Threads = 12
    T.SpawnEvents()
    PickleObject(T, "TMP3")
        
    ev1 = UnpickleObject("TMP1")
    ev2 = UnpickleObject("TMP2")
    ev3 = UnpickleObject("TMP3")
    p = sum([ev1, ev2])
    
    assert len(p) == len(ev3)
    print("PASSED: SAME LENGTH", len(p), len(ev3))

    for i, j in zip(p, ev3):
        assert i.EventIndex == j.EventIndex
    print("PASSED: CONSISTENT INDEX")

    for i, j in zip(p, ev3):
        assert i.Filename == j.Filename
    print("PASSED: SAME FILENAMES")
    
    for i, j in zip(p, ev3):
        assert len(i.Trees["nominal"].DetectorObjects) == len(j.Trees["nominal"].DetectorObjects)
    print("PASSED: SAME NUMBER OF PARTICLES PER EVENT")

    ev1 = UnpickleObject("TMP1")
    ev2 = UnpickleObject("TMP2")
    ev3 = UnpickleObject("TMP3")
    z = UnpickleObject("TMP3")
    p = sum([ev1, ev2, ev3])
    
    assert len(p) == len(z)
    print("PASSED: SAME LENGTH", len(p), len(z))

    for i in p:
        assert isinstance(z.HashToROOT(i.Filename), str)
    print("PASSED: SAME FILENAMES")
    
    for i in p:
        ob1, ob2 = p[i.Filename], z[i.Filename]
        assert len(ob1.Trees["nominal"].DetectorObjects) == len(ob2.Trees["nominal"].DetectorObjects)
    print("PASSED: SAME NUMBER OF PARTICLES PER EVENT")
    ev1.rm("_Pickle")

def _fx(a):
    return a.eta

def test_graphgenerator():
    File1 = [list(Files)[0] + "/" + i for i in Files[list(Files)[0]]]
    File2 = [list(Files)[1] + "/" + i for i in Files[list(Files)[1]]]
    
    Ev = EventGenerator(File1) 
    Ev.Event = Event
    Ev.SpawnEvents()
    
    Gr = GraphGenerator()
    Gr += Ev 
    Gr.AddNodeFeature(_fx, "TEST")
    Gr.EventGraph = EventGraphChildren
    Gr.CompileEventGraph()
    PickleObject(Gr, "TMP1")

    T = EventGenerator(File2) 
    T.Event = Event
    T.SpawnEvents()

    Gr = GraphGenerator()
    Gr += T 
    Gr.AddNodeFeature(_fx, "TEST")
    Gr.EventGraph = EventGraphChildren
    Gr.CompileEventGraph()
    PickleObject(Gr, "TMP2")

    T = EventGenerator(Files) 
    T.Event = Event
    T.SpawnEvents()

    Gr = GraphGenerator()
    Gr += T
    Gr.AddNodeFeature(_fx, "TEST")
    Gr.EventGraph = EventGraphChildren
    Gr.CompileEventGraph()
    PickleObject(Gr, "TMP3")

    ev1 = UnpickleObject("TMP1")
    ev2 = UnpickleObject("TMP2")
    z = UnpickleObject("TMP3")

    p = sum([ev1, ev2])
    
    assert len(p) == len(z)
    print("PASSED: SAME LENGTH", len(p), len(z))

    for i, j in zip(p, z):
        assert i.EventIndex == j.EventIndex
    print("PASSED: CONSISTENT INDEX")

    for i, j in zip(p, z):
        assert i.Filename == j.Filename
    print("PASSED: SAME FILENAMES")
    
    for i, j in zip(p, z):
        assert i.Trees["nominal"].num_nodes == j.Trees["nominal"].num_nodes
    print("PASSED: SAME NUMBER OF PARTICLES PER EVENT")

    ev1 = UnpickleObject("TMP1")
    ev2 = UnpickleObject("TMP2")
    ev3 = UnpickleObject("TMP3")
    z = UnpickleObject("TMP3")
    p = sum([ev1, ev2, ev3])
    
    assert len(p) == len(z)
    print("PASSED: SAME LENGTH", len(p), len(z))

    for i in p:
        assert isinstance(z.HashToROOT(i.Filename), str)
    print("PASSED: SAME FILENAMES")
    
    for i, j in zip(p, z):
        ob1, ob2 = p[i.Filename], z[i.Filename]
        assert ob1.Trees["nominal"].num_nodes == ob2.Trees["nominal"].num_nodes
    print("PASSED: SAME NUMBER OF PARTICLES PER EVENT")
    Ev.rm("_Pickle")

def test_EventGeneratorDumper():
    Ev = EventGenerator(Files) 
    Ev.Event = Event 
    Ev.EventStop = 14
    Ev.SpawnEvents()
    
    Objects = {}
    for i in Ev:
        Objects[i.Filename] = i

    hdf = HDF5()
    hdf.Threads = 2
    hdf.VerboseLevel = 0
    hdf.Directory = "./_Pickle/"
    hdf.MultiThreadedDump(Objects, "./_Pickle/")
    for name, obj in hdf:
        print(name, obj.Trees["nominal"].Tops, obj)
        print(len(Objects[name].Trees["nominal"].DetectorObjects) == len(obj.Trees["nominal"].DetectorObjects))
        assert len(Objects[name].Trees["nominal"].DetectorObjects) == len(obj.Trees["nominal"].DetectorObjects)

    hdf.MergeHDF5("_Pickle/")
    hdf.Directory = False
    hdf.Filename = "_Pickle/UNTITLED.hdf5"
    for name, obj in hdf:
        print(name, obj.Trees["nominal"].Tops, obj)
        print(len(Objects[name].Trees["nominal"].DetectorObjects) == len(obj.Trees["nominal"].DetectorObjects))
        assert len(Objects[name].Trees["nominal"].DetectorObjects) == len(obj.Trees["nominal"].DetectorObjects)
    hdf.rm("_Pickle")

def test_GraphGeneratorDumper():
    Ev = EventGenerator(Files) 
    Ev.Event = Event 
    Ev.EventStop = 14
    Ev.SpawnEvents()
    
    Gr = GraphGenerator()
    Gr += Ev
    Gr.AddNodeFeature(_fx)
    Gr.EventGraph = EventGraphChildren
    Gr.CompileEventGraph()

    hdf = HDF5()
    Objects = {}
    for i in Gr:
        Objects[i.Filename] = i
    hdf.MultiThreadedDump(Objects, "_Pickle/Graphs/")
    hdf.MergeHDF5("_Pickle/Graphs/")
    hdf.Filename = "_Pickle/Graphs/UNTITLED.hdf5"
    for name, obj in hdf:
        assert name == obj.Filename
        assert bool(Objects[name].Trees["nominal"].num_nodes == obj.Trees["nominal"].num_nodes)
    hdf.rm("_Pickle")
