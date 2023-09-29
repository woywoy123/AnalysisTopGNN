from AnalysisG import Analysis
from ObjectDefinitions.Event import ExampleEvent
from AnalysisG.Plotting import TH1F


# // ========= Defining running the Event Compiler =========== //
# Sample 1: see test/samples/sample1/smpl1.root 
example_sample1 = "../test/samples/sample1/"
Ana1 = Analysis()
Ana1.InputSample("sample1", example_sample1)
Ana1.Event = ExampleEvent # < link the event definition to the framework
Ana1.EventCache = False # < Don't create a cache
Ana1.Threads = 1 # < how many CPU threads to utilize 
Ana1.EventStop = 100 # < how many events to generate 
Ana1.Launch() # < launches the Analysis 

# Sample 2: 
example_sample2 = "../test/samples/single_lepton/"
Ana2 = Analysis()
Ana2.InputSample("sample2", {example_sample2 : ["*"]})
Ana2.Event = ExampleEvent
Ana2.EventCache = False
Ana2.Threads = 1
Ana2.EventStop = 100
Ana2.DisablePyAMI = True # Disables the pyami search
Ana2.DisablePyAMI = False

for i in Ana2:
    # return the absolute path of the ROOT file 
    # if you authenticate to PyAmi using the bash command:
    # AUTH_PYAMI, the framework will attempt to scrape the 
    # meta data of your samples to find the associated DAOD sample
    # and any other details e.g. total events, cross section etc.
    try:
        print(i.DatasetName)
        print(i.nFiles)
        print(i.total_events)
        print(i.short)
        print(i.DAOD)
        print(i.cross_section)
        print(i.Files)
        print(i.generator_tune)
        print(i.keywords)
        print(i.isMC)
        print(i.version)
    except AttributeError:
        print(i.ROOT)
    break

# We can also merge samples together into a single Analysis
AnotherAnalysis = Ana1 + Ana2
assert len(AnotherAnalysis) == len(Ana1) + len(Ana2)
assert len(AnotherAnalysis) == 200

# The above would NOT result in event duplication!
# See this example:
l1 = len(Ana1)
l_dup = sum([Ana1 for _ in range(4)])
assert len(l_dup) == l1

# We can also do a reverse look-up of the event
for i in Ana1:
    hash_ = i.hash
    break

event = Ana1[hash_]
assert event.hash == hash_

# What about if we want all the events associated with a particular ROOT file?
# Well this is easy! 

for i in Ana1:
    ROOT = i.ROOT
    break

events = AnotherAnalysis[ROOT] # < will scan for all events associated with this ROOT
print(events)

# What if we want to check if a ROOT or event is in some analysis instance?
val = hash_ in Ana2
assert val == False # shouldnt have the event
assert hash_ in AnotherAnalysis # This should because it is the sum of Ana1 and Ana2
assert hash_ in Ana1


