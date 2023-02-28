from AnalysisTopGNN import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.IO import UnpickleObject, PickleObject
import PyC.NuSol.Tensors as NuT
import PyC.NuSol.CUDA as NuC
from Checks import *
from NeutrinoSolutionDeconstruct import *
from time import time
torch.set_printoptions(precision=20)
torch.set_printoptions(linewidth = 120)

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

makeSample = False
its = 100
errorMargin = 2 # Percentage for double Neutrino

if makeSample:
    Ana = Analysis()
    Ana.InputSample("bsm4t-1000", "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root")
    Ana.Event = Event
    #Ana.EventStop = 100
    Ana.EventCache = True
    Ana.DumpPickle = True 
    Ana.chnk = 100
    Ana.VerboseLevel = 2
    Ana.Launch()
    l = len(Ana)
    
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
        
if makeSample:
    PickleObject(vl, "TMP")

vl = UnpickleObject("TMP")
T = SampleTensor(vl["b"], vl["lep"], vl["ev"], vl["t"], "cuda", [[100, 0], [0, 100]])
R = SampleVector(vl["b"], vl["lep"], vl["ev"], vl["t"])
print(len(vl["b"]))

print("======================= Testing Speed of Single Neutrino Reconstruction ===================")
diff = [[], [], []]
for i in range(its):
    t1 = time()
    for r, t in zip(R, T):
        b, mu = r[0], r[1]
        met_x, met_y = r[4], r[5]
        mT, mW, mNu = r[6], r[7], r[8]
        try:
            sol = singleNeutrinoSolution(b, mu, (met_x, met_y), [[100, 0], [0, 100]], mW**2, mT**2)
            sol.nu
        except:
            continue
    t2 = time()
    diff[0].append(t2 - t1)

for t in range(its):
    t1 = time()
    t_sol = NuT.NuPtEtaPhiE(T.b, T.mu, T.met, T.phi, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12)
    t2 = time()
    diff1 = t2 - t1 
    diff[1].append(diff1)

for t in range(its):   
    t1 = time()
    t_solC = NuC.NuPtEtaPhiE(T.b, T.mu, T.met, T.phi, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12)
    t2 = time()
    diff2 = t2 - t1
    diff[2].append(diff2)

print(sum(diff[0]), sum(diff[1]))
print("--- Testing Performance Between Original and C++ of Nu ---")
print("Speed Factor (> 1 is better): ", (sum(diff[0])) / sum(diff[1]))

print(sum(diff[0]), sum(diff[2]))
print("--- Testing Performance Between Original and CUDA of Nu ---")
print("Speed Factor (> 1 is better): ", (sum(diff[0])) / sum(diff[2]))

print(sum(diff[1]), sum(diff[2]))
print("--- Testing Performance Between C++ and CUDA of Nu ---")
print("Speed Factor (> 1 is better): ", (sum(diff[1])) / sum(diff[2]))

print("======================= Testing Speed of Double Neutrino Reconstruction ===================")
diff = [[], [], []]
for i in range(its):
    t1 = time()
    for r, t in zip(R, T):
        b, mu = r[0], r[1]
        _b, _mu = r[2], r[3]
        met_x, met_y = r[4], r[5]
        mT, mW, mNu = r[6], r[7], r[8]
        try:
            sol = doubleNeutrinoSolutions((_b, b), (_mu, mu), (met_x, met_y), mW**2, mT**2)
            sol.nunu_s
        except:
            continue
    t2 = time()
    diff[0].append(t2 - t1)



b = torch.cat([T.b for i in range(its)], 0)
b_ = torch.cat([T.b_ for i in range(its)], 0)
mu = torch.cat([T.mu for i in range(its)], 0)
mu_ = torch.cat([T.mu_ for i in range(its)], 0)
met = torch.cat([T.met for i in range(its)], 0)
phi = torch.cat([T.phi for i in range(its)], 0)
mT = torch.cat([T.mT for i in range(its)], 0)
mW = torch.cat([T.mW for i in range(its)], 0)
mN = torch.cat([T.mN for i in range(its)], 0)

t1 = time()
t_sol = NuT.NuNuPtEtaPhiE(b, b_, mu, mu_, met, phi, mT, mW, mN, 1e-12)
t2 = time()
diff1 = t2 - t1 
diff[1].append(diff1)

t1 = time()
t_solC = NuC.NuNuPtEtaPhiE(b, b_, mu, mu_, met, phi, mT, mW, mN, 1e-12)
t2 = time()
diff2 = t2 - t1
diff[2].append(diff2)

