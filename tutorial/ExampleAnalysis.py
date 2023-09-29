from AnalysisG import Analysis
from ObjectDefinitions.Event import ExampleEvent
from AnalysisG.Plotting import TH1F

example_sample = "../test/samples/sample1/"

# // ========= Defining running the Event Compiler =========== //
# Sample 1: see test/samples/sample1/smpl1.root 
Ana = Analysis()
Ana.InputSample("sample1", example_sample)
Ana.Event = ExampleEvent # < link the event definition to the framework
Ana.EventCache = False # < Don't create a cache
Ana.Threads = 1 # < how many CPU threads to utilize 
Ana.EventStop = 100 # < how many events to generate 

# Launching can be done via simply running it as an iterator (magic function)
for event in Ana:
    print("This is the current tree: ", event.Tree) # events contain information which tree this is 
    print("This is a hash: ", event.hash) # this is used to uniquely identify the event.
    print("Number of jets: ", event.nJets) # retrieve the event attribute
    for particle in event.Out:
        print(particle) # will print out the particle as a string 
        print(particle.Type) # shows the type of particle this is 
        break
    break

# Now lets plot the masses of all jets in an event
masses = []
for event in Ana:
    event.Out # < jets in our event
    all_jets_summed = sum(event.Out) # produces another jet like object
    masses += [all_jets_summed.Mass/1000] # convert to GeV
    all_jets_summed.px # Can return the cartesian momenta
    all_jets_summed.eta # Pseudo-Rapidity

# Configure the plotting class.
Masses = TH1F()
Masses.xData = masses
Masses.Style = "ATLAS"
Masses.ATLASLumi = 1
Masses.Title = "Summed Jet Masses"
Masses.xTitle = "Mass of combined Jets (GeV)"
Masses.xMin = 0
Masses.xMax = 1000
Masses.xBins = 100
Masses.Filename = "SummedJets"
Masses.OutputDirectory = "ExamplePlots"
Masses.SaveFigure()


