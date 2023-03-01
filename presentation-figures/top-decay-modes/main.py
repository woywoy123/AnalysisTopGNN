from AnalysisTopGNN import Analysis 
from AnalysisTopGNN.Events import Event 
from AnalysisTopGNN.Templates.Selection import Selection 
from AnalysisTopGNN.IO import UnpickleObject
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F 
import sys
import vector
import torch
sys.path.append("../../truth-studies/NeutrinoReconstruction/")
from neutrino_momentum_reconstruction import *
import PyC.NuSol.CUDA as NuC
import PyC.NuSol.Tensors as NuT

class TopCounter(Selection):

    def __init__(self):
        Selection.__init__(self)
        self.DecayMode = {"Had" : 0, "Lep" : 0, "nTop" : 0}
        self.nLepton = {"None" : 0, "1L" : 0, "2L" : 0, "3L" : 0, "4L" : 0, "" : 0, "nEvents" : 0}

    def Strategy(self, event):
        tops = event.Tops
        counter = 0
        for t in tops:
            mode = "Had" if len([c for c in t.Children if abs(c.pdgid) in [11, 13, 15]]) == 0 else "Lep"
            self.DecayMode[mode] += 1
            if mode == "Lep":
                counter += 1
        self.DecayMode["nTop"] += len(tops)
       
        case = "None" if counter == 0 else ""
        case = "1L" if counter == 1 else case
        case = "2L" if counter == 2 else case
        case = "3L" if counter == 3 else case
        case = "4L" if counter == 4 else case
        self.nLepton[case] += 1
        self.nLepton["nEvents"] += 1

class Truth(Selection):
    def __init__(self):
        Selection.__init__(self)
        self.Tops = {"Had1" : [], "Had2" : [], "Lep1" : [], "Lep2" : []}
        self.Neutrinos = {"Lep1" : [], "Lep2" : []}
        self.Leptons = {"Lep1" : [], "Lep2" : []}
        
        self.Event = {"METx" : [], "METy" : [], "MET" : [], "Phi" : []}
        self.MassTopsTC = {"Had1" : [], "Had2" : [], "Lep1" : [], "Lep2" : []}
        self.MassTopsTJ = {"Had1" : [], "Had2" : [], "Lep1" : [], "Lep2" : []}
        self.MassTopsRECO = {"Had1" : [], "Had2" : [], "Lep1" : [], "Lep2" : []}

        self.EventStats = {"Events" : 0, "Tops" : 0, "True2L" : 0}

    def Selection(self, event):
        tops = event.Tops
        counter = 0
        for t in tops:
            counter += len([c for c in t.Children if abs(c.pdgid) in [11, 13, 15]])
        if counter != 2 or len(tops) != 4:
            return False
        
        self.EventStats["True2L"] += 1
        h, l = 0, 0
        for t in tops:
            if len([c for c in t.Children if abs(c.pdgid) in [11, 13, 15]]) > 0:
                l += 1
                self.Tops["Lep" + str(l)].append(t)
                self.Neutrinos["Lep" + str(l)] += [c for c in t.Children if abs(c.pdgid) in [12, 14, 16]]
                self.Leptons["Lep" + str(l)] += [c for c in t.Children if abs(c.pdgid) in [11, 13, 15]]
            else:
                h += 1
                self.Tops["Had" + str(h)].append(t)
        return True 
            
    def PurgeLastEntry(self):
        for i in self.Tops:
            self.Tops[i] = self.Tops[i][:-1]
        self.Event["METx"] = self.Event["METx"][:-1]
        self.Event["METy"] = self.Event["METy"][:-1]
        self.Event["MET"] = self.Event["MET"][:-1]
        self.Event["Phi"] = self.Event["Phi"][:-1]
        for i in self.Neutrinos:
            self.Neutrinos[i] = self.Neutrinos[i][:-1]
            self.Leptons[i] = self.Leptons[i][:-1]
        
        for i in self.MassTopsTJ:
            self.MassTopsTJ[i] = self.MassTopsTJ[i][:-1]
            self.MassTopsRECO[i] = self.MassTopsRECO[i][:-1]


    def Strategy(self, event):
        import PyC.Transform.Floats as TF
        
        tops = event.Tops 
        met = event.met
        phi = event.met_phi
        px, py = TF.Px(met, phi), TF.Py(met, phi)
    
        self.Event["METx"].append(px)
        self.Event["METy"].append(py)
        self.Event["MET"].append(met)
        self.Event["Phi"].append(phi)
        
        for i in self.MassTopsTC:
            self.MassTopsTC[i] += [sum(self.Tops[i][-1].Children).Mass]
        
        remove = False
        for i in self.Tops:
            # Reject if the top has no truth jets matched 
            if len(self.Tops[i][-1].TruthJets) == 0:
                remove = True
            # Reject if the truth jets have more than one top contributions
            for tj in self.Tops[i][-1].TruthJets:
                if len(tj.Tops) != 1:
                    remove = True

            x = [l for l in self.Tops[i][-1].TruthJets] if remove == False else []
            if "Lep" in i and len(x) > 0:
                nu = self.Neutrinos[i][-1]
                lep = self.Leptons[i][-1]
                x.append(nu) 
                x.append(lep)
                x = [sum(x).Mass]

            elif len(x) > 0:
                x = [sum(x).Mass]
            else:
                x = [0]
            self.MassTopsTJ[i] += x

            # Reject if the top has no jets matched 
            if len(self.Tops[i][-1].Jets) == 0:
                remove = True
            # Reject if the truth jets have more than one top contributions
            for j in self.Tops[i][-1].Jets:
                if len(j.Tops) != 1:
                    remove = True

            x = [l for l in self.Tops[i][-1].Jets] if remove == False else []
            if "Lep" in i and len(x) > 0:
                nu = self.Neutrinos[i][-1] 
                lep = self.Leptons[i][-1]
                x.append(nu) 
                x.append(lep)
                x = [sum(x).Mass] 

            elif len(x) > 0:
                x = [sum(x).Mass]
            else:
                x = [0]

            self.MassTopsRECO[i] += x

        if remove:
            self.PurgeLastEntry()
            return "FAILED->"
        self.EventStats["Events"] += 1
        self.EventStats["Tops"] += len(tops)

