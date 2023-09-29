from AnalysisTopGNN import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.IO import PickleObject, UnpickleObject
import torch
import NuR.DoubleNu.Floats as Sf
import NuR.Physics.Floats as F
from AnalysisTopGNN.Particles.Particles import Neutrino
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F
from itertools import combinations
import numpy as np
import math
 
_charged_leptons = [11, 13, 15]

mW = 80.385*1000 # MeV : W Boson Mass
mT = 172.5*1000  # MeV : t Quark Mass
mT_GeV = 172.5   # GeV : t Quark Mass
mN = 0           # GeV : Neutrino Mass
device = "cpu"

# Transform all event properties into torch tensors
class SampleTensor:

    def __init__(self, hadronic_groups, leptonic_groups, ev):
        self.device = device
        self.n = len(ev)
        
        self.b_had1 = self.MakeKinematics(hadronic_groups, 0, 0)
        self.b_had2 = self.MakeKinematics(hadronic_groups, 1, 0)
        self.q_had1 = [self.MakeKinematics(hadronic_groups, 0, i) for i in range(1,3)]
        self.q_had2 = [self.MakeKinematics(hadronic_groups, 1, i) for i in range(1,3)]
        self.b_lep1 = self.MakeKinematics(leptonic_groups, 0, 0)
        self.b_lep2 = self.MakeKinematics(leptonic_groups, 1, 0)
        self.lep1 = self.MakeKinematics(leptonic_groups, 0, 1)
        self.lep2 = self.MakeKinematics(leptonic_groups, 1, 1)

        self.mT = self.MakeTensor(mT)
        self.mW = self.MakeTensor(mW)
        self.mN = self.MakeTensor(mN)

        self.MakeEvent(ev)

    def MakeKinematics(self, obj, group, idx):
        return torch.tensor([[i[group][idx].pt, i[group][idx].eta, i[group][idx].phi, i[group][idx].e] for i in obj], dtype = torch.double, device = self.device)

        return group_tensor
    
    def MakeEvent(self, obj):
        self.met = torch.tensor([[ev.met] for ev in obj], dtype = torch.double, device = device)
        self.phi = torch.tensor([[ev.met_phi] for ev in obj], dtype = torch.double, device = device)

    def MakeTensor(self, val):
        return torch.tensor([[val] for i in range(self.n)], dtype = torch.double, device = self.device)

# Group particles into hadronic groups based on invariant mass and partial leptonic groups based on dR
def ParticleGroups(ev):

    groups = {"hadronic": [], "leptonic": []}
    lquarks = []
    bquarks = []
    leptons = []

    for p in ev.TopChildren:
        if abs(p.pdgid) < 5:
            lquarks.append(p)
        elif abs(p.pdgid) == 5:
            bquarks.append(p)
        elif abs(p.pdgid) in _charged_leptons:
            leptons.append(p)

    # Only keep same-sign dilepton events with 4 b's and 4 non-b's
    if len(leptons) != 2 or leptons[0].charge != leptons[1].charge or len(bquarks) != 4 or len(lquarks) != 4:
        return 0

    # Find the group of one b quark and two jets for which the invariant mass is closest to that of a top quark
    closestGroups = []
    while len(bquarks) > 2:
        lowestError = 1e100
        for b in bquarks:
            for pair in combinations(lquarks, 2):
                IM = sum([b, pair[0], pair[1]]).Mass
                if abs(mT_GeV - IM) < lowestError:
                    bestB = b
                    bestQuarkPair = pair
                    lowestError = abs(mT_GeV - IM)
        # Remove last closest group from lists and add them to dictionary
        bquarks.remove(bestB)
        lquarks.remove(bestQuarkPair[0])
        lquarks.remove(bestQuarkPair[1])
        groups["hadronic"].append([bestB, bestQuarkPair[0], bestQuarkPair[1]])

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
        # Remove last closest lepton and b from lists and add them to dictionary
        leptons.remove(closestL)
        bquarks.remove(closestB)
        groups["leptonic"].append([closestB, closestL])

    return groups

