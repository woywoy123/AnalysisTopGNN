from neutrino_momentum_reconstruction_python3 import singleNeutrinoSolution
from AnalysisTopGNN import Analysis 
from AnalysisTopGNN.Events import Event 
from AnalysisTopGNN.IO import PickleObject, UnpickleObject
import ROOT as r
import torch
import NuR.SingleNu.Floats as Sf
import NuR.Physics.Floats as F
from time import time
import numpy as np

Sxx = 100
Sxy = 0
Syx = 0
Syy = 100
mW = 80.385*1000 # MeV : W Boson Mass
mT = 172.5*1000  # MeV : t Quark Mass
mN = 0           # GeV : Neutrino Mass
device = "cpu"

def CompareNumerical(r_ori, r_pyt, string):
    print("(" + string + ") -> Original: ", r_ori, " ||  Pytorch: ", r_pyt, " || Error (%): ", 100*abs(r_pyt - r_ori)/r_ori)

def _MakeTensor(val, n, device = "cpu", dtp = torch.double):
    return torch.tensor([val for i in range(n)], device = device, dtype = dtp)


def SingleNeutrino(b, mu, ev):
    r_b = r.TLorentzVector()
    r_b.SetPtEtaPhiE(b.pt, b.eta, b.phi, b.e)
    
    r_mu = r.TLorentzVector()
    r_mu.SetPtEtaPhiE(mu.pt, mu.eta, mu.phi, mu.e)

    x = F.ToPx(ev.met, ev.met_phi, "cpu").tolist()[0][0]
    y = F.ToPy(ev.met, ev.met_phi, "cpu").tolist()[0][0]
    return singleNeutrinoSolution(r_b, r_mu, x, y, [[Sxx, Sxy], [Syx, Syy]])
    
def SingleNeutrinoPyT(b, mu, ev):
    _b = torch.tensor([[b_.pt, b_.eta, b_.phi, b_.e] for b_ in b], dtype = torch.double, device = device)
    _mu = torch.tensor([[mu_.pt, mu_.eta, mu_.phi, mu_.e] for mu_ in mu], dtype = torch.double, device = device)

    _met = torch.tensor([[ev_.met] for ev_ in ev], dtype = torch.double, device = device)
    _phi = torch.tensor([[ev_.met_phi] for ev_ in ev], dtype = torch.double, device = device)
    
    n = len(b)
    _mT = _MakeTensor([mT], n, device)
    _mW = _MakeTensor([mW], n, device)
    _mN = _MakeTensor([mN], n, device)
    _Sxx = _MakeTensor([Sxx], n, device)
    _Sxy = _MakeTensor([Sxy], n, device) 
    _Syx = _MakeTensor([Syx], n, device) 
    _Syy = _MakeTensor([Syy], n, device)
    return Sf.SolT(_b, _mu, _mT, _mW, _mN, _met, _phi, _Sxx, _Sxy, _Syx, _Syy)

def ParticleCollectors(ev):
    prt = { abs(p.pdgid) : p for t in ev.Tops for p in t.Children if t.DecayLeptonically() }
    b = prt[5]
    lep = [prt[i] for i in [11, 13, 15] if i in prt][0]
    nu = [prt[i] for i in [12, 14, 16] if i in prt][0]
    t = [ t for t in ev.Tops if t.DecayLeptonically()][0]
    return [b, lep, nu, ev, t]

direc = "<Some Directory>"
Ana = Analysis()
Ana.InputSample("bsm700", direc)
Ana.Event = Event
Ana.EventCache = True
Ana.DumpPickle = True 
Ana.Launch()

vl = {"b" : [], "lep" : [], "nu" : [], "ev" : [], "t" : []}
for i in Ana:
    ev = i.Trees["nominal"]
    tops = [ t for t in ev.Tops if t.DecayLeptonically()]

    if len(tops) == 1:
        k = ParticleCollectors(ev)
        vl["b"].append(k[0])
        vl["lep"].append(k[1])
        vl["nu"].append(k[2])
        vl["ev"].append(k[3])
        vl["t"].append(k[4])

res = {"Or" : [], "PT" : []}
t1p = time()    
for i in range(len(vl["b"])):
    res["Or"].append(SingleNeutrino(vl["b"][i], vl["lep"][i], vl["ev"][i]))
t2p = time()

t1c = time()
res["PT"] = SingleNeutrinoPyT(vl["b"], vl["lep"], vl["ev"])
t2c = time()

print("Python: ", t2p - t1p)
print("C++: ", t2c - t1c)
print("Improvement Factor: ", (t2p - t1p)/(t2c - t1c))

exit()

### Debugging 
c = SingleNeutrinoPyT(vl["b"], vl["lep"], vl["ev"])

def Recursion(inpt1, inpt2):
    if isinstance(inpt1, list) == False:
        try:
            return abs(inpt1 - inpt2)/(inpt1)
        except ZeroDivisionError:
            return abs(inpt1 - intp2)

    diff = 0
    for i, j in zip(inpt1, inpt2):
        diff += Recursion(i, j)
    return diff 

it = -1
kill = 0
for i in range(len(c[1])):
    it += 1

    if c[0][i] == True:
        it -= 1
        continue
    try:
        s = SingleNeutrino(vl["b"][i], vl["lep"][i], vl["ev"][i])
        sol = s.nu.tolist()
        chi = s.chi2.tolist()
    except:
        sol = []
        chi = None
    sol_ = c[1][it].tolist()
    chi_ = c[2][it].tolist()[0]
    if Recursion(sol, sol_) < 0.01:
        continue

    print("---")
    print(it)
    print("++++ Momentum of Neutrino ++++")
    print("ROOT: ", np.array(sol))    
    print("PyTorch: ", np.array(sol_))
    print("--- Chi2 of Prediction ---")    
    print("ROOT: ", chi)   
    print("PyTorch: ", chi_)
