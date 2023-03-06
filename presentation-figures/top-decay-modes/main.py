from AnalysisTopGNN import Analysis 
from AnalysisTopGNN.Events import Event 
from AnalysisTopGNN.Templates.Selection import Selection 
from AnalysisTopGNN.IO import UnpickleObject
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F 
from AnalysisTopGNN.Templates import ParticleTemplate
import sys
import math
import vector
import torch
sys.path.append("../../truth-studies/NeutrinoReconstruction/")
from neutrino_momentum_reconstruction import *
import PyC.NuSol.CUDA as NuC
import PyC.NuSol.Tensors as NuT


class Neutrino(ParticleTemplate):
    def __init__(self, px=None, py=None, pz=None):
        self.Type = "nu"
        ParticleTemplate.__init__(self)
        self.px = px
        self.py = py
        self.pz = pz

    @property
    def phi(self):
        return self._phi

    @property
    def eta(self):
        return self._eta

    @property
    def pt(self):
        return self._pt

def MakeNu(sols):
    nu1 = Neutrino()
    nu1.px = sols[0]*1000
    nu1.py = sols[1]*1000
    nu1.pz = sols[2]*1000
    return nu1


def ParticleTensor(lst):
    out = []
    for p in lst:
        out.append([p.pt/1000, p.eta, p.phi, p.e/1000])
    t = torch.tensor(out, dtype=torch.float64, device = "cuda")
    t_ = t.to("cpu")
    return t, t_

def ParticleVector(p):
    return vector.obj(pt = p.pt/1000, eta = p.eta, phi = p.phi, E = p.e/1000)

def GetParticle(t, lst, invert = False):
    if invert:
        return[c for c in t.Children if abs(c.pdgid) not in lst][-1]
    return [c for c in t.Children if abs(c.pdgid) in lst][-1]

