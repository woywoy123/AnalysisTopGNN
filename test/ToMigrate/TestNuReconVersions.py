from AnalysisTopGNN import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.IO import UnpickleObject, PickleObject
import PyC.Transform.Floats as F
from Checks import *
import torch

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

def MakeTensor_(inpt, indx):
    return torch.tensor([[ i[indx]._px/1000, i[indx]._py/1000, i[indx]._pz/1000, i[indx]._e/1000 ] for i in inpt], dtype = torch.float64, device = "cuda")



Ana = Analysis()
Ana.InputSample("bsm4t-1000", "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root")
Ana.Event = Event
Ana.EventStop = 100
Ana.EventCache = True
Ana.DumpPickle = True 
Ana.chnk = 100
Ana.VerboseLevel = 2
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
        it+=1

    
    if it == 1000:
        break

Skip = False
try:
    import PyC.NuSol.CUDA as NuC
except:
    Skip = True

if Skip == False:
    b1c = MakeTensor_(vl["b"], 0)
    b2c = MakeTensor_(vl["b"], 1)
    mu1c = MakeTensor_(vl["lep"], 0)
    mu2c = MakeTensor_(vl["lep"], 1)
    
    metx = torch.tensor([ [F.Px(i.met, i.met_phi)/1000] for i in vl["ev"] ], dtype = torch.float64, device = "cuda")
    mety = torch.tensor([ [F.Py(i.met, i.met_phi)/1000] for i in vl["ev"] ], dtype = torch.float64, device = "cuda")
    T = SampleTensor(vl["b"], vl["lep"], vl["ev"], vl["t"], "cuda", [[100, 0], [0, 100]])
    
    # ------------------ Single Neutrino Reconstruction -------------------------- # 
    sol_tP = NuC.NuPtEtaPhiE(T.b, T.mu, T.met, T.phi, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12)
    sol_tC = NuC.NuPxPyPzE(b1c, mu1c, metx, mety, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12)
    AssertEquivalenceRecursive(sol_tC[1].tolist(), sol_tP[1].tolist(), 0.01)
    
    Pb_l, Pmu_l, Pmet_l = [], [], []
    Cb_l, Cmu_l, Cmet_l = [], [], []
    met_lS, mass_l = [], []
    
    for i in range(len(sol_tP[0])):
        b, mu, ev = vl["b"][i][0], vl["lep"][i][0], vl["ev"][i]
        _solP = NuC.NuDoublePtEtaPhiE(
                b.pt/1000, b.eta, b.phi, b.e/1000, 
                mu.pt/1000, mu.eta, mu.phi, mu.e/1000, 
                ev.met/1000, ev.met_phi, 
                100, 0, 0, 100, 
                vl["t"][i][0].Mass, 80.385, 0, 1e-12)
       
        _solC = NuC.NuDoublePxPyPzE(
                b._px/1000, b._py/1000, b._pz/1000, b.e/1000, 
                mu._px/1000, mu._py/1000, mu._pz/1000, mu.e/1000, 
                F.Px(ev.met, ev.met_phi)/1000, F.Py(ev.met, ev.met_phi)/1000, 
                100, 0, 0, 100, 
                vl["t"][i][0].Mass, 80.385, 0, 1e-12)
        AssertEquivalenceRecursive(_solP[1].tolist(), _solC[1].tolist(), 0.01)
    
    
        Pb_l.append([b.pt/1000, b.eta, b.phi, b.e/1000])
        Pmu_l.append([mu.pt/1000, mu.eta, mu.phi, mu.e/1000])
        Pmet_l.append([ev.met/1000, ev.met_phi])
     
        Cb_l.append([b._px/1000, b._py/1000, b._pz/1000, b.e/1000])
        Cmu_l.append([mu._px/1000, mu._py/1000, mu._pz/1000, mu.e/1000])
        Cmet_l.append([F.Px(ev.met, ev.met_phi)/1000, F.Py(ev.met, ev.met_phi)/1000])
    
        met_lS.append([100, 0, 0, 100])
        mass_l.append([vl["t"][i][0].Mass, 80.385, 0])
    
    _solPL = NuC.NuListPtEtaPhiE(Pb_l, Pmu_l, Pmet_l, met_lS, mass_l, 1e-12)
    _solCL = NuC.NuListPxPyPzE(Cb_l, Cmu_l, Cmet_l, met_lS, mass_l, 1e-12)
    
    AssertEquivalenceRecursive(sol_tP[1].tolist(), _solCL[1].tolist(), 0.01)
    AssertEquivalenceRecursive(_solPL[1].tolist(), _solCL[1].tolist(), 0.01)
    
    # ------------------ Double Neutrino Reconstruction -------------------------- # 
    sol_tP = NuC.NuNuPtEtaPhiE(T.b, T.b_, T.mu, T.mu_, T.met, T.phi, T.mT, T.mW, T.mN, 1e-12)
    sol_tC = NuC.NuNuPxPyPzE(b1c, b2c, mu1c, mu2c, metx, mety, T.mT, T.mW, T.mN, 1e-12)
    # Solutions v
    for i, j in zip(sol_tC[3], sol_tP[3]):
        AssertSimilarSets(i.tolist(), j.tolist(), 1)
    # Solutions v_
    for i, j in zip(sol_tC[4], sol_tP[4]):
        AssertSimilarSets(i.tolist(), j.tolist(), 1)
    
    Pb, Pmu, Pmet = [], [], []
    Pb_, Pmu_ = [], []
    
    Cb, Cmu, Cmet = [], [], []
    Cb_, Cmu_ = [], []
    
    it = 0
    for i in range(len(sol_tP[0])):
        b, mu, ev = vl["b"][i][0], vl["lep"][i][0], vl["ev"][i]
        b_, mu_ = vl["b"][i][1], vl["lep"][i][1]
        
        Pb.append([b.pt/1000, b.eta, b.phi, b.e/1000])
        Pb_.append([b_.pt/1000, b_.eta, b_.phi, b_.e/1000])
        
        Pmu.append([mu.pt/1000, mu.eta, mu.phi, mu.e/1000])
        Pmu_.append([mu_.pt/1000, mu_.eta, mu_.phi, mu_.e/1000])
        
        Pmet.append([ev.met/1000, ev.met_phi])
    
        Cb.append([b._px/1000, b._py/1000, b._pz/1000, b.e/1000])
        Cb_.append([b_._px/1000, b_._py/1000, b_._pz/1000, b_.e/1000])
        
        Cmu.append([mu._px/1000, mu._py/1000, mu._pz/1000, mu.e/1000])
        Cmu_.append([mu_._px/1000, mu_._py/1000, mu_._pz/1000, mu_.e/1000])
        
        Cmet.append([F.Px(ev.met, ev.met_phi)/1000, F.Py(ev.met, ev.met_phi)/1000])
    
        _solP = NuC.NuNuDoublePtEtaPhiE(
                Pb[-1][0],    Pb[-1][1],   Pb[-1][2],   Pb[-1][3], 
                Pb_[-1][0],   Pb_[-1][1],  Pb_[-1][2],  Pb_[-1][3], 
                Pmu[-1][0],   Pmu[-1][1],  Pmu[-1][2],  Pmu[-1][3], 
                Pmu_[-1][0],  Pmu_[-1][1], Pmu_[-1][2], Pmu_[-1][3], 
                Pmet[-1][0],  Pmet[-1][1],
                mass_l[i][0], mass_l[i][1], mass_l[i][2], 
                1e-12)
        if _solP[0]:
            continue
        AssertSimilarSets(sol_tP[3][it].tolist(), _solP[3][0].tolist(), 1)
        it += 1
        
        _solC = NuC.NuNuDoublePxPyPzE(
                Cb[-1][0],   Cb[-1][1],   Cb[-1][2],   Cb[-1][3], 
                Cb_[-1][0],  Cb_[-1][1],  Cb_[-1][2],  Cb_[-1][3], 
                Cmu[-1][0],  Cmu[-1][1],  Cmu[-1][2],  Cmu[-1][3], 
                Cmu_[-1][0], Cmu_[-1][1], Cmu_[-1][2], Cmu_[-1][3], 
                Cmet[-1][0], Cmet[-1][1],
                mass_l[i][0], mass_l[i][1], mass_l[i][2], 
                1e-12)
    
        AssertSimilarSets(_solC[3][0].tolist(), _solP[3][0].tolist(), 1)
    
    sol_tP = NuC.NuNuListPtEtaPhiE(Pb, Pb_, Pmu, Pmu_, Pmet, mass_l, 1e-12)
    sol_tC = NuC.NuNuListPxPyPzE(Cb, Cb_, Cmu, Cmu_, Cmet, mass_l, 1e-12)
    # Solutions v
    for i, j in zip(sol_tC[3], sol_tP[3]):
        AssertSimilarSets(i.tolist(), j.tolist(), 1)
    # Solutions v_
    for i, j in zip(sol_tC[4], sol_tP[4]):
        AssertSimilarSets(i.tolist(), j.tolist(), 1)

