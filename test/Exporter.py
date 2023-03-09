from AnalysisTopGNN.Generators import EventGenerator, GraphGenerator
from AnalysisTopGNN.IO import UnpickleObject, PickleObject
from AnalysisTopGNN.Events import Event, EventGraphChildren
from AnalysisTopGNN.Samples import SampleTracer
from AnalysisTopGNN.IO import HDF5

def TestEventGenerator(Files):
    File1 = Files[0]
    File2 = Files[1] 

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

    for i, j in zip(p, z):
        assert i.EventIndex == j.EventIndex
    print("PASSED: CONSISTENT INDEX")
    
    for i, j in zip(p, z):
        assert i.Filename == j.Filename
    print("PASSED: SAME FILENAMES")
    
    for i, j in zip(p, z):
        assert len(i.Trees["nominal"].DetectorObjects) == len(j.Trees["nominal"].DetectorObjects)
    print("PASSED: SAME NUMBER OF PARTICLES PER EVENT")

    return True 


def Test(a):
    return a.eta

def TestGraphGenerator(Files):
    from AnalysisTopGNN.Generators import GraphGenerator
    from AnalysisTopGNN.Events import EventGraphChildren

    File1 = Files[0]
    File2 = Files[1] 

    Ev = EventGenerator(File1) 
    Ev.Event = Event
    Ev.SpawnEvents()
    
    Gr = GraphGenerator()
    Gr += Ev 
    Gr.AddNodeFeature(Test, "TEST")
    Gr.EventGraph = EventGraphChildren
    Gr.CompileEventGraph()
    PickleObject(Gr, "TMP1")

    T = EventGenerator(File2) 
    T.Event = Event
    T.SpawnEvents()

    Gr = GraphGenerator()
    Gr += T 
    Gr.AddNodeFeature(Test, "TEST")
    Gr.EventGraph = EventGraphChildren
    Gr.CompileEventGraph()
    PickleObject(Gr, "TMP2")

    T = EventGenerator(Files) 
    T.Event = Event
    T.SpawnEvents()

    Gr = GraphGenerator()
    Gr += T
    Gr.AddNodeFeature(Test, "TEST")
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

    for i, j in zip(p, z):
        assert i.EventIndex == j.EventIndex
    print("PASSED: CONSISTENT INDEX")

    for i, j in zip(p, z):
        assert i.Filename == j.Filename
    print("PASSED: SAME FILENAMES")
    
    for i, j in zip(p, z):
        assert i.Trees["nominal"].num_nodes == j.Trees["nominal"].num_nodes
    print("PASSED: SAME NUMBER OF PARTICLES PER EVENT")

    return True 


def TestEventGeneratorDumper(Files):

    File1 = Files[0]

    Ev = EventGenerator(File1) 
    Ev.Event = Event
    Ev.SpawnEvents()
    
    Objects = {}
    it = 0
    for i in Ev:
        Objects[i.Filename] = i
        it+=1 
        if it == 24:
            break

    hdf = HDF5()
    hdf.Threads = 12
    hdf.VerboseLevel = 0
    hdf.Directory = "./_Pickle/"
    hdf.MultiThreadedDump(Objects, "./_Pickle/")
    for name, obj in hdf:
        print(name, obj.Trees["nominal"].Tops, obj)
        print(len(Objects[name].Trees["nominal"].DetectorObjects) == len(obj.Trees["nominal"].DetectorObjects))
        if len(Objects[name].Trees["nominal"].DetectorObjects) == len(obj.Trees["nominal"].DetectorObjects):
            continue
        return False

    hdf.MergeHDF5("_Pickle/")
    hdf.Directory = False
    hdf.Filename = "_Pickle/UNTITLED.hdf5"
    for name, obj in hdf:
        print(name, obj.Trees["nominal"].Tops, obj)
        print(len(Objects[name].Trees["nominal"].DetectorObjects) == len(obj.Trees["nominal"].DetectorObjects))
        if len(Objects[name].Trees["nominal"].DetectorObjects) == len(obj.Trees["nominal"].DetectorObjects):
            continue
        return False
    return True

def TestGraphGeneratorDumper(Files):
    from AnalysisTopGNN.Generators import GraphGenerator
    from AnalysisTopGNN.Events import EventGraphChildren
    
    File1 = Files[0]

    Ev = EventGenerator(File1) 
    Ev.Event = Event
    Ev.SpawnEvents()
    
    Gr = GraphGenerator()
    Gr += Ev
    Gr.AddNodeFeature(Test)
    Gr.EventGraph = EventGraphChildren
    Gr.CompileEventGraph()

    hdf = HDF5()
    Objects = {}
    it = 0
    for i in Gr:
        Objects[i.Filename] = i
        it+=1 
        if it == 12:
            break
    hdf.MultiThreadedDump(Objects, "_Pickle/Graphs/")
    hdf.MergeHDF5("_Pickle/Graphs/")
    hdf.Filename = "_Pickle/Graphs/UNTITLED.hdf5"
    for name, obj in hdf:
        print(name, obj.Trees["nominal"], obj)
    return True