def FitToTruth(t1, t2, nus):
    fit = {}
    for i, j in nus:
        diff = 0
        diff += math.log(abs(t1._px - i.px)/1000)
        diff += math.log(abs(t2._px - j.px)/1000)

        diff += math.log(abs(t1._py - i.py)/1000)
        diff += math.log(abs(t2._py - j.py)/1000)

        diff += math.log(abs(t1._pz - i.pz)/1000)
        diff += math.log(abs(t2._pz - j.pz)/1000)
        fit[diff] = [i, j]
        
        # Swap the order. We just want to know whether the solution pairs are present in truth.
        diff = 0
        diff += math.log(abs(t1._px - j.px)/1000)
        diff += math.log(abs(t2._px - i.px)/1000)

        diff += math.log(abs(t1._py - j.py)/1000)
        diff += math.log(abs(t2._py - i.py)/1000)

        diff += math.log(abs(t1._pz - j.pz)/1000)
        diff += math.log(abs(t2._pz - i.pz)/1000)
        fit[diff] = [j, i] 
    
    f = list(fit)
    f.sort()
    return fit[f[0]], f[0]

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
        self.Neutrinos = TruthContainer.Neutrinos
       
        self.NsolChildren = {"Original" : [], "CPU" : [], "Non-CUDA" : [], "CUDA" : []}
        self.Chi2Children = {"Original" : [], "CPU" : [], "Non-CUDA" : [], "CUDA" : []}
        self.MassChildren = {"Original" : [], "CPU" : [], "Non-CUDA" : [], "CUDA" : [], "TRUTH": []}

        self.NsolTruthJets = {"Original" : [], "CPU" : [], "Non-CUDA" : [], "CUDA" : []}
        self.Chi2TruthJets = {"Original" : [], "CPU" : [], "Non-CUDA" : [], "CUDA" : []}
        self.MassTruthJets = {"Original" : [], "CPU" : [], "Non-CUDA" : [], "CUDA" : [], "TRUTH": []}

        self.NsolJets = {"Original" : [], "CPU" : [], "Non-CUDA" : [], "CUDA" : []}
        self.Chi2Jets = {"Original" : [], "CPU" : [], "Non-CUDA" : [], "CUDA" : []}
        self.MassJets = {"Original" : [], "CPU" : [], "Non-CUDA" : [], "CUDA" : [], "TRUTH": []}
        self.Time = {"Original" : [], "CPU" : [], "Non-CUDA" : [], "CUDA" : []}
   
    def Orignal(self, q1, q2, l1, l2, met_x, met_y, mT, mW):
        try:
            sol = doubleNeutrinoSolutions((q1, q2), (l1, l2), (met_x, met_y), mW**2, mT**2)
            sol = sol.nunu_s
        except:
            return 
        return sol

    def MakeOriginal(self, V1):
        out_v = []
        self._t1
        for i in range(len(V1["mT"])):
            out_v.append(self.Orignal(V1["b1"][i], V1["b2"][i], V1["l1"][i], V1["l2"][i], V1["metx"][i], V1["mety"][i], V1["mT"][i], V1["mW"][i]))
        self._t2
        self.Time["Original"].append(self._TimeStats[-1])
        return self.MakeNu(out_v)
 
    def MakeNu(self, sol1, sol2 = None, sol3 = None):
        out = []
        if sol2 == None:
            for i in sol1:
                if i == None:
                    out.append(None)
                    continue
                out.append([[MakeNu(p), MakeNu(q)] for p, q in i])
        else:
            it = 0
            for sk in sol1:
                if sk == True:
                    out.append(None)
                    continue
                n1, n2 = sol2[it], sol3[it]
                it+=1 
                out.append([[MakeNu(x.tolist()), MakeNu(y.tolist())] for x, y in zip(n1, n2) if x.sum(-1) != 0 and y.sum(-1) != 0])
        return out

    def CompareSols(self, output):
        for i in output:
            output[i] = [len(k) for k in self.Nus[i] if k != None] 

    def BestNuNu(self, Truth, output):
        for key in output:
            for i in range(len(Truth["nu1"])):
                if self.Nus[key][i] == None:
                    continue
                nu1, nu2 = Truth["nu1"][i], Truth["nu2"][i]
                if len(self.Nus[key][i]) == 0:
                    self.Nus[key][i] = None
                    continue
                else:
                    nu, chi2 = FitToTruth(nu1, nu2, self.Nus[key][i]) 
                self.Nus[key][i] = nu 
                output[key].append(chi2)
    
    def Mass(self, Truth, output):
        output["TRUTH"] =  [ (i+j+k).Mass for i, j, k in zip(Truth["nu1"], Truth["l1"], Truth["b1"]) ]
        output["TRUTH"] += [ (i+j+k).Mass for i, j, k in zip(Truth["nu2"], Truth["l2"], Truth["b2"]) ]
        
        for i in self.Nus:
            t1 = [(n[0]+l+b).Mass for n, l, b in zip(self.Nus[i], Truth["l1"], Truth["b1"]) if n != None]
            t2 = [(n[1]+l+b).Mass for n, l, b in zip(self.Nus[i], Truth["l2"], Truth["b2"]) if n != None]           
            output[i] += t1 + t2

  
    def MakeTensor(self, V1, key):
        self._t1
        if key == "CPU" or key == "Non-CUDA":
            sol = NuT.NuNuPtEtaPhiE(V1["b1"], V1["b2"], V1["l1"], V1["l2"], V1["met"], V1["phi"], V1["mT"], V1["mW"], V1["mNu"], 1e-12)
        if key == "CUDA":
            sol = NuC.NuNuPtEtaPhiE(V1["b1"], V1["b2"], V1["l1"], V1["l2"], V1["met"], V1["phi"], V1["mT"], V1["mW"], V1["mNu"], 1e-12)
        self._t2
        self.Time[key].append(self._TimeStats[-1])
        return self.MakeNu(sol[0], sol[1], sol[2]) 

    def Prepare(self, lst):
        Cv = {c : None for c in lst if c not in ["metP", "metC"]}
        Ct = {c : None for c in lst if c not in ["metC", "metP"]}
        Ct_ = {c : None for c in lst if c not in ["metC", "metP"]}
        for i in Cv:
            Cv[i] = [ParticleVector(k) for k in lst[i]]
            Ct[i], Ct_[i] = ParticleTensor(lst[i])
        mT = [(i + j + t).Mass for i, j, t in zip(lst["b1"], lst["nu1"], lst["l1"])]
        mW = [(j + t).Mass for j, t in zip(lst["nu1"], lst["l1"])]

        Ct["mT"] = torch.tensor(mT, dtype=torch.float64, device = "cuda").view(-1, 1)
        Ct["mW"] = torch.tensor(mW, dtype=torch.float64, device = "cuda").view(-1, 1)
        Ct["mNu"] = torch.tensor([0 for i in lst["metP"]], dtype=torch.float64, device = "cuda").view(-1, 1)
        Ct["met"] = torch.tensor([i[0] for i in lst["metP"]], dtype=torch.float64, device = "cuda").view(-1, 1)
        Ct["phi"] = torch.tensor([i[1] for i in lst["metP"]], dtype=torch.float64, device = "cuda").view(-1, 1)

        Ct_["mT"] = torch.tensor(mT, dtype=torch.float64, device = "cpu").view(-1, 1)
        Ct_["mW"] = torch.tensor(mW, dtype=torch.float64, device = "cpu").view(-1, 1)
        Ct_["mNu"] = torch.tensor([0 for i in lst["metP"]], dtype=torch.float64, device = "cpu").view(-1, 1)
        Ct_["met"] = torch.tensor([i[0] for i in lst["metP"]], dtype=torch.float64, device = "cpu").view(-1, 1)
        Ct_["phi"] = torch.tensor([i[1] for i in lst["metP"]], dtype=torch.float64, device = "cpu").view(-1, 1)
        
        Cv["metx"] = [c[0] for c in lst["metC"]]
        Cv["mety"] = [c[1] for c in lst["metC"]]
        Cv["mT"] = mT
        Cv["mW"] = mW

        return Cv, Ct, Ct_

    def __call__(self):
        Children = {"b1" : [], "b2" : [], "l1" : [], "l2" : [], "nu1" : [], "nu2" : [], "metC" : [], "metP" : []}
        TruthJet = {"b1" : [], "b2" : [], "l1" : [], "l2" : [], "nu1" : [], "nu2" : [], "metC" : [], "metP" : []}
        Jet = {"b1" : [], "b2" : [], "l1" : [], "l2" : [], "nu1" : [], "nu2" : [], "metC" : [], "metP" : []}
        self.nEvents = {"Children" : 0, "TruthJets" : 0, "Jets" : 0}
        for i, j, metx, mety, _met, _phi in zip(self.Tops["Lep1"], self.Tops["Lep2"], self.Event["METx"], self.Event["METy"], self.Event["MET"], self.Event["Phi"]):
            _met, _phi = _met.tolist()[0]/1000, _phi.tolist()[0]
            metx, mety = metx/1000, mety/1000

            l1, l2 = GetParticle(i, [11, 13, 15]), GetParticle(j, [11, 13, 15])
            nu1, nu2 = GetParticle(i, [12, 14, 16]), GetParticle(j, [12, 14, 16])
            q1, q2 = GetParticle(i, [11, 12, 13, 14, 15, 16], True), GetParticle(j, [11, 12, 13, 14, 15, 16, 22], True)
            
            for k, p in zip([q1, q2, l1, l2, nu1, nu2, [metx, mety], [_met, _phi]], ["b1", "b2", "l1", "l2", "nu1", "nu2", "metC", "metP"]):
                Children[p].append(k)
            self.nEvents["Children"] += 1
            b1, b2 = [c for c in i.TruthJets if c.is_b_var == 5], [c for c in j.TruthJets if c.is_b_var == 5]
            if len(b1) != 1 or len(b2) != 1:
                continue
            for k, p in zip([b1[-1], b2[-1], l1, l2, nu1, nu2, [metx, mety], [_met, _phi]], ["b1", "b2", "l1", "l2", "nu1", "nu2", "metC", "metP"]):
                TruthJet[p].append(k)
            self.nEvents["TruthJets"] += 1
            b1, b2 = [c for c in i.Jets if c.btagged == 1], [c for c in j.Jets if c.btagged == 1]
            if len(b1) != 1 or len(b2) != 1:
                continue
            for k, p in zip([b1[-1], b2[-1], l1, l2, nu1, nu2, [metx, mety], [_met, _phi]], ["b1", "b2", "l1", "l2", "nu1", "nu2", "metC", "metP"]):
                Jet[p].append(k)
            self.nEvents["Jets"] += 1

        Cv, Ct, Ct_ = self.Prepare(Children) 
        self.Nus = {}
        self.Nus["Original"] = self.MakeOriginal(Cv)
        self.Nus["CPU"] = self.MakeTensor(Ct_, "CPU")
        self.Nus["Non-CUDA"] = self.MakeTensor(Ct, "Non-CUDA")       
        self.Nus["CUDA"] = self.MakeTensor(Ct, "CUDA")    
        self.CompareSols(self.NsolChildren)
        self.BestNuNu(Children, self.Chi2Children)
        self.Mass(Children, self.MassChildren)

        Cv, Ct, Ct_ = self.Prepare(TruthJet) 
        self.Nus = {}
        self.Nus["Original"] = self.MakeOriginal(Cv)
        self.Nus["CPU"] = self.MakeTensor(Ct_, "CPU")
        self.Nus["Non-CUDA"] = self.MakeTensor(Ct, "Non-CUDA")       
        self.Nus["CUDA"] = self.MakeTensor(Ct, "CUDA")    
        self.CompareSols(self.NsolTruthJets)
        self.BestNuNu(TruthJet, self.Chi2TruthJets)
        self.Mass(TruthJet, self.MassTruthJets)

        Cv, Ct, Ct_ = self.Prepare(Jet) 
        self.Nus = {}
        self.Nus["Original"] = self.MakeOriginal(Cv)
        self.Nus["CPU"] = self.MakeTensor(Ct_, "CPU")
        self.Nus["Non-CUDA"] = self.MakeTensor(Ct, "Non-CUDA")       
        self.Nus["CUDA"] = self.MakeTensor(Ct, "CUDA")    
        self.CompareSols(self.NsolJets)
        self.BestNuNu(Jet, self.Chi2Jets)
        self.Mass(Jet, self.MassJets)
 