class NuNu(Selection):

    def __init__(self, TruthContainer):
        Selection.__init__(self)
        self.Tops = TruthContainer.Tops
        self.Event = TruthContainer.Event
    
    def Orignal(self, q1, q2, l1, l2, met_x, met_y, mT, mW):
        l1_v = vector.obj(pt = l1.pt/1000, eta = l1.eta, phi = l1.phi, E = l1.e/1000)
        l2_v = vector.obj(pt = l2.pt/1000, eta = l2.eta, phi = l2.phi, E = l2.e/1000)

        q1_v = vector.obj(pt = q1.pt/1000, eta = q1.eta, phi = q1.phi, E = q1.e/1000)
        q2_v = vector.obj(pt = q2.pt/1000, eta = q2.eta, phi = q2.phi, E = q2.e/1000)
 
        try:
            sol = doubleNeutrinoSolutions((q1_v, q2_v), (l1_v, l2_v), (met_x, met_y), mW**2, mT**2)
            sol = sol.nunu_s
        except:
            return 
        
        return sol


    def __call__(self):
        b, b_ = [], []
        l, l_ = [], []
        met, mass = [], []
        tsolO, tsolCpp, tsolCU = 0, 0, 0
        for i, j, metx, mety, _met, _phi in zip(self.Tops["Lep1"], self.Tops["Lep2"], 
                                                self.Event["METx"], self.Event["METy"], 
                                                self.Event["MET"], self.Event["Phi"]):
            _met = _met.tolist()[0]
            _phi = _phi.tolist()[0]
            l1 = [c for c in i.Children if abs(c.pdgid) in [11, 13, 15]][-1]
            l2 = [c for c in j.Children if abs(c.pdgid) in [11, 13, 15]][-1]
            
            nu1 = [c for c in i.Children if abs(c.pdgid) in [12, 14, 16]][-1]
            nu2 = [c for c in j.Children if abs(c.pdgid) in [12, 14, 16]][-1]
 
            q1 = [c for c in i.Children if abs(c.pdgid) not in [11, 12, 13, 14, 15, 16, 22]][-1]
            q2 = [c for c in j.Children if abs(c.pdgid) not in [11, 12, 13, 14, 15, 16, 22]][-1]
           
            tMass = i.Mass
            WMass = (l1 + nu1).Mass
            self._t1
            solO = self.Orignal(q1, q2, l1, l2, metx, mety, tMass, WMass)
            self._t2
            tsolO += self._TimeStats.pop()
            if solO != None:
                pass
            
            b.append([q1.pt/1000, q1.eta, q1.phi, q1.e/1000])
            b_.append([q2.pt/1000, q2.eta, q2.phi, q2.e/1000])

            l.append([l1.pt/1000, l1.eta, l1.phi, l1.e/1000])
            l_.append([l2.pt/1000, l2.eta, l2.phi, l2.e/1000])
            
            met.append([_met, _phi])
            mass.append([tMass, WMass, 0])
       
        b = torch.tensor(b, dtype = torch.float64, device = "cuda")
        b_ = torch.tensor(b_, dtype = torch.float64, device = "cuda")
        l = torch.tensor(l, dtype = torch.float64, device = "cuda")
        l_ = torch.tensor(l_, dtype = torch.float64, device = "cuda")

        met_ = torch.tensor([[i[0]] for i in met], dtype = torch.float64, device = "cuda")
        phi_ = torch.tensor([[i[1]] for i in met], dtype = torch.float64, device = "cuda")

        mT_ = torch.tensor([[i[0]] for i in mass], dtype = torch.float64, device = "cuda")
        mW_ = torch.tensor([[i[1]] for i in mass], dtype = torch.float64, device = "cuda")
        mNu_ = torch.tensor([[i[2]] for i in mass], dtype = torch.float64, device = "cuda")

        self._t1
        solC = NuC.NuNuPtEtaPhiE(b, b_, l, l_, met_, phi_, mT_, mW_, mNu_, 1e-12)
        self._t2
        tsolCU = self._TimeStats.pop()

        self._t1
        solC = NuT.NuNuPtEtaPhiE(b, b_, l, l_, met_, phi_, mT_, mW_, mNu_, 1e-12)
        self._t2
        tsolCpp = self._TimeStats.pop()
            
        print("SPEED BOOST FACTOR (CPP vs ORIGINAL): ", tsolO/tsolCpp)
        print("SPEED BOOST FACTOR (CUDA vs ORIGINAL): ", tsolO/tsolCU)
        print("SPEED BOOST FACTOR (CPP vs CUDA): ", tsolCpp/tsolCU)



