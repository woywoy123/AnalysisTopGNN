from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.IO import PickleObject, UnpickleObject
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F

PDGID = { 1 : "d"        ,  2 : "u"             ,  3 : "s", 
          4 : "c"        ,  5 : "b"             , 11 : "e", 
         12 : "$\\nu_e$" , 13 : "$\mu$"         , 14 : "$\\nu_{\mu}$", 
         15 : "$\\tau$"  , 16 : "$\\nu_{\\tau}$", 21 : "g", 
         22 : "$\\gamma$"}
 
_leptons = [11, 12, 13, 14, 15, 16]
_charged_leptons = [11, 13, 15]
topMass = 172.5


def TestFromRes(Ana):

    for ev in Ana:

        print("---New event---")
        
        event = ev.Trees["nominal"]

        tops = event.Tops 
        print("Accessing top.index", [t.index for t in tops])
        print("Accessing top.FromRes", [t.FromRes for t in tops])
        print("Accessing child.TopIndex from tops.Children", [[c.TopIndex for c in t.Children] for t in tops])
        print("Accessing child.TopIndex from Event.TopChildren", [c.TopIndex for c in event.TopChildren])
        print("Using child.TopIndex as an index to access list", [[tops[c.TopIndex].index for c in t.Children] for t in tops]) 

        # Method 1
        lquarks = []
        bquarks = []
        leptons = []
        for p in event.TopChildren:
            if abs(p.pdgid) < 5:
                lquarks.append([p, event.Tops[p.TopIndex].FromRes])
            elif abs(p.pdgid) == 5:
                bquarks.append([p, event.Tops[p.TopIndex].FromRes])
            elif abs(p.pdgid) in _charged_leptons:
                leptons.append([p, event.Tops[p.TopIndex].FromRes])

        # Method 2
        lquarks2 = []
        bquarks2 = []
        leptons2 = []
        for t in event.Tops:
            for p in t.Children:
                if abs(p.pdgid) < 5:
                    lquarks2.append([p, t.FromRes])
                elif abs(p.pdgid) == 5:
                    bquarks2.append([p, t.FromRes])
                elif abs(p.pdgid) in _charged_leptons:
                    leptons2.append([p, t.FromRes])

        print("-> Method 1:")
        print(f"Light quarks: {lquarks}")
        print(f"b quarks: {bquarks}")
        print(f"Leptons: {leptons}")
        print("-> Method 2:")
        print(f"Light quarks: {lquarks2}")
        print(f"b quarks: {bquarks2}")
        print(f"Leptons: {leptons2}")
        exit()

        

