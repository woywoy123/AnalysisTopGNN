from AnalysisTopGNN import Analysis
from ObjectDefinitions.Event import Event

# // ======================== Running the Event Compiler ============================= //

#direc = "/atlasgpfs01/usatlas/data/eleboulicaut/ttH_tttt_m1000"
direc = "/usatlas/u/eleboulicaut/ttH_tttt_m1000_tmp/DAOD_TOPQ1.21955717._000001.root"
Ana = Analysis()
Ana.InputSample("bsm1000", direc)
Ana.Event = Event
Ana.EventStop = 2
Ana.ProjectName = "CustomEvents"
Ana.EventCache = True
Ana.DumpPickle = True 
Ana.Threads = 1
Ana.Launch()

for i in Ana:
    
    # Access the event properties 
    ev = i.Trees["nominal"]
     
    # Retrieve event object attributes 
    print("----- New Event -----") 
    print(f"HASH = {i.Filename}\n")
    print(f"CHILDREN = {[c.pdgid for c in ev.Children]}\n")
    print(f"LEPTONS = {[l.pdgid for l in ev.Leptons]}\n")
    print(f"TopIndex = {[l.TopIndex for l in ev.Leptons]}\n")
    print(f"FromRes = {[l.FromRes for l in ev.Leptons]}\n")
    truthJets_pdgid = {i: [parton.pdgid for parton in tj.Parton] for i,tj in enumerate(ev.TruthJets)}
    truthJets_topIndex = {i: [parton.TopIndex for parton in tj.Parton] for i,tj in enumerate(ev.TruthJets)}
    truthJets_fromRes = {i: [parton.FromRes for parton in tj.Parton] for i,tj in enumerate(ev.TruthJets)}
    print(f"TRUTHJETs = {truthJets_pdgid}")
    print(f"TopIndex = {truthJets_topIndex}\n")
    print(f"FromRes = {truthJets_fromRes}\n")

    # Do efficiency calculation ##




