from AnalysisG import Analysis
from ObjectDefinitions.Event import ExampleEvent
from AnalysisG.Plotting import TH1F

# // ======================== Running the Event Compiler ============================= //
# Sample 1: Resonance Top Sample
Ana = Analysis()
Ana.InputSample("bsm4t-1000", "<some sample directory>")
Ana.Event = ExampleEvent
Ana.EventCache = False
Ana.Threads = 1
Ana.EventStop = 100 # < How many events to generate
Ana.Launch

# Sample 2: Adding some Background 
Ana2 = Analysis()
Ana2.InputSample("SingleTop", "<some sample directory>")
Ana2.Event = Event
Ana2.EventCache = True # < whether to store the events 
Ana2.Threads = 12
Ana2.Verbose = 1
Ana2.Launch

All = Ana + Ana2

ResonanceMass = []
for ev in All:
    
    # Access the event properties 
    ev.Tree

    # ===== Some nice additional features ===== #
    # Get the event hash
    # hash_ = i.hash
    
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


