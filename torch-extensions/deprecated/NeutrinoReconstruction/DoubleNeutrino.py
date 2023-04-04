from AnalysisTopGNN import Analysis
from AnalysisTopGNN.Events import Event 
from AnalysisTopGNN.IO import PickleObject, UnpickleObject
import ROOT as r
import torch
import NuR.DoubleNu.Floats as Sf
import NuR.Physics.Floats as F
from neutrino_momentum_reconstruction_python3 import doubleNeutrinoSolutions
import numpy as np
from time import time
from AnalysisTopGNN.Particles.Particles import Neutrino
import math
from AnalysisTopGNN.Plotting import TH1F, TH2F, CombineTH1F

mW = 80.385*1000 # MeV : W Boson Mass
mT = 172.5*1000  # MeV : t Quark Mass
mN = 0           # GeV : Neutrino Mass
device = "cpu"

def CompareNumerical(r_ori, r_pyt, string):
    print("(" + string + ") -> Original: ", r_ori, " ||  Pytorch: ", r_pyt, " || Error (%): ", 100*abs(r_pyt - r_ori)/r_ori)

class SampleTensor:

    def __init__(self, b, mu, ev, top):
        self.device = device
        self.n = len(b)
        
        self.b = self.MakeKinematics(0, b)
        self.b_ = self.MakeKinematics(1, b)
        self.mu = self.MakeKinematics(0, mu)
        self.mu_ = self.MakeKinematics(1, mu)
        
        self.mT = torch.tensor([[top[i][0].Mass * 1000] for i in range(self.n)], dtype = torch.double, device = self.device)
        self.mW = self.MakeTensor(mW)
        self.mN = self.MakeTensor(mN)

        self.MakeEvent(ev)

    def MakeKinematics(self, idx, obj):
        return torch.tensor([[i[idx].pt, i[idx].eta, i[idx].phi, i[idx].e] for i in obj], dtype = torch.double, device = self.device)
    
    def MakeEvent(self, obj):
        self.met = torch.tensor([[ev.met] for ev in obj], dtype = torch.double, device = device)
        self.phi = torch.tensor([[ev.met_phi] for ev in obj], dtype = torch.double, device = device)

    def MakeTensor(self, val):
        return torch.tensor([[val] for i in range(self.n)], dtype = torch.double, device = self.device)

class SampleROOT:
    def __init__(self, b, mu, ev, top):

        self.n = len(ev)
        self.b = [self.MakeKinematics(0, i) for i in b]
        self.b_ = [self.MakeKinematics(1, i) for i in b]       

        self.mu = [self.MakeKinematics(0, i) for i in mu]
        self.mu_ = [self.MakeKinematics(1, i) for i in mu]       

        self.met_x = []
        self.met_y = []
        
        for i in ev:
            x, y = self.MakeEvent(i)
            self.met_x.append(x)
            self.met_y.append(y)

        self.mT = [top[i][0].Mass*1000 for i in range(self.n)] 
        self.mW = [mW for i in range(self.n)]
        self.mN = [mN for i in range(self.n)]

    def MakeKinematics(self, idx, obj):
        r_ = r.TLorentzVector()
        r_.SetPtEtaPhiE(obj[idx].pt, obj[idx].eta, obj[idx].phi, obj[idx].e)
        return r_

    def MakeEvent(self, obj):
        x = F.ToPx(obj.met, obj.met_phi, "cpu").tolist()[0][0]
        y = F.ToPy(obj.met, obj.met_phi, "cpu").tolist()[0][0]
        return x, y

def Difference(tru, pred):
    diff = 0
    for i in range(2):
        diff += ( (tru[i].pt - pred[i]._pt) / tru[i].pt )**2 
        diff += ( (tru[i].eta - pred[i]._eta) / tru[i].eta )**2
        diff += ( (tru[i].phi - pred[i]._phi) / tru[i].phi )**2
        diff += ( (tru[i].e - pred[i]._e) / tru[i].e )**2
    return math.sqrt(diff)

def MakeParticle(inpt):
    Nu = Neutrino()
    Nu.px = inpt[0]
    Nu.py = inpt[1]
    Nu.pz = inpt[2]
    return Nu