print(sum(diff[0]), sum(diff[1]))
print("--- Testing Performance Between Original and C++ of NuNu ---")
print("Speed Factor (> 1 is better): ", (sum(diff[0])) / sum(diff[1]))

print(sum(diff[0]), sum(diff[2]))
print("--- Testing Performance Between Original and CUDA of NuNu ---")
print("Speed Factor (> 1 is better): ", (sum(diff[0])) / sum(diff[2]))

print(sum(diff[1]), sum(diff[2]))
print("--- Testing Performance Between C++ and CUDA of NuNu ---")
print("Speed Factor (> 1 is better): ", (sum(diff[1])) / sum(diff[2]))

exit()

print("======================= Testing Consistency of Single Neutrino Reconstruction =================== ")
_sol = NuC.NuPtEtaPhiE(T.b, T.mu, T.met, T.phi, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12)
t_sol = NuT.NuPtEtaPhiE(T.b, T.mu, T.met, T.phi, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12)
Fail = False
it = 0
for r, t in zip(R, T):
    b, mu = r[0], r[1]
    met_x, met_y = r[4], r[5]
    mT, mW, mNu = r[6], r[7], r[8]
    try:
        sol = singleNeutrinoSolution(b, mu, (met_x, met_y), [[100, 0], [0, 100]], mW**2, mT**2)
        sol.nu
    except:
        continue

    if _sol[0][T.it] == True:
        continue

    if AssertEquivalenceList(sol.nu.tolist(), _sol[1][it].tolist()) == False:
        print(T.it)
        print("DIFF >1%!!! (CUDA)")
        Fail = True

    if AssertEquivalenceList(sol.nu.tolist(), t_sol[1][it].tolist()) == False:
        print(T.it)
        print("DIFF >1%!!! (PyTorch)")
        Fail = True
    it += 1
if Fail:
    print("Not Passed!")
else:
    print("Passed!")

print("======================= Testing Consistency of Double Neutrino Reconstruction =================== ")
# ------ Testing normal order ------ #
t_sol = NuT.NuNuPtEtaPhiE(T.b, T.b_, T.mu, T.mu_, T.met, T.phi, T.mT, T.mW, T.mN, 1e-12)
_sol = NuC.NuNuPtEtaPhiE(T.b, T.b_, T.mu, T.mu_, T.met, T.phi, T.mT, T.mW, T.mN, 1e-12)

# ------ Testing reverse order ------ #
invt_sol = NuT.NuNuPtEtaPhiE(T.b_, T.b, T.mu_, T.mu, T.met, T.phi, T.mT, T.mW, T.mN, 1e-12)
inv_sol = NuC.NuNuPtEtaPhiE(T.b_, T.b, T.mu_, T.mu, T.met, T.phi, T.mT, T.mW, T.mN, 1e-12)
it = 0
for r, t in zip(R, T):
    b, mu = r[0], r[1]
    _b, _mu = r[2], r[3]
    met_x, met_y = r[4], r[5]
    mT, mW, mNu = r[6], r[7], r[8]
    
    try:
        sol = doubleNeutrinoSolutions((b, _b), (mu, _mu), (met_x, met_y), mW**2, mT**2)
        sol.nunu_s
    except:
        continue

    if _sol[0][T.it] == True:
        continue

    # test if the values of the implementations are below a 1% error 
    if AssertSolutionSets(sol.nunu_s, t_sol[1][it].tolist(), t_sol[2][it].tolist(), errorMargin):
        print(it)
        print("DIFF >" + str(errorMargin) + "%!!! (Torch)")

    if AssertSolutionSets(sol.nunu_s, _sol[1][it].tolist(), _sol[2][it].tolist(), errorMargin):
        print(it)
        print("DIFF >" + str(errorMargin) + "%!!! (CUDA)")
    
    # Reverse the solutions
    sol = doubleNeutrinoSolutions((_b, b), (_mu, mu), (met_x, met_y), mW**2, mT**2)
    if AssertSolutionSets(sol.nunu_s, invt_sol[1][it].tolist(), invt_sol[2][it].tolist(), errorMargin):
        print(it)
        print("DIFF >" + str(errorMargin) + "%!!! (Torch - Reverse)")

    if AssertSolutionSets(sol.nunu_s, inv_sol[1][it].tolist(), inv_sol[2][it].tolist(), errorMargin):
        print(it)
        print("DIFF >" + str(errorMargin) + "%!!! (CUDA - Reverse)")
    it += 1