def PlotTemplate():
    plt = {}
    plt["xMin"] = 100
    plt["xMax"] = 250
    plt["xStep"] = 1
    plt["xTitle"] = "Invariant Mass (GeV)"
    plt["yTitle"] = "Entries (arb.)"
    return plt

Ana = Analysis()
#Ana.InputSample("bsm-1000", "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root")
#Ana.InputSample("bsm-1000-all", "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000/")
Ana.InputSample("sm", "/home/tnom6927/Downloads/LISA/LisaSamples/user.esitniko/user.esitniko.32411527._000001.output.root")
Ana.AddSelection("top-count", TopCounter)
Ana.AddSelection("truth", Truth)
Ana.MergeSelection("top-count")
Ana.MergeSelection("truth")
Ana.Event = Event 
Ana.EventCache = True 
Ana.DumpPickle = True 
Ana.Launch()

exit()
x = UnpickleObject("./UNTITLED/Selections/Merged/truth.pkl")

nn = NuNu(x)
nn()

its = {
    "Children" : [nn.NsolChildren, nn.Chi2Children, nn.MassChildren], 
    "TruthJets" : [nn.NsolTruthJets, nn.Chi2TruthJets, nn.MassTruthJets], 
    "Reco-Jets" : [nn.NsolJets, nn.Chi2Jets, nn.MassJets]
}