def ParticleCollectors(ev):
    t1 = [ t for t in ev.Tops if t.LeptonicDecay][0]
    t2 = [ t for t in ev.Tops if t.LeptonicDecay][1]
    
    out = []
    prt = { abs(p.pdgid) : p for p in t1.Children }
    b = prt[5]
    lep = [prt[i] for i in [11, 13, 15] if i in prt][0]
    nu = [prt[i] for i in [12, 14, 16] if i in prt][0]
    out.append([b, lep, nu, t1])
    
    prt = { abs(p.pdgid) : p for p in t2.Children }
    b = prt[5]
    lep = [prt[i] for i in [11, 13, 15] if i in prt][0]
    nu = [prt[i] for i in [12, 14, 16] if i in prt][0]
    out.append([b, lep, nu, t2])

    return out

direc = "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000/"
Ana = Analysis()
Ana.InputSample("bsm1000", direc)
Ana.Event = Event
Ana.EventCache = True
Ana.DumpPickle = True 
Ana.chnk = 100
Ana.Launch()

it = 0
vl = {"b" : [], "lep" : [], "nu" : [], "ev" : [], "t" : []}
for i in Ana:
    ev = i.Trees["nominal"]
    tops = [ t for t in ev.Tops if t.LeptonicDecay]

    if len(tops) == 2:
        k = ParticleCollectors(ev)
        vl["b"].append(  [k[0][0], k[1][0]])
        vl["lep"].append([k[0][1], k[1][1]])
        vl["nu"].append( [k[0][2], k[1][2]])
        vl["t"].append(  [k[0][3], k[1][3]])
        vl["ev"].append(ev)

T = SampleTensor(vl["b"], vl["lep"], vl["ev"], vl["t"])
R = SampleROOT(vl["b"], vl["lep"], vl["ev"], vl["t"])

print("n-Events: ", T.n)
t1c = time()
s_ = Sf.SolT(T.b, T.b_, T.mu, T.mu_, T.mT, T.mW, T.mN, T.met, T.phi, 1e-12)
t2c = time()
tc = t2c - t1c
print("C++: ", tc, " device: ", device)

s = []
t1p = time()
for i in range(R.n):
    try:
        s.append(doubleNeutrinoSolutions(R.b[i], R.b_[i], R.mu[i], R.mu_[i], R.met_x[i], R.met_y[i], mT2 = R.mT[i]**2))
    except:
        s.append(None)
t2p = time()
tp = t2p - t1p 
print("Python: ", tp)
print("Speed Factor (> 1 is better): ", tp/tc)

s_inv = Sf.SolT(T.b_, T.b, T.mu_, T.mu, T.mT, T.mW, T.mN, T.met, T.phi, 1e-12)
sinv = []
for i in range(R.n):
    try:
        sinv.append(doubleNeutrinoSolutions(R.b_[i], R.b[i], R.mu_[i], R.mu[i], R.met_x[i], R.met_y[i], mT2 = R.mT[i]**2))
    except:
        sinv.append(None)


error_Torch = []
error_Python = []

PT_Torch = []
PT_Python = []
PT_Truth = []

Phi_Torch = []
Phi_Python = []
Phi_Truth = []

Eta_Torch = []
Eta_Python = []
Eta_Truth = []

E_Torch = []
E_Python = []
E_Truth = []

Mass_Torch = []
Mass_Python = []
Mass_Truth = []

