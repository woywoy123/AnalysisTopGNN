from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.IO import PickleObject, UnpickleObject
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F
from itertools import combinations
import numpy as np
import sys
sys.path.insert(0, '/eos/user/e/elebouli/BSM4tops/FourTopsAnalysis/models/NeutrinoReconstructionOriginal')
from neutrino_momentum_reconstruction import doubleNeutrinoSolutions
import vector
import math

PDGID = { 1 : "d"        ,  2 : "u"             ,  3 : "s", 
          4 : "c"        ,  5 : "b"             , 11 : "e", 
         12 : "$\\nu_e$" , 13 : "$\mu$"         , 14 : "$\\nu_{\mu}$", 
         15 : "$\\tau$"  , 16 : "$\\nu_{\\tau}$", 21 : "g", 
         22 : "$\\gamma$"}
 
_leptons = [11, 12, 13, 14, 15, 16]
_charged_leptons = [11, 13, 15]
_neutrinos = [12, 14, 16]
topMass = 172.5

def PlotTemplate(nevents, lumi):
    Plots = {
                "yTitle" : "Entries (a.u.)",
                "xMin" : 0, 
                "yMin" : 0, 
                "xMax" : None,
                "xBins" : None,
                "OutputDirectory" : "./Figures_withNeutrinoReco_truthMET_EventStop100/", 
                "Style" : "ATLAS",
                "ATLASLumi" : lumi,
                "NEvents" : nevents
            }
    return Plots