i = 0 
print("Orignal ", nn.Time["Original"][i], " CPU ", nn.Time["CPU"][i], " Non-CUDA ",  nn.Time["Non-CUDA"][i], " CUDA ", nn.Time["CUDA"][i], " Events ", nn.nEvents["Children"])
print("(Children) SPEED (Original/CPU): " + str(nn.Time["Original"][i]/nn.Time["CPU"][i]))
print("(Children) SPEED (Original/Non-CUDA): " + str(nn.Time["Original"][i]/nn.Time["Non-CUDA"][i]))
print("(Children) SPEED (Original/CUDA): " + str(nn.Time["Original"][i]/nn.Time["CUDA"][i]))
print("(Children) SPEED (CPU/CUDA): " + str(nn.Time["CPU"][i]/nn.Time["CUDA"][i]))
print("(Children) SPEED (Non-CUDA/CUDA): " + str(nn.Time["Non-CUDA"][i]/nn.Time["CUDA"][i]))

print("")
i = 1
print("Orignal ", nn.Time["Original"][i], " CPU ", nn.Time["CPU"][i], " Non-CUDA ",  nn.Time["Non-CUDA"][i], " CUDA ", nn.Time["CUDA"][i], " Events ", nn.nEvents["TruthJets"])
print("(TruthJets) SPEED (Original/CPU): " + str(nn.Time["Original"][i]/nn.Time["CPU"][i]))
print("(TruthJets) SPEED (Original/Non-CUDA): " + str(nn.Time["Original"][i]/nn.Time["Non-CUDA"][i]))
print("(TruthJets) SPEED (Original/CUDA): " + str(nn.Time["Original"][i]/nn.Time["CUDA"][i]))
print("(TruthJets) SPEED (CPU/CUDA): " + str(nn.Time["CPU"][i]/nn.Time["CUDA"][i]))
print("(TruthJets) SPEED (Non-CUDA/CUDA): " + str(nn.Time["Non-CUDA"][i]/nn.Time["CUDA"][i]))