def PlotTemplate():
    plt = {}
    plt["xMin"] = 100
    plt["xMax"] = 250
    plt["xStep"] = 1
    plt["xTitle"] = "Invariant Mass (GeV)"
    plt["yTitle"] = "Entries (arb.)"
    return plt

#Ana = Analysis()
#Ana.InputSample("bsm-1000", "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root")
#Ana.InputSample("bsm-1000-all", "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000")
#Ana.AddSelection("top-count", TopCounter)
#Ana.AddSelection("truth", Truth)
#Ana.MergeSelection("top-count")
#Ana.MergeSelection("truth")
#Ana.Event = Event 
#Ana.EventCache = True 
#Ana.DumpPickle = True 
#Ana.Launch()

x = UnpickleObject("./UNTITLED/Selections/Merged/truth.pkl")

nn = NuNu(x)
nn()


exit()




hsts = []
for i in x.MassTopsTC:
    p = PlotTemplate()
    p["xData"] = x.MassTopsTC[i]
    p["Title"] = i
    hsts.append(TH1F(**p))

p = PlotTemplate()
p["Histograms"] = hsts
p["Title"] = "Top Mass Derived From Truth Children for Dilepton Events"
p["xStep"] = 10
p["Stack"] = True
y = CombineTH1F(**p)
y.Filename = "MassTopsChildren"
y.SaveFigure()

hsts = []
for i in x.MassTopsTJ:
    p = PlotTemplate()
    p["xData"] = x.MassTopsTJ[i]
    p["Title"] = i
    hsts.append(TH1F(**p))

p = PlotTemplate()
p["Histograms"] = hsts
p["Title"] = "Top Mass Derived From Truth Jets (with Truth Neutrino and Lepton if Leptonic)"
p["xStep"] = 10
p["Stack"] = True
y = CombineTH1F(**p)
y.Filename = "MassTopsTruthJets"
y.SaveFigure()

hsts = []
for i in x.MassTopsRECO:
    p = PlotTemplate()
    p["xData"] = x.MassTopsRECO[i]
    p["Title"] = i
    hsts.append(TH1F(**p))

p = PlotTemplate()
p["Histograms"] = hsts
p["Title"] = "Top Mass Derived From Reco Jets (with Truth Neutrino and Lepton if Leptonic)"
p["xStep"] = 10
p["Stack"] = True
y = CombineTH1F(**p)
y.Filename = "MassTopsJets"
y.SaveFigure()

print(x.EventStats)


t = UnpickleObject("./UNTITLED/Selections/Merged/top-count.pkl")
nEvents = t.nLepton["nEvents"]
L0 = (t.nLepton["None"] / nEvents) * 100
L1 = (t.nLepton["1L"] / nEvents) * 100
L2 = (t.nLepton["2L"] / nEvents) * 100
L3 = (t.nLepton["3L"] / nEvents) * 100
L4 = (t.nLepton["4L"] / nEvents) * 100

ntops = t.DecayMode["nTop"]
Had = (t.DecayMode["Had"] / ntops) * 100
Lep = (t.DecayMode["Lep"] / ntops) * 100

print("Decay Mode (%): (HAD)", Had, " (LEP) ", Lep)
print("Lepton Multiplicity (%): (0L)", L0, " (1L)", L1, " (2L)", L2, " (3L)", L3, " (4L)", L4)