# Calculate a metric to determine the best neutrino solution
def Difference(leptonic_groups, neutrinos):
    diff = 0
    for g,group in enumerate(leptonic_groups):
        top_group = sum([group[0], group[1], neutrinos[g]])
        diff += abs(mT_GeV - top_group.Mass)
    return diff

# Transform neutrino solution into Neutrino object
def MakeParticle(inpt):
    Nu = Neutrino()
    Nu.px = inpt[0]
    Nu.py = inpt[1]
    Nu.pz = inpt[2]
    return Nu

# For plotting
def PlotTemplate(nevents, lumi):
    Plots = {
                "yTitle" : "Entries (a.u.)",
                "xMin" : 0, 
                "yMin" : 0, 
                "xMax" : None,
                "xBins" : None,
                "OutputDirectory" : "./Figures_Dilepton_EventStop100/", 
                "Style" : "ATLAS",
                "ATLASLumi" : lumi,
                "NEvents" : nevents
            }
    return Plots


def DileptonAnalysis_withNeutrinoReco(Ana):

    ReconstructedHadTopMass = {"Res": [], "Spec": []}
    ReconstructedLepTopMass = {"Res": [], "Spec": []}
    ReconstructedResonanceMass = []
    numSolutions = []
    event_groups = {"hadronic" : [], "leptonic" : [], "ev" : [], "tops": []}

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
    numSolutions = []

    for ev in Ana:
        
        event = ev.Trees["nominal"]
        nevents += 1

        # Create hadronic/leptonic groups from all particles in the event
        groups = ParticleGroups(event)
        if groups == 0:
            neventsNotPassed += 1
            continue

        lumi += event.Lumi

        event_groups["hadronic"].append(groups["hadronic"])
        event_groups["leptonic"].append(groups["leptonic"])
        event_groups["ev"].append(event)
        event_groups["tops"].append(event.Tops)

    T = SampleTensor(event_groups["hadronic"], event_groups["leptonic"], event_groups["ev"])
    print("Number of events processed: ", T.n)

    # Neutrino reconstruction
    s_ = Sf.SolT(T.b_lep1, T.b_lep2, T.lep1, T.lep2, T.mT, T.mW, T.mN, T.met, T.phi, 1e-12)

    it = -1
    for i in range(T.n):

         # Test if a solution was found
        useEvent = s_[0][i]
        if useEvent != True: 
            numSolutions.append(0)
            neventsNotPassed += 1
            continue
        it += 1
        
        # Collect all solutions and choose one
        neutrinos = []
        nu1, nu2 = s_[1][it], s_[2][it]
        numSolutionsEvent = 0
        for k in range(len(nu1)):
            if sum(nu1[k] + nu2[k]) == 0:
                continue
            numSolutionsEvent += 1
            neutrino1 = MakeParticle(nu1[k].tolist())
            neutrino2 = MakeParticle(nu2[k].tolist())
            neutrinos.append([neutrino1, neutrino2])
        numSolutions.append(numSolutionsEvent)
        
        # Calculate metric to determine best neutrino solution
        close_T = { Difference(event_groups["leptonic"][i], p) : p for p in neutrinos }
        if len(close_T) == 0:
            neventsNotPassed += 1
            continue
        x = list(close_T)
        x.sort()
        closest_nuSol = close_T[x[0]]

        # Make reconstructed tops and assign them to resonance/spectator
        leptonicGroups = [sum([event_groups["leptonic"][i][g][0], event_groups["leptonic"][i][g][1], closest_nuSol[g]]) for g in range(2)]
        if leptonicGroups[0].pt > leptonicGroups[1].pt:
            #print("Leptonic group 0 has largest pt: assigning it to resonance")
            LeptonicResTop = leptonicGroups[0]
            LeptonicSpecTop = leptonicGroups[1]
            nFromRes_leptonicGroup = len([p for p in event_groups["leptonic"][i][0] if event_groups["tops"][i][p.TopIndex].FromRes == 1])
            #print(f"FromRes for this group is {[event_groups['tops'][i][p.TopIndex].FromRes for p in event_groups['leptonic'][i][0]]}")
        else:
            #print("Leptonic group 1 has largest pt: assigning it to resonance")
            LeptonicResTop = leptonicGroups[1]
            LeptonicSpecTop = leptonicGroups[0]
            nFromRes_leptonicGroup = len([p for p in event_groups["leptonic"][i][1] if event_groups["tops"][i][p.TopIndex].FromRes == 1])
            #print(f"FromRes for this group is {[event_groups['tops'][i][p.TopIndex].FromRes for p in event_groups['leptonic'][i][1]]}")
        #print(f"nFromRes_leptonicGroup = {nFromRes_leptonicGroup}")
        if nFromRes_leptonicGroup == 2:
            eff_resonance_lep += 1

        hadronicGroups = [sum(event_groups["hadronic"][i][g]) for g in range(2)]
        if hadronicGroups[0].pt > hadronicGroups[1].pt:
            #print("Best hadronic group has highest pt: assigning it to resonance")
            HadronicResTop = hadronicGroups[0]
            HadronicSpecTop = hadronicGroups[1]
            nFromRes_hadronicGroup = len([p for p in event_groups["hadronic"][i][0] if event_groups["tops"][i][p.TopIndex].FromRes == 1])
            #print(f"FromRes for this group is {[event_groups['tops'][i][p.TopIndex].FromRes for p in event_groups['hadronic'][i][0]]}")
        else:
            #print("Second best hadronic group has highest pt: assigning it to resonance")
            HadronicResTop = hadronicGroups[1]
            HadronicSpecTop = hadronicGroups[0]
            nFromRes_hadronicGroup = len([p for p in event_groups["hadronic"][i][1] if event_groups["tops"][i][p.TopIndex].FromRes == 1])
            #print(f"FromRes for this group is {[event_groups['tops'][i][p.TopIndex].FromRes for p in event_groups['hadronic'][i][1]]}")  
        #print(f"nFromRes_hadronicGroup = {nFromRes_hadronicGroup}")
        if nFromRes_hadronicGroup == 3:
            eff_resonance_had += 1

        if nFromRes_leptonicGroup == 2 and nFromRes_hadronicGroup == 3: 
            eff_resonance += 1

        # Calculate efficiencies of groupings
        if event_groups["leptonic"][i][0][0].TopIndex == event_groups["leptonic"][i][0][1].TopIndex: 
            eff_closestLeptonicGroup += 1
        #     print(f"l/b from closest leptonic group come from same top {event_groups['leptonic'][i][0][0].TopIndex}")
        # else:
        #     print(f"l/b from closest leptonic group come from different tops: {[event_groups['leptonic'][i][0][j].TopIndex for j in range(2)]}")
        
        if event_groups["leptonic"][i][1][0].TopIndex == event_groups["leptonic"][i][1][1].TopIndex: 
            eff_remainingLeptonicGroup += 1
        #     print(f"l/b from second closest leptonic group come from same top {event_groups['leptonic'][i][1][0].TopIndex}")
        # else:
        #     print(f"l/b from second closest leptonic group come from different tops: {[event_groups['leptonic'][i][1][j].TopIndex for j in range(2)]}")

        if event_groups["hadronic"][i][0][0].TopIndex == event_groups["hadronic"][i][0][1].TopIndex and event_groups["hadronic"][i][0][1].TopIndex == event_groups["hadronic"][i][0][2].TopIndex: 
            eff_bestHadronicGroup += 1
        #     print(f"b/q/q from best hadronic group come from same top {event_groups['hadronic'][i][0][0].TopIndex}")
        # else:
        #     print(f"b/q/q from best hadronic group come from different tops: {[event_groups['hadronic'][i][0][j].TopIndex for j in range(3)]}")
        
        if event_groups["hadronic"][i][1][0].TopIndex == event_groups["hadronic"][i][1][1].TopIndex and event_groups["hadronic"][i][1][1].TopIndex == event_groups["hadronic"][i][1][2].TopIndex: 
            eff_remainingHadronicGroup += 1
        #     print(f"b/q/q from remaining hadronic group come from same top {event_groups['hadronic'][i][1][0].TopIndex}")
        # else:
        #     print(f"b/q/q from remaining hadronic group come from different tops: {[event_groups['hadronic'][i][1][j].TopIndex for j in range(3)]}")

        # Calculate masses of tops and resonance
        print(f"Hadronic top mass: res = {HadronicResTop.Mass}, spec = {HadronicSpecTop.Mass}")
        print(f"Leptonic top mass: res = {LeptonicResTop.Mass}, spec = {LeptonicSpecTop.Mass}")
        print(f"Resonance mass: {sum([HadronicResTop, LeptonicResTop]).Mass}")
        ReconstructedHadTopMass["Res"].append(HadronicResTop.Mass)
        ReconstructedHadTopMass["Spec"].append(HadronicSpecTop.Mass)
        ReconstructedLepTopMass["Res"].append(LeptonicResTop.Mass)
        ReconstructedLepTopMass["Spec"].append(LeptonicSpecTop.Mass)
        ReconstructedResonanceMass.append(sum([HadronicResTop, LeptonicResTop]).Mass)

    # Print out efficiencies
    neventsFinal = nevents - neventsNotPassed
    string = ""
    string += f"Number of events passed: {neventsFinal} / {nevents} \n"
    string += "Efficiencies: \n"
    string += f"Closest leptonic group from same top: {eff_closestLeptonicGroup / (neventsFinal)} \n"
    string += f"Remaining leptonic group from same top: {eff_remainingLeptonicGroup / (neventsFinal)} \n"
    string += f"Closest hadronic group from same top: {eff_bestHadronicGroup / (neventsFinal)} \n"
    string += f"Remaining hadronic group from same top: {eff_remainingHadronicGroup / (neventsFinal)} \n"
    string += f"Leptonic decay products correctly assigned to resonance: {eff_resonance_lep / (neventsFinal)} \n"
    string += f"Hadronic decay products correctly assigned to resonance: {eff_resonance_had / (neventsFinal)} \n"
    string += f"All decay products correctly assigned to resonance: {eff_resonance / (neventsFinal)} \n"
    print(string)

    f = open("Dilepton_withNeutrinoReco_efficiencies.txt", "w")
    f.write(string)
    f.close()

    # Plotting
    Plots = PlotTemplate(neventsFinal, lumi)
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

    Plots = PlotTemplate(neventsFinal, lumi)
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

    Plots = PlotTemplate(neventsFinal, lumi)
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

    Plots = PlotTemplate(neventsFinal, lumi)
    Plots["Title"] = "Number of neutrino solutions"
    Plots["xTitle"] = "#"
    Plots["xStep"] = 1
    Plots["xBinCentering"] = True
    Plots["Filename"] = "NumNeutrinoSolutions"
    Plots["Histograms"] = []
    _Plots = {}
    _Plots["xData"] = numSolutions
    Plots["Histograms"].append(TH1F(**_Plots))
    
    X = CombineTH1F(**Plots)
    X.SaveFigure()


direc = "/eos/home-t/tnommens/Processed/Dilepton/ttH_tttt_m1000"
Ana = Analysis()
Ana.InputSample("bsm1000", direc)
Ana.Event = Event
Ana.EventStop = 100
Ana.ProjectName = "Dilepton" + (f"_EventStop{Ana.EventStop}" if Ana.EventStop else "") 
Ana.EventCache = True
Ana.DumpPickle = True 
Ana.chnk = 100
Ana.Launch()

DileptonAnalysis_withNeutrinoReco(Ana)

