from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.IO import PickleObject, UnpickleObject
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F
from itertools import combinations

PDGID = { 1 : "d"        ,  2 : "u"             ,  3 : "s", 
          4 : "c"        ,  5 : "b"             , 11 : "e", 
         12 : "$\\nu_e$" , 13 : "$\mu$"         , 14 : "$\\nu_{\mu}$", 
         15 : "$\\tau$"  , 16 : "$\\nu_{\\tau}$", 21 : "g", 
         22 : "$\\gamma$"}
 
_leptons = [11, 12, 13, 14, 15, 16]
_charged_leptons = [11, 13, 15]
topMass = 172.5

def PlotTemplate(nevents, lumi):
    Plots = {
                "yTitle" : "Entries (a.u.)",
                "xMin" : 0, 
                "yMin" : 0, 
                "xMax" : None,
                "xBins" : None,
                "OutputDirectory" : "./Figures/", 
                "Style" : "ATLAS",
                "ATLASLumi" : lumi,
                "NEvents" : nevents
            }
    return Plots


def DileptonAnalysis(Ana):

    ReconstructedHadTopMass = {"Res": [], "Spec": []}
    ReconstructedLepTopMass = {"Res": [], "Spec": []}
    ReconstructedResonanceMass = []

    nevents = 0
    neventsNotPassed = 0
    lumi = 0
    eff_closestLeptonicGroup = 0
    eff_remainingLeptonicGroup = 0
    eff_bestHadronicGroup = 0
    eff_remainingHadronicGroup = 0
    eff_resonance_had = 0
    eff_resonance_lep = 0
    eff_resonance = 0

    for ev in Ana:

        print("---New event---")
        
        event = ev.Trees["nominal"]
        nevents += 1
        lumi += event.Lumi
    
        lquarks = []
        bquarks = []
        leptons = []

        for p in event.TopChildren:
            if abs(p.pdgid) < 5:
                lquarks.append(p)
            elif abs(p.pdgid) == 5:
                bquarks.append(p)
            elif abs(p.pdgid) in _charged_leptons:
                leptons.append(p)
        print(f"Number of light quarks: {len(lquarks)}")
        print(f"Number of b quarks: {len(bquarks)}")
        print(f"Number of leptons: {len(leptons)}")
        print(f"Charge of leptons: {[l.charge for l in leptons]}")

        # Only keep same-sign dilepton events with 4 b's and 4 non-b's
        if len(leptons) != 2 or leptons[0].charge != leptons[1].charge or len(bquarks) != 4 or len(lquarks) != 4:
            neventsNotPassed += 1
            continue
        
        # Match leptons with their closest b quarks
        closestPairs = []
        while leptons != []:
            lowestDR = 100
            for l in leptons:
                for b in bquarks:
                    if l.DeltaR(b) < lowestDR: # Possibility of adding requirement: if np.sign(b.charge) != np.sign(l.charge)
                        lowestDR = l.DeltaR(b)
                        closestB = b
                        closestL = l
            # Removing last closest lepton and b from lists and add them to closestPairs
            leptons.remove(closestL)
            bquarks.remove(closestB)
            closestPairs.append([closestB, closestL])
        closestLeptonicGroup = sum(closestPairs[0])
        remainingLeptonicGroup = sum(closestPairs[1])

        ## Assign group with closest dR to resonance
        # LeptonicResTop = closestLeptonicGroup
        # LeptonicSpecTop = remainingLeptonicGroup
        # nFromRes_leptonicGroup = len([p for p in closestPairs[0] if event.Tops[p.TopIndex].FromRes == 0])
        # if nFromRes_leptonicGroup == 2:
        #     eff_resonance_lep += 1

        ## Assign group with largest pT to resonance -> best option
        if closestLeptonicGroup.pt > remainingLeptonicGroup.pt:
            print("Lepton/b pair with smallest dR has largest pT")
            LeptonicResTop = closestLeptonicGroup
            LeptonicSpecTop = remainingLeptonicGroup
            nFromRes_leptonicGroup = len([p for p in closestPairs[0] if event.Tops[p.TopIndex].FromRes == 0]) # FromRes variable is inverted when using TopIndex
        else:
            print("Remaining lepton/b pair has largest pT")
            LeptonicResTop = remainingLeptonicGroup
            LeptonicSpecTop = closestLeptonicGroup
            nFromRes_leptonicGroup = len([p for p in closestPairs[1] if event.Tops[p.TopIndex].FromRes == 0])
        print(f"{nFromRes_leptonicGroup} particles in the leptonic resonance group are actually from resonance")
        if nFromRes_leptonicGroup == 2:
            eff_resonance_lep += 1

        ## Assign group with smallest eta to resonance
        # if abs(closestLeptonicGroup.eta) < abs(remainingLeptonicGroup.eta):
        #     print("Pair with smallest dR has smallest eta")
        #     LeptonicResTop = closestLeptonicGroup
        #     LeptonicSpecTop = remainingLeptonicGroup
        #     nFromRes_leptonicGroup = len([p for p in closestPairs[0] if event.Tops[p.TopIndex].FromRes == 0])
        # else:
        #     print("Remaining pair has smallest eta")
        #     LeptonicResTop = remainingLeptonicGroup
        #     LeptonicSpecTop = closestLeptonicGroup
        #     nFromRes_leptonicGroup = len([p for p in closestPairs[1] if event.Tops[p.TopIndex].FromRes == 0])
        # if nFromRes_leptonicGroup == 2:
        #     eff_resonance_lep += 1

        # Check if objects within each pair come from the same top
        if closestPairs[0][0].TopIndex == closestPairs[0][1].TopIndex: 
            eff_closestLeptonicGroup += 1
            print(f"Lepton and b in closest group are from same top: {closestPairs[0][0].TopIndex}")
        else:
            print(f"Lepton and b in closest group are from different tops: {closestPairs[0][0].TopIndex} and {closestPairs[0][1].TopIndex}")
        if closestPairs[1][0].TopIndex == closestPairs[1][1].TopIndex: 
            eff_remainingLeptonicGroup += 1
            print(f"Lepton and b in remaining group are from same top: {closestPairs[1][0].TopIndex}")
        else:
            print(f"Lepton and b in remaining group are from different tops: {closestPairs[1][0].TopIndex} and {closestPairs[1][1].TopIndex}")

        # Find the group of one b quark and two jets for which the invariant mass is closest to that of a top quark
        closestGroups = []
        while bquarks != []:
            lowestError = 1e100
            for b in bquarks:
                for pair in combinations(lquarks, 2):
                    IM = sum([b, pair[0], pair[1]]).CalculateMass()
                    if abs(topMass - IM) < lowestError:
                        bestB = b
                        bestQuarkPair = pair
                        lowestError = abs(topMass - IM)
            # Remove last closest group from lists and add them to closestGroups
            bquarks.remove(bestB)
            lquarks.remove(bestQuarkPair[0])
            lquarks.remove(bestQuarkPair[1])
            closestGroups.append([bestB, bestQuarkPair[0], bestQuarkPair[1]])
        bestHadronicGroup = sum(closestGroups[0])
        remainingHadronicGroup = sum(closestGroups[1])
        
        ## Assign group with IM closest to topMass to resonance
        # HadronicResTop = bestHadronicGroup
        # HadronicSpecTop = remainingHadronicGroup
        # nFromRes_hadronicGroup = len([p for p in closestGroups[0] if event.Tops[p.TopIndex].FromRes == 0])
        # if nFromRes_hadronicGroup == 3:
        #     eff_resonance_had += 1

        ## Assign group with largest pT to resonance -> best option
        if bestHadronicGroup.pt > remainingHadronicGroup.pt:
            print("Group with closest mass to top has largest pT")
            HadronicResTop = bestHadronicGroup
            HadronicSpecTop = remainingHadronicGroup
            nFromRes_hadronicGroup = len([p for p in closestGroups[0] if event.Tops[p.TopIndex].FromRes == 0])
        else:
            print("Remaining group has largest pT")
            HadronicResTop = remainingHadronicGroup
            HadronicSpecTop = bestHadronicGroup
            nFromRes_hadronicGroup = len([p for p in closestGroups[1] if event.Tops[p.TopIndex].FromRes == 0])
        print(f"{nFromRes_hadronicGroup} particles in the hadronic resonance group are actually from resonance")
        if nFromRes_hadronicGroup == 3:
            eff_resonance_had += 1

        ## Assign group with smallest eta to resonance
        # if abs(bestHadronicGroup.eta) < abs(remainingHadronicGroup.eta):
        #     print("Group with closest mass to top has smallest eta")
        #     HadronicResTop = bestHadronicGroup
        #     HadronicSpecTop = remainingHadronicGroup
        #     nFromRes_hadronicGroup = len([p for p in closestGroups[0] if event.Tops[p.TopIndex].FromRes == 0])
        # else:
        #     print("Remaining group has smallest eta")
        #     HadronicResTop = remainingHadronicGroup
        #     HadronicSpecTop = bestHadronicGroup
        #     nFromRes_hadronicGroup = len([p for p in closestGroups[1] if event.Tops[p.TopIndex].FromRes == 0])
        # if nFromRes_hadronicGroup == 3:
        #     eff_resonance_had += 1
        
        ## Assign groups with dR between them closest to pi to resonance
        # leptonicGroups = [closestLeptonicGroup, remainingLeptonicGroup]
        # hadronicGroups = [bestHadronicGroup, remainingHadronicGroup]
        # resonanceGroups = []
        # indices = []
        # while leptonicGroups != []:
        #     lowestError = 1e100
        #     for il, lepGroup in enumerate(leptonicGroups):
        #         print(f"Leptonic group {il}")
        #         for ih, hadGroup in enumerate(hadronicGroups):
        #             print(f"Hadronic group {ih}")
        #             dR = lepGroup.DeltaR(hadGroup)
        #             print(f"Delta R between them: {dR}")
        #             if abs(dR - 3.14) < lowestError:
        #                 bestLep = lepGroup
        #                 bestHad = hadGroup
        #                 bestIndexLep = il
        #                 bestIndexHad = ih
        #                 lowestError = abs(dR - 3.14)
        #                 print("Lowest error so far")
        #     print("Removing last best group from lists and adding them to resonanceGroups")
        #     leptonicGroups.remove(bestLep)
        #     hadronicGroups.remove(bestHad)
        #     resonanceGroups.append([bestLep, bestHad])
        #     indices.append([bestIndexLep, bestIndexHad])

        # LeptonicResTop = resonanceGroups[0][0]
        # LeptonicSpecTop = resonanceGroups[1][0]
        # HadronicResTop = resonanceGroups[0][1]
        # HadronicSpecTop = resonanceGroups[1][1]
        # nFromRes_leptonicGroup = len([p for p in closestPairs[indices[0][0]] if event.Tops[p.TopIndex].FromRes == 0])
        # nFromRes_hadronicGroup = len([p for p in closestGroups[indices[0][1]] if event.Tops[p.TopIndex].FromRes == 0])
        # if nFromRes_leptonicGroup == 2:
        #     eff_resonance_lep += 1
        # if nFromRes_hadronicGroup == 3:
        #     eff_resonance_had += 1

        # Check if objects within each group come from the same top
        if closestGroups[0][0].TopIndex == closestGroups[0][1].TopIndex and closestGroups[0][1].TopIndex == closestGroups[0][2].TopIndex: 
            eff_bestHadronicGroup += 1
            print(f"All particles in best hadronic group are from same top: {closestGroups[0][0].TopIndex}")
        else: 
            print(f"Particles in best hadronic group are from different tops: {closestGroups[0][0].TopIndex}, {closestGroups[0][1].TopIndex} and {closestGroups[0][2].TopIndex}")
        
        if closestGroups[1][0].TopIndex == closestGroups[1][1].TopIndex and closestGroups[1][1].TopIndex == closestGroups[1][2].TopIndex: 
            eff_remainingHadronicGroup += 1
            print(f"All particles in remaining hadronic group are from same top: {closestGroups[1][0].TopIndex}")
        else:
            print(f"Particles in remaining hadronic group are from different tops: {closestGroups[1][0].TopIndex}, {closestGroups[1][1].TopIndex} and {closestGroups[1][2].TopIndex}")

        if nFromRes_leptonicGroup == 2 and nFromRes_hadronicGroup == 3: 
            eff_resonance += 1
            print("All particles assigned to resonance are actually from resonance")

        # Calculate masses of tops and resonance
        print(f"Hadronic top mass: res = {HadronicResTop.CalculateMass()}, spec = {HadronicSpecTop.CalculateMass()}")
        print(f"Leptonic top mass: res = {LeptonicResTop.CalculateMass()}, spec = {LeptonicSpecTop.CalculateMass()}")
        print(f"Resonance mass: {sum([HadronicResTop, LeptonicResTop]).CalculateMass()}")
        ReconstructedHadTopMass["Res"].append(HadronicResTop.CalculateMass())
        ReconstructedHadTopMass["Spec"].append(HadronicSpecTop.CalculateMass())
        ReconstructedLepTopMass["Res"].append(LeptonicResTop.CalculateMass())
        ReconstructedLepTopMass["Spec"].append(LeptonicSpecTop.CalculateMass())
        ReconstructedResonanceMass.append(sum([HadronicResTop, LeptonicResTop]).CalculateMass())

    # Print out efficiencies
    print(f"Number of events not passed: {neventsNotPassed} / {nevents}")
    print("Efficiencies:")
    print(f"Closest leptonic group from same top: {eff_closestLeptonicGroup / (nevents-neventsNotPassed) }")
    print(f"Remaining leptonic group from same top: {eff_remainingLeptonicGroup / (nevents-neventsNotPassed)}")
    print(f"Closest hadronic group from same top: {eff_bestHadronicGroup / (nevents-neventsNotPassed)}")
    print(f"Remaining hadronic group from same top: {eff_remainingHadronicGroup / (nevents-neventsNotPassed)}")
    print(f"Leptonic decay products correctly assigned to resonance: {eff_resonance_lep / (nevents-neventsNotPassed)}")
    print(f"Hadronic decay products correctly assigned to resonance: {eff_resonance_had / (nevents-neventsNotPassed)}")
    print(f"All decay products correctly assigned to resonance: {eff_resonance / (nevents-neventsNotPassed)}")

    # Plotting
    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Reconstructed Hadronic Top Mass"
    Plots["xTitle"] = "Mass (GeV)"
    Plots["xBins"] = 200
    Plots["xMin"] = 0
    Plots["xMax"] = 200
    Plots["Filename"] = "RecoHadTopMass"
    Plots["Histograms"] = []

    for i in ReconstructedHadTopMass:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = ReconstructedHadTopMass[i]
        Plots["Histograms"].append(TH1F(**_Plots))
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Reconstructed Leptonic Top Mass"
    Plots["xTitle"] = "Mass (GeV)"
    Plots["xBins"] = 200
    Plots["xMin"] = 0
    Plots["xMax"] = 200
    Plots["Filename"] = "RecoLepTopMass"
    Plots["Histograms"] = []

    for i in ReconstructedLepTopMass:
        _Plots = {}
        _Plots["Title"] = i
        _Plots["xData"] = ReconstructedLepTopMass[i]
        Plots["Histograms"].append(TH1F(**_Plots))
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()

    Plots = PlotTemplate(nevents, lumi)
    Plots["Title"] = "Reconstructed Resonance Mass"
    Plots["xTitle"] = "Mass (GeV)"
    Plots["xBins"] = 150
    Plots["xMin"] = 0
    Plots["xMax"] = 1500
    Plots["Filename"] = "RecoResMass"
    Plots["Histograms"] = []
    _Plots = {}
    _Plots["xData"] = ReconstructedResonanceMass
    Plots["Histograms"].append(TH1F(**_Plots))
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()

