from AnalysisTopGNN import Analysis
from ObjectDefinitions.Event import Event
from AnalysisTopGNN.Plotting import TH1F

# // ======================== Running the Event Compiler ============================= //
# Sample 1: Resonance Top Sample
Ana = Analysis()
Ana.InputSample("bsm4t-1000", "/home/tnom6927/Downloads/samples/tttt/DAOD_TOPQ1.21955717._000003.root")
Ana.Event = Event
Ana.EventCache = True
Ana.Threads = 12
Ana.EventStop = 100 # < How many events to generate
Ana.VerboseLevel = 1
Ana.Launch()

# Sample 2: Adding some Background 
Ana2 = Analysis()
Ana2.InputSample("SingleTop", "/home/tnom6927/Downloads/samples/t/QU_14.root")
Ana2.Event = Event
Ana2.EventCache = True
Ana2.Threads = 12
Ana2.VerboseLevel = 1
Ana2.DumpPickle = True # < Entirely optional if you want to avoid having to recompile each time
Ana2.Launch()

All = Ana + Ana2

ResonanceMass = []
for i in All:
    
    # Access the event properties 
    ev = i.Trees["nominal"]

    # ===== Some nice additional features ===== #
    # Get the event hash
    # hash_ = i.Filename
    
    # Get the ROOT name from which this event originate from
    # rootname = All.HashToROOT(hash_)
    
    # Return a specific event object from the hash 
    # SpecificEvent = All[hash_]
    
    # Check if a given event hash is present in sample:
    # print(hash_ in Ana2)
     
    # Retrieve event object attributes  
    # print(ev.phi)
    # print(ev.met)
    # print(ev.SomeJets)
    # print(ev.Tops)

    # Collect resonance tops 
    resonance = []
    for top in ev.Tops:
        if top.FromResonance == 0:
            continue
        resonance.append(top)

    # Sum tops quarks from resonance.
    Res = sum(resonance)

    # if the list is empty, Res will be 0.
    if Res == 0:
        continue
    ResonanceMass.append(Res.Mass)

Res = TH1F()
Res.xData = ResonanceMass
Res.Title = "Invariant Mass of Resonance Derived from Resonance Tops"
Res.xTitle = "Mass of Resonance (GeV)"
Res.yTitle = "Entries (Arb.)"
Res.xMin = 0 
Res.xStep = 100
Res.Filename = "MassOfResonance"
Res.OutputDirectory = "Example"
Res.SaveFigure()