Skip = False
try:
    import PyC.NuSol.Tensors as NuC
except:
    Skip = True
if Skip:
    exit()

b1c = MakeTensor_(vl["b"], 0)
b2c = MakeTensor_(vl["b"], 1)
mu1c = MakeTensor_(vl["lep"], 0)
mu2c = MakeTensor_(vl["lep"], 1)

metx = torch.tensor([ [F.Px(i.met, i.met_phi)/1000] for i in vl["ev"] ], dtype = torch.float64, device = "cuda")
mety = torch.tensor([ [F.Py(i.met, i.met_phi)/1000] for i in vl["ev"] ], dtype = torch.float64, device = "cuda")
T = SampleTensor(vl["b"], vl["lep"], vl["ev"], vl["t"], "cuda", [[100, 0], [0, 100]])

# ------------------ Single Neutrino Reconstruction -------------------------- # 
sol_tP = NuC.NuPtEtaPhiE(T.b, T.mu, T.met, T.phi, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12)
sol_tC = NuC.NuPxPyPzE(b1c, mu1c, metx, mety, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12)
AssertEquivalenceRecursive(sol_tC[1].tolist(), sol_tP[1].tolist(), 0.01)

Pb_l, Pmu_l, Pmet_l = [], [], []
Cb_l, Cmu_l, Cmet_l = [], [], []
met_lS, mass_l = [], []