def DileptonAnalysis_withNeutrinoReco(Ana):

    ReconstructedHadTopMass = {"Res": [], "Spec": []}
    ReconstructedLepTopMass = {"Res": [], "Spec": []}
    ReconstructedResonanceMass = []
    MissingET = {"From ntuples": [], "From neg sum of truth objects": [], "From neg sum of truth objects incl rad": [], "From truth neutrinos": []}
    MissingETDiff = {"From neg sum of truth objects": [], "From neg sum of truth objects incl rad": [], "From truth neutrinos": []}
    numSolutions = []

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
    
    nDifferentSolutionsPermutations = 0

    for ev in Ana:
        
        event = ev.Trees["nominal"]
        nevents += 1
        lumi += event.Lumi
    
        lquarks = []
        bquarks = []
        leptons = []
        neutrinos = []

        for p in event.TopChildren:
            if abs(p.pdgid) < 5:
                lquarks.append(p)
            elif abs(p.pdgid) == 5:
                bquarks.append(p)
            elif abs(p.pdgid) in _charged_leptons:
                leptons.append(p)
            elif abs(p.pdgid) in _neutrinos:
                neutrinos.append(p)

        # Only keep same-sign dilepton events with 4 b's and 4 non-b's
        if len(leptons) != 2 or leptons[0].charge != leptons[1].charge or len(bquarks) != 4 or len(lquarks) != 4:
            neventsNotPassed += 1
            continue
        
        print(f"---Event {nevents}---")

        #print(f"Number of top children = {len(event.TopChildren)}")
        #print(f"PDGIDs are {[p.pdgid for p in event.TopChildren]}")
        all_particles = sum(leptons + bquarks + lquarks)
        met = all_particles.pt / 1000.
        met_x = -(all_particles.pt / 1000.) * np.cos(all_particles.phi)
        met_y = -(all_particles.pt / 1000.) * np.sin(all_particles.phi)

        ## This gives the same result as above
        # neg_sum_x = [-p.pt * np.cos(p.phi) for p in (leptons + bquarks + lquarks)]
        # neg_sum_y = [-p.pt * np.sin(p.phi) for p in (leptons + bquarks + lquarks)]
        # met_x2 = sum(neg_sum_x)
        # met_y2 = sum(neg_sum_y)
        # met2 = math.sqrt(pow(met_x2, 2) + pow(met_y2, 2))

        all_particles_withRad = sum([p for p in event.TopChildren if p.pdgid not in _neutrinos])
        met_withRad = all_particles_withRad.pt / 1000.
        met_withRad_x = -(all_particles_withRad.pt / 1000.) * np.cos(all_particles_withRad.phi)
        met_withRad_y = -(all_particles_withRad.pt / 1000.) * np.sin(all_particles_withRad.phi)

        event_met = event.met / 1000.
        event_met_x = (event.met / 1000.) * np.cos(event.met_phi)
        event_met_y = (event.met / 1000.) * np.sin(event.met_phi)

        # print(f"MET, MET_x and MET_y from event = {event.met}, {event_met_x}, {event_met_y}")
        # print(f"MET, MET_x and MET_y calculated from partons = {met}, {met_x}, {met_y}")
        # print(f"MET, MET_x and MET_y calculated from partons including radiation = {met_withRad}, {met_withRad_x}, {met_withRad_y}")
        MissingET["From ntuples"].append(event_met)
        MissingET["From neg sum of truth objects"].append(met)
        MissingET["From neg sum of truth objects incl rad"].append(met_withRad)
        MissingETDiff["From neg sum of truth objects"].append(met - event_met)
        MissingETDiff["From neg sum of truth objects incl rad"].append(met_withRad - event_met)
        if len(neutrinos) > 0:
            #print(f"Number of neutrinos: {len(neutrinos)}")
            nus = sum(neutrinos)
            MissingET["From truth neutrinos"].append(nus.pt/1000.)
            MissingETDiff["From truth neutrinos"].append(nus.pt/1000. - event_met)
            #print(f"MET, MET_x and MET_y from neutrinos = {nus.pt}, {nus.pt * np.cos(nus.phi)}, {nus.pt * np.sin(nus.phi)}")
        #print(f"Sum of tops pT = {sum([t for t in event.Tops]).pt}")
        

        # Find the group of one b quark and two jets for which the invariant mass is closest to that of a top quark
        closestGroups = []
        while len(bquarks) > 2:
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

        # Check if objects within each group come from the same top
        if closestGroups[0][0].TopIndex == closestGroups[0][1].TopIndex and closestGroups[0][1].TopIndex == closestGroups[0][2].TopIndex: 
            eff_bestHadronicGroup += 1
        
        if closestGroups[1][0].TopIndex == closestGroups[1][1].TopIndex and closestGroups[1][1].TopIndex == closestGroups[1][2].TopIndex: 
            eff_remainingHadronicGroup += 1

        # Assign group with largest pT to resonance 
        if bestHadronicGroup.pt > remainingHadronicGroup.pt:
            #print("Best hadronic group has highest pt: assigning it to resonance")
            HadronicResTop = bestHadronicGroup
            HadronicSpecTop = remainingHadronicGroup
            nFromRes_hadronicGroup = len([p for p in closestGroups[0] if event.Tops[p.TopIndex].FromRes == 0])
            #print(f"FromRes for this group is {[event.Tops[p.TopIndex].FromRes for p in closestGroups[0]]}")
        else:
            #print("Second best hadronic group has highest pt: assigning it to resonance")
            HadronicResTop = remainingHadronicGroup
            HadronicSpecTop = bestHadronicGroup
            nFromRes_hadronicGroup = len([p for p in closestGroups[1] if event.Tops[p.TopIndex].FromRes == 0])
            #print(f"FromRes for this group is {[event.Tops[p.TopIndex].FromRes for p in closestGroups[1]]}")
        #print(f"nFromRes_hadronicGroup = {nFromRes_hadronicGroup}")
        if nFromRes_hadronicGroup == 3:
            eff_resonance_had += 1

        # Match remaining leptons with their closest b quarks
        closestPairs = []
        while leptons != []:
            lowestDR = 100
            for l in leptons:
                for b in bquarks:
                    if l.DeltaR(b) < lowestDR: 
                        lowestDR = l.DeltaR(b)
                        closestB = b
                        closestL = l
            # Removing last closest lepton and b from lists and add them to closestPairs
            leptons.remove(closestL)
            bquarks.remove(closestB)
            closestPairs.append([closestB, closestL])

        # Check if objects within each pair come from the same top
        if closestPairs[0][0].TopIndex == closestPairs[0][1].TopIndex: 
            eff_closestLeptonicGroup += 1

        if closestPairs[1][0].TopIndex == closestPairs[1][1].TopIndex: 
            eff_remainingLeptonicGroup += 1

        # Turn Children objects into vector objects
        closestPairsVec = [[vector.obj(pt=closestPairs[j][i].pt/1000., phi=closestPairs[j][i].phi, eta=closestPairs[j][i].eta, E=closestPairs[j][i].e/1000.) for i in range(len(closestPairs[j]))] for j in range(len(closestPairs))]

        # Neutrino reconstruction
        try:
            print("Calling doubleNeutrinoSolutions for order (b0,b1), (l0,l1)...")
            nu_solutions = doubleNeutrinoSolutions((closestPairsVec[0][0], closestPairsVec[1][0]), (closestPairsVec[0][1], closestPairsVec[1][1]), (met_x, met_y))
            nunu_s = nu_solutions.nunu_s
            numSolutions.append(len(nunu_s))
        except np.linalg.LinAlgError:
            numSolutions.append(0)
            continue

        # Testing the effect of changing the order and b quarks and leptons in neutrino reconstruction
        try:
            print("Calling doubleNeutrinoSolutions for order (b1,b0), (l1,l0)...")
            nu_solutions_perm = doubleNeutrinoSolutions((closestPairsVec[1][0], closestPairsVec[0][0]), (closestPairsVec[1][1], closestPairsVec[0][1]), (met_x, met_y))
            nunu_s_perm = nu_solutions_perm.nunu_s
        except np.linalg.LinAlgError:
            continue

        different = False
        if len(nunu_s) != len(nunu_s_perm): 
            #print(f"Permutations give different number of solutions: {len(nunu_s)} vs {len(nunu_s_perm)}.")
            different = True
        else:
            for solution in nunu_s:
                for nu_s in solution:
                    for j,pj in enumerate(nu_s):
                        match = any([True for s in range(len(nunu_s_perm)) for n in range(len(nunu_s_perm[s])) if abs(pj - nunu_s_perm[s][n][j]) < 10e-4])
                        if not match: different = True

        if different == True: 
            nDifferentSolutionsPermutations += 1
            print("Permutations give different solutions!!")
            # print(f"b0 = {closestPairsVec[0][0]}")
            # print(f"b1 = {closestPairsVec[1][0]}")
            # print(f"l0 = {closestPairsVec[0][1]}")
            # print(f"l1 = {closestPairsVec[1][1]}")
            # print(f"met_x = {met_x}")
            # print(f"met_y = {met_y}")
            # print(f"Solutions with (b0,b1), (l0,l1): \n{nunu_s}")
            # print(f"Solutions with (b1,b0), (l1,l0): \n{nunu_s_perm}")


        #print(f"Number of neutrino solutions: {numSolutions[-1]}")
        
        # Choose best solution
        lowestError = 1e100
        for s,solution in enumerate(nunu_s):
            #print(f"Solution {s}")
            groups = []
            nFromRes = []
            for i, nu_s in enumerate(solution):
                #print(f"Neutrino {i}")
                nu_vec = vector.obj(px=nu_s[0], py=nu_s[1], pz=nu_s[2], E=math.sqrt(sum(pow(element, 2) for element in nu_s)))
                group = nu_vec + closestPairsVec[i][0] + closestPairsVec[i][1]
                #print(f"Reconstructed top mass: {group.mass}")
                groups.append(group)
                nFromRes.append(len([p for p in closestPairs[i] if event.Tops[p.TopIndex].FromRes == 0]))
                #print(f"FromRes for partial leptonic group is {[event.Tops[p.TopIndex].FromRes for p in closestPairs[i]]}")
            error = abs(topMass - groups[0].mass) + abs(topMass - groups[1].mass)
            if error < lowestError:
                #print("Lowest error so far")
                leptonicGroups = groups
                lowestError = error
                nFromRes_leptonicGroups = nFromRes

        # Assign group with largest pT to resonance -> best option
        if leptonicGroups[0].pt > leptonicGroups[1].pt:
            #print("Leptonic group 0 has largest pt: assigning it to resonance")
            LeptonicResTop = leptonicGroups[0]
            LeptonicSpecTop = leptonicGroups[1]
            nFromRes_leptonicGroup = nFromRes_leptonicGroups[0]
        else:
            #print("Leptonic group 1 has largest pt: assigning it to resonance")
            LeptonicResTop = leptonicGroups[1]
            LeptonicSpecTop = leptonicGroups[0]
            nFromRes_leptonicGroup = nFromRes_leptonicGroups[1]
        #print(f"nFromRes_leptonicGroup = {nFromRes_leptonicGroup}")
        if nFromRes_leptonicGroup == 2:
            eff_resonance_lep += 1

        if nFromRes_leptonicGroup == 2 and nFromRes_hadronicGroup == 3: 
            eff_resonance += 1

        # Calculate masses of tops and resonance
        HadronicResTopVec = vector.obj(pt=HadronicResTop.pt/1000., eta=HadronicResTop.eta, phi=HadronicResTop.phi, E=HadronicResTop.e/1000.)
        HadronicSpecTopVec = vector.obj(pt=HadronicSpecTop.pt/1000., eta=HadronicSpecTop.eta, phi=HadronicSpecTop.phi, E=HadronicSpecTop.e/1000.)
        #print(f"Hadronic top mass: res = {HadronicResTopVec.mass}, spec = {HadronicSpecTopVec.mass}")
        #print(f"Leptonic top mass: res = {LeptonicResTop.mass}, spec = {LeptonicSpecTop.mass}")
        #print(f"Resonance mass: {(HadronicResTopVec + LeptonicResTop).mass}")
        ReconstructedHadTopMass["Res"].append(HadronicResTopVec.mass)
        ReconstructedHadTopMass["Spec"].append(HadronicSpecTopVec.mass)
        ReconstructedLepTopMass["Res"].append(LeptonicResTop.mass)
        ReconstructedLepTopMass["Spec"].append(LeptonicSpecTop.mass)
        ReconstructedResonanceMass.append((HadronicResTopVec + LeptonicResTop).mass)

    # Print out efficiencies
    #print(f"Number of events not passed: {neventsNotPassed} / {nevents}")
    #print("Efficiencies:")
    #print(f"Closest leptonic group from same top: {eff_closestLeptonicGroup / (nevents-neventsNotPassed) }")
    #print(f"Remaining leptonic group from same top: {eff_remainingLeptonicGroup / (nevents-neventsNotPassed)}")
    #print(f"Closest hadronic group from same top: {eff_bestHadronicGroup / (nevents-neventsNotPassed)}")
    #print(f"Remaining hadronic group from same top: {eff_remainingHadronicGroup / (nevents-neventsNotPassed)}")
    #print(f"Leptonic decay products correctly assigned to resonance: {eff_resonance_lep / (nevents-neventsNotPassed)}")
    #print(f"Hadronic decay products correctly assigned to resonance: {eff_resonance_had / (nevents-neventsNotPassed)}")
    #print(f"All decay products correctly assigned to resonance: {eff_resonance / (nevents-neventsNotPassed)}")

    print(f"Number of events where neutrino solutions were different for permutations: {nDifferentSolutionsPermutations}")

    # Plotting
    # Plots = PlotTemplate(nevents, lumi)
    # Plots["Title"] = "Reconstructed Hadronic Top Mass"
    # Plots["xTitle"] = "Mass (GeV)"
    # Plots["xBins"] = 200
    # Plots["xMin"] = 0
    # Plots["xMax"] = 200
    # Plots["Filename"] = "RecoHadTopMass"
    # Plots["Histograms"] = []

    # for i in ReconstructedHadTopMass:
    #     _Plots = {}
    #     _Plots["Title"] = i
    #     _Plots["xData"] = ReconstructedHadTopMass[i]
    #     Plots["Histograms"].append(TH1F(**_Plots))
    
    # X = CombineTH1F(**Plots)
    # X.SaveFigure()

    # Plots = PlotTemplate(nevents, lumi)
    # Plots["Title"] = "Reconstructed Leptonic Top Mass"
    # Plots["xTitle"] = "Mass (GeV)"
    # Plots["xBins"] = 200
    # Plots["xMin"] = 0
    # Plots["xMax"] = 200
    # Plots["Filename"] = "RecoLepTopMass"
    # Plots["Histograms"] = []

    # for i in ReconstructedLepTopMass:
    #     _Plots = {}
    #     _Plots["Title"] = i
    #     _Plots["xData"] = ReconstructedLepTopMass[i]
    #     Plots["Histograms"].append(TH1F(**_Plots))
    
    # X = CombineTH1F(**Plots)
    # X.SaveFigure()

    # Plots = PlotTemplate(nevents, lumi)
    # Plots["Title"] = "Reconstructed Resonance Mass"
    # Plots["xTitle"] = "Mass (GeV)"
    # Plots["xBins"] = 150
    # Plots["xMin"] = 0
    # Plots["xMax"] = 1500
    # Plots["Filename"] = "RecoResMass"
    # Plots["Histograms"] = []
    # _Plots = {}
    # _Plots["xData"] = ReconstructedResonanceMass
    # Plots["Histograms"].append(TH1F(**_Plots))
    
    # X = CombineTH1F(**Plots)
    # X.SaveFigure()

    # Plots = PlotTemplate(nevents, lumi)
    # Plots["Title"] = "Number of neutrino solutions"
    # Plots["xTitle"] = "#"
    # Plots["xStep"] = 1
    # Plots["xBinCentering"] = True
    # Plots["Filename"] = "NumNeutrinoSolutions"
    # Plots["Histograms"] = []
    # _Plots = {}
    # _Plots["xData"] = numSolutions
    # Plots["Histograms"].append(TH1F(**_Plots))
    
    # X = CombineTH1F(**Plots)
    # X.SaveFigure()

    # Plots = PlotTemplate(nevents, lumi)
    # Plots["Title"] = "Missing Transverse Energy"
    # Plots["xTitle"] = "MET (GeV)"
    # Plots["xBins"] = 200
    # Plots["xMin"] = 0
    # Plots["xMax"] = 1000
    # Plots["Filename"] = "MET_withRad"
    # Plots["Histograms"] = []

    # for i in MissingET:
    #     _Plots = {}
    #     _Plots["Title"] = i
    #     _Plots["xData"] = MissingET[i]
    #     Plots["Histograms"].append(TH1F(**_Plots))
    
    # X = CombineTH1F(**Plots)
    # X.SaveFigure()

    # Plots = PlotTemplate(nevents, lumi)
    # Plots["Title"] = "Missing Transverse Energy Difference"
    # Plots["xTitle"] = "MET calculated - MET from ntuples (GeV)"
    # Plots["xBins"] = 200
    # Plots["xMin"] = -500
    # Plots["xMax"] = 500
    # Plots["Filename"] = "METDiff_withRad"
    # Plots["Histograms"] = []

    # for i in MissingETDiff:
    #     _Plots = {}
    #     _Plots["Title"] = i
    #     _Plots["xData"] = MissingETDiff[i]
    #     Plots["Histograms"].append(TH1F(**_Plots))
    
    # X = CombineTH1F(**Plots)
    # X.SaveFigure()