print("")
i = 2
print("Orignal ", nn.Time["Original"][i], " CPU ", nn.Time["CPU"][i], " Non-CUDA ",  nn.Time["Non-CUDA"][i], " CUDA ", nn.Time["CUDA"][i], " Events ", nn.nEvents["Jets"])
print("(Jets) SPEED (Original/CPU): " + str(nn.Time["Original"][i]/nn.Time["CPU"][i]))
print("(Jets) SPEED (Original/Non-CUDA): " + str(nn.Time["Original"][i]/nn.Time["Non-CUDA"][i]))
print("(Jets) SPEED (Original/CUDA): " + str(nn.Time["Original"][i]/nn.Time["CUDA"][i]))
print("(Jets) SPEED (CPU/CUDA): " + str(nn.Time["CPU"][i]/nn.Time["CUDA"][i]))
print("(Jets) SPEED (Non-CUDA/CUDA): " + str(nn.Time["Non-CUDA"][i]/nn.Time["CUDA"][i]))


for key in its:
    hst = []
    p = PlotTemplate()
    p["xData"] = its[key][2]["Original"]
    p["Title"] = "Reconstructed"
    hst.append(TH1F(**p))

    p = PlotTemplate()
    p["xData"] = its[key][2]["TRUTH"]
    p["Title"] = "Truth"
    hst.append(TH1F(**p))

    p = PlotTemplate()
    p["Histograms"] = hst
    p["Title"] = "Reconstructed Invariant Top Mass From Reconstructed Neutrinos - " + key
    p["xStep"] = 10
    y = CombineTH1F(**p)
    y.Filename = "Mass" + key + "NuNu_OriginalOnly"
    y.SaveFigure()


for i in its:
    hst = []
    for key in its[i][0]:
        p = PlotTemplate()
        p["xData"] = its[i][0][key]
        p["Title"] = key
        hst.append(TH1F(**p))
    
    p = PlotTemplate()
    p["Histograms"] = hst
    p["Title"] = "Number of Obtained Solutions for Different Algorithm Implementations - " + i
    p["xStep"] = 1
    p["xMin"] = 0
    p["xMax"] = 6
    p["xTitle"] = "Number of Solutions"
    p["xBinCentering"] = True
    y = CombineTH1F(**p)
    y.Filename = i + "_nSols"
    y.SaveFigure()
    
    hst = []
    for key in its[i][1]:
        p = PlotTemplate()
        p["xData"] = its[i][1][key]
        p["Title"] = key
        hst.append(TH1F(**p))
    
    p = PlotTemplate()
    p["Histograms"] = hst
    p["xTitle"] = "log(Chi)"
    p["Title"] = "Error Between True Neutrino Pairs and Reconstructed Neutrinos - " + i
    p["xStep"] = 5
    p["xMin"] = 0
    p["xMax"] = None
    y = CombineTH1F(**p)
    y.Filename = i + "_LogChi"
    y.SaveFigure()
    
    hst = []
    for key in its[i][2]:
        p = PlotTemplate()
        p["xData"] = its[i][2][key]
        p["Title"] = key
        hst.append(TH1F(**p))
    
    p = PlotTemplate()
    p["Histograms"] = hst
    p["Title"] = "Reconstructed Invariant Top Mass From Neutrinos - " + i
    p["xStep"] = 10
    p["xMin"] = 100
    p["xMax"] = 250
    y = CombineTH1F(**p)
    y.Filename = "Mass" + i + "NuNu"
    y.SaveFigure()
    
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