for i in range(len(sol_tP[0])):
    b, mu, ev = vl["b"][i][0], vl["lep"][i][0], vl["ev"][i]
    _solP = NuC.NuDoublePtEtaPhiE(
            b.pt/1000, b.eta, b.phi, b.e/1000, 
            mu.pt/1000, mu.eta, mu.phi, mu.e/1000, 
            ev.met/1000, ev.met_phi, 
            100, 0, 0, 100, 
            vl["t"][i][0].Mass, 80.385, 0, 1e-12)
   
    _solC = NuC.NuDoublePxPyPzE(
            b._px/1000, b._py/1000, b._pz/1000, b.e/1000, 
            mu._px/1000, mu._py/1000, mu._pz/1000, mu.e/1000, 
            F.Px(ev.met, ev.met_phi)/1000, F.Py(ev.met, ev.met_phi)/1000, 
            100, 0, 0, 100, 
            vl["t"][i][0].Mass, 80.385, 0, 1e-12)
    AssertEquivalenceRecursive(_solP[1].tolist(), _solC[1].tolist(), 0.05)


    Pb_l.append([b.pt/1000, b.eta, b.phi, b.e/1000])
    Pmu_l.append([mu.pt/1000, mu.eta, mu.phi, mu.e/1000])
    Pmet_l.append([ev.met/1000, ev.met_phi])
 
    Cb_l.append([b._px/1000, b._py/1000, b._pz/1000, b.e/1000])
    Cmu_l.append([mu._px/1000, mu._py/1000, mu._pz/1000, mu.e/1000])
    Cmet_l.append([F.Px(ev.met, ev.met_phi)/1000, F.Py(ev.met, ev.met_phi)/1000])

    met_lS.append([100, 0, 0, 100])
    mass_l.append([vl["t"][i][0].Mass, 80.385, 0])

_solPL = NuC.NuListPtEtaPhiE(Pb_l, Pmu_l, Pmet_l, met_lS, mass_l, 1e-12)
_solCL = NuC.NuListPxPyPzE(Cb_l, Cmu_l, Cmet_l, met_lS, mass_l, 1e-12)

AssertEquivalenceRecursive(sol_tP[1].tolist(), _solCL[1].tolist(), 0.05)
AssertEquivalenceRecursive(_solPL[1].tolist(), _solCL[1].tolist(), 0.05)