it = -1
for i in range(T.n):
    useEvent = s_[0][i]
    if useEvent != True:
        continue
    it += 1
    neutrinos = []
    neutrinos_t = []
    
    nu_t, nu_t_ = s_[1][it], s_[2][it]
    for k in range(len(nu_t)):
        if sum(nu_t[k] + nu_t_[k]) == 0:
            continue
        nut1 = MakeParticle(nu_t[k].tolist())
        nut2 = MakeParticle(nu_t_[k].tolist())
        neutrinos_t.append([nut1, nut2])
    
    nu_sols = np.array(s[i].nunu_s)
    for k in nu_sols:
        nut1 = MakeParticle(k[0].tolist())
        nut2 = MakeParticle(k[1].tolist())
        neutrinos.append([nut1, nut2])
    
    close_P = { Difference(vl["nu"][i], p) : p for p in neutrinos }
    close_T = { Difference(vl["nu"][i], p) : p for p in neutrinos_t }
    
    if len(close_P) == 0 or len(close_T) == 0:
        continue

    x = list(close_P)
    x.sort()
    close_P = close_P[x[0]]
    error_Python.append(x[0])
    PT_Python += [k._pt/1000 for k in close_P]
    Phi_Python += [k._phi for k in close_P]
    Eta_Python += [k._eta for k in close_P]
    E_Python += [k._e/1000 for k in close_P]
    Mass_Python += [sum([close_P[0], vl["b"][i][0], vl["lep"][i][0]]).Mass]
    Mass_Python += [sum([close_P[1], vl["b"][i][1], vl["lep"][i][1]]).Mass]

    x = list(close_T)
    x.sort()
    close_T = close_T[x[0]]
    error_Torch.append(x[0])
    PT_Torch += [k._pt/1000 for k in close_T]
    Phi_Torch += [k._phi for k in close_T]
    Eta_Torch += [k._eta for k in close_T]
    E_Torch += [k._e/1000 for k in close_T]
    Mass_Torch += [sum([close_T[0], vl["b"][i][0], vl["lep"][i][0]]).Mass]
    Mass_Torch += [sum([close_T[1], vl["b"][i][1], vl["lep"][i][1]]).Mass]

    PT_Truth += [k.pt/1000 for k in vl["nu"][i]]
    Phi_Truth += [k.phi for k in vl["nu"][i]]
    Eta_Truth += [k.eta for k in vl["nu"][i]]
    E_Truth += [k.e/1000 for k in vl["nu"][i]]
    Mass_Truth += [sum([vl["nu"][i][0], vl["b"][i][0], vl["lep"][i][0]]).Mass]
    Mass_Truth += [sum([vl["nu"][i][1], vl["b"][i][1], vl["lep"][i][1]]).Mass]

ErrorMatrix = TH2F()
ErrorMatrix.xBins = 1000
ErrorMatrix.yBins = 1000
ErrorMatrix.xMin = 0
ErrorMatrix.yMin = 0
ErrorMatrix.xMax = 15
ErrorMatrix.yMax = 15
ErrorMatrix.xData = error_Python
ErrorMatrix.xTitle = "Python Prediction"
ErrorMatrix.yData = error_Torch
ErrorMatrix.yTitle = "PyTorch Prediction"
ErrorMatrix.Filename = "ErrorMatrix"
ErrorMatrix.Title = "Error Matrix Between Neutrino Reconstruction Algorithm"
ErrorMatrix.SaveFigure()

def Performance(tru, py, tor, title, xtitle, lmin = None):
    PT_Tru = TH1F()
    PT_Tru.xData = tru 
    PT_Tru.Title = "Truth"
    
    PT_Tor = TH1F()
    PT_Tor.xData = tor
    PT_Tor.Title = "Torch"
    
    PT_Py = TH1F()
    PT_Py.xData = py
    PT_Py.Title = "Python"
    
    th = CombineTH1F()
    th.Histograms = [PT_Tru, PT_Tor, PT_Py]
    th.xTitle = "Neutrino " + xtitle
    th.Title = title + " Reconstruction of Neutrinos"
    th.xMin = 0 if lmin == None else lmin
    th.xMax = max(tru)
    th.xBins = 1000
    th.Filename = title + "_Reconstruction"
    th.SaveFigure()

Performance(PT_Truth, PT_Python, PT_Torch, "PT", "Transverse Momenta (GeV)")
Performance(E_Truth, E_Python, E_Torch, "Energy", "Energy (GeV)")
Performance(Phi_Truth, Phi_Python, Phi_Torch, "Phi", "Phi")
Performance(Eta_Truth, Eta_Python, Eta_Torch, "Eta", "Eta")
Performance(Mass_Truth, Mass_Python, Mass_Torch, "Top Mass", "Top Mass (GeV)", lmin = 160)