# ------------------ Double Neutrino Reconstruction -------------------------- # 
sol_tP = NuC.NuNuPtEtaPhiE(T.b, T.b_, T.mu, T.mu_, T.met, T.phi, T.mT, T.mW, T.mN, 1e-12)
sol_tC = NuC.NuNuPxPyPzE(b1c, b2c, mu1c, mu2c, metx, mety, T.mT, T.mW, T.mN, 1e-12)
# Solutions v
for i, j in zip(sol_tC[3], sol_tP[3]):
    AssertSimilarSets(i.tolist(), j.tolist(), 1)
# Solutions v_
for i, j in zip(sol_tC[4], sol_tP[4]):
    AssertSimilarSets(i.tolist(), j.tolist(), 1)

Pb, Pmu, Pmet = [], [], []
Pb_, Pmu_ = [], []

Cb, Cmu, Cmet = [], [], []
Cb_, Cmu_ = [], []

it = 0
for i in range(len(sol_tP[0])):
    b, mu, ev = vl["b"][i][0], vl["lep"][i][0], vl["ev"][i]
    b_, mu_ = vl["b"][i][1], vl["lep"][i][1]
    
    Pb.append([b.pt/1000, b.eta, b.phi, b.e/1000])
    Pb_.append([b_.pt/1000, b_.eta, b_.phi, b_.e/1000])
    
    Pmu.append([mu.pt/1000, mu.eta, mu.phi, mu.e/1000])
    Pmu_.append([mu_.pt/1000, mu_.eta, mu_.phi, mu_.e/1000])
    
    Pmet.append([ev.met/1000, ev.met_phi])

    Cb.append([b._px/1000, b._py/1000, b._pz/1000, b.e/1000])
    Cb_.append([b_._px/1000, b_._py/1000, b_._pz/1000, b_.e/1000])
    
    Cmu.append([mu._px/1000, mu._py/1000, mu._pz/1000, mu.e/1000])
    Cmu_.append([mu_._px/1000, mu_._py/1000, mu_._pz/1000, mu_.e/1000])
    
    Cmet.append([F.Px(ev.met, ev.met_phi)/1000, F.Py(ev.met, ev.met_phi)/1000])

    _solP = NuC.NuNuDoublePtEtaPhiE(
            Pb[-1][0],    Pb[-1][1],   Pb[-1][2],   Pb[-1][3], 
            Pb_[-1][0],   Pb_[-1][1],  Pb_[-1][2],  Pb_[-1][3], 
            Pmu[-1][0],   Pmu[-1][1],  Pmu[-1][2],  Pmu[-1][3], 
            Pmu_[-1][0],  Pmu_[-1][1], Pmu_[-1][2], Pmu_[-1][3], 
            Pmet[-1][0],  Pmet[-1][1],
            mass_l[i][0], mass_l[i][1], mass_l[i][2], 
            1e-12)
    if _solP[0]:
        continue
    AssertSimilarSets(sol_tP[3][it].tolist(), _solP[3][0].tolist(), 1)
    it += 1
    
    _solC = NuC.NuNuDoublePxPyPzE(
            Cb[-1][0],   Cb[-1][1],   Cb[-1][2],   Cb[-1][3], 
            Cb_[-1][0],  Cb_[-1][1],  Cb_[-1][2],  Cb_[-1][3], 
            Cmu[-1][0],  Cmu[-1][1],  Cmu[-1][2],  Cmu[-1][3], 
            Cmu_[-1][0], Cmu_[-1][1], Cmu_[-1][2], Cmu_[-1][3], 
            Cmet[-1][0], Cmet[-1][1],
            mass_l[i][0], mass_l[i][1], mass_l[i][2], 
            1e-12)

    AssertSimilarSets(_solC[3][0].tolist(), _solP[3][0].tolist(), 1)

sol_tP = NuC.NuNuListPtEtaPhiE(Pb, Pb_, Pmu, Pmu_, Pmet, mass_l, 1e-12)
sol_tC = NuC.NuNuListPxPyPzE(Cb, Cb_, Cmu, Cmu_, Cmet, mass_l, 1e-12)
# Solutions v
for i, j in zip(sol_tC[3], sol_tP[3]):
    AssertSimilarSets(i.tolist(), j.tolist(), 1)
# Solutions v_
for i, j in zip(sol_tC[4], sol_tP[4]):
    AssertSimilarSets(i.tolist(), j.tolist(), 1)
