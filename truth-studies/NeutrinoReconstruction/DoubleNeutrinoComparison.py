from AnalysisTopGNN import Analysis 
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.Particles.Particles import Neutrino
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F
import PyC.NuSol.Tensors as NuT
import PyC.Transform.Floats as Tf
from neutrino_momentum_reconstruction import doubleNeutrinoSolutions
import vector
import math

def MakeNu(sols):
    nu1 = Neutrino()
    nu1.px = sols[0]*1000
    nu1.py = sols[1]*1000
    nu1.pz = sols[2]*1000
    return nu1

def FitToTruth(t1, t2, nus):
    fit = {}
    for i, j in nus:
        diff = 0
        diff += ((t1._px - i.px)/1000)**2
        diff += ((t2._px - j.px)/1000)**2

        diff += ((t1._py - i.py)/1000)**2
        diff += ((t2._py - j.py)/1000)**2

        diff += ((t1._pz - i.pz)/1000)**2
        diff += ((t2._pz - j.pz)/1000)**2
        fit[diff] = [i, j]
        
        # Swap the order. We just want to know whether the solution pairs are present in truth.
        diff = 0
        diff += ((t1._px - j.px)/1000)**2
        diff += ((t2._px - i.px)/1000)**2

        diff += ((t1._py - j.py)/1000)**2
        diff += ((t2._py - i.py)/1000)**2

        diff += ((t1._pz - j.pz)/1000)**2
        diff += ((t2._pz - i.pz)/1000)**2
        fit[diff] = [j, i] # < keep like this, we dont care if the order is incorrect.
    
    f = list(fit)
    f.sort()
    return fit[f[0]], f[0]


Ana = Analysis()
#Ana.InputSample("bsm-1000-all", "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000")
Ana.InputSample("bsm-1000")
Ana.Event = Event 
Ana.EventCache = True 
Ana.DumpPickle = True 
Ana.chnk = 200
Ana.Launch()

numSolutions_Torch = []
numSolutions_Python = []

chi2_Python = []
chi2_Torch = []

Top1M_Python = []
Top2M_Python = []

Top1M_Torch = []
Top2M_Torch = []

delta_Top1M_Python = []
delta_Top2M_Python = []

delta_Top1M_Torch = []
delta_Top2M_Torch = []

it = -1
for i in Ana:
    ev = i.Trees["nominal"]
    tops = [t for t in ev.Tops if t.LeptonicDecay]
    
    it += 1
    if len(tops) != 2:
        continue
    t1, t2 = tops
    
    # Dilepton Selection on truth level. 
    # Conditions:
    # - Two Neutrinos 
    # - Two Leptons 
    # - Two quarks with no gluons.
    nu1 = [c for c in t1.Children if abs(c.pdgid) in [12, 14, 16]] 
    nu2 = [c for c in t2.Children if abs(c.pdgid) in [12, 14, 16]] 
    if len(nu1 + nu2) != 2:
        continue
    
    lep1 = [c for c in t1.Children if abs(c.pdgid) in [11, 13, 15]]
    lep2 = [c for c in t2.Children if abs(c.pdgid) in [11, 13, 15]]
    if len(lep1 + lep2) != 2:
        continue
    
    q1 = [ c for c in t1.Children if c not in nu1 + lep1 ]
    q2 = [ c for c in t2.Children if c not in nu2 + lep2 ]
    if len(q1 + q2) != 2:
        continue
    
    # True Neutrinos....
    n1, n2 = nu1[0], nu2[0]
    
    # Observables....
    l1, l2 = lep1[0], lep2[0]
    q1, q2 = q1[0], q2[0]
    
    l1_v = vector.obj(pt = l1.pt/1000, eta = l1.eta, phi = l1.phi, E = l1.e/1000)
    l2_v = vector.obj(pt = l2.pt/1000, eta = l2.eta, phi = l2.phi, E = l2.e/1000)

    q1_v = vector.obj(pt = q1.pt/1000, eta = q1.eta, phi = q1.phi, E = q1.e/1000)
    q2_v = vector.obj(pt = q2.pt/1000, eta = q2.eta, phi = q2.phi, E = q2.e/1000)
    
    mW = (n1 + l1).Mass # Generate a W-boson
    mT = t1.Mass
    try:
        sol = doubleNeutrinoSolutions(
                    (q1_v, q2_v), (l1_v, l2_v), 
                    (Tf.Px(ev.met/1000, ev.met_phi), Tf.Py(ev.met/1000, ev.met_phi)), 
                    mW**2, mT**2)
        sol = sol.nunu_s
    except:
        continue
    _sol = NuT.NuNuDoublePtEtaPhiE(
            q1.pt/1000, q1.eta, q1.phi, q1.e/1000, 
            q2.pt/1000, q2.eta, q2.phi, q2.e/1000,
            l1.pt/1000, l1.eta, l1.phi, l1.e/1000, 
            l2.pt/1000, l2.eta, l2.phi, l2.e/1000,
            ev.met/1000, ev.met_phi, 
            mT, mW, 0, 1e-12)
   

    skip, _nu1, _nu2 = _sol[0], _sol[1], _sol[2]
    if len(sol) != 0:
        nuR = [ [MakeNu(s_.tolist()), MakeNu(s.tolist())] for s_, s in sol ]
    else:
        nuR = []

    nuT = [ [MakeNu(k.tolist()), MakeNu(p.tolist())] for k, p in zip(_nu1[0], _nu2[0]) if sum(k + p) != 0.]

    # Collect the number of solutions 
    numSolutions_Python.append(len(nuR))
    numSolutions_Torch.append(len(nuT))
    
    # Try to find the neutrino solutions closest to truth
    mT1 = (n1 + l1 + q1).Mass
    mT2 = (n2 + l2 + q2).Mass 
    if len(nuR) != 0:
        nuR, _chi2 = FitToTruth(n1, n2, nuR)
        _n1, _n2 = nuR
        _t1 = (_n1 + l1 + q1).Mass
        _t2 = (_n2 + l2 + q2).Mass
        chi2_Python.append(math.log(_chi2))
        
        Top1M_Python.append(_t1)
        Top2M_Python.append(_t2)

        delta_Top1M_Python.append(_t1 - mT1)
        delta_Top2M_Python.append(_t2 - mT2)
    
    if len(nuT) != 0:
        nuT, _chi2 = FitToTruth(n1, n2, nuT)
        _n1, _n2 = nuT 

        _t1 = (_n1 + l1 + q1).Mass
        _t2 = (_n2 + l2 + q2).Mass
        
        chi2_Torch.append(math.log(_chi2))

        Top1M_Torch.append(_t1)
        Top2M_Torch.append(_t2)

        delta_Top1M_Torch.append(_t1 - mT1)
        delta_Top2M_Torch.append(_t2 - mT2)
 
PT_Tor = TH1F()
PT_Tor.Texture = True
PT_Tor.xData = numSolutions_Torch
PT_Tor.Title = "Torch"

PT_Py = TH1F()
PT_Py.Texture = True
PT_Py.xData = numSolutions_Python
PT_Py.Title = "Python"

numSolPlot = CombineTH1F()
numSolPlot.Histograms = [PT_Tor, PT_Py]
numSolPlot.xMin = 0
numSolPlot.xStep = 1
numSolPlot.xTitle = "Number of solutions"
numSolPlot.Title = "Number of solutions for neutrino reconstruction"
numSolPlot.Filename = "NumNeutrinoSolutions"
numSolPlot.SaveFigure()


## =================== Chi2 ====================== # 
Pchi2 = TH1F()
Pchi2.xData = chi2_Python
Pchi2.xStep = 1
Pchi2.Title = "Python"

Tchi2 = TH1F()
Tchi2.xData = chi2_Torch
Tchi2.xStep = 1
Tchi2.Title = "Torch"

Chi2 = CombineTH1F()
Chi2.Histograms = [Pchi2, Tchi2]
Chi2.Title = "Chi2 of Best Fitting Double Neutrino Solution"
Chi2.xTitle = "log(Chi2) (arb.)"
Chi2.yTitle = "Entries (arb.)"
Chi2.xMin = -5
Chi2.xStep = 1
Chi2.Filename = "Chi2_Neutrino_Solutions"
Chi2.SaveFigure()


# =================== Top 1 ====================== # 
PMT1 = TH1F()
PMT1.xData = Top1M_Python
PMT1.xStep = 1
PMT1.Title = "Python"

TMT1 = TH1F()
TMT1.xData = Top1M_Torch
TMT1.xStep = 1
TMT1.Title = "Torch"

TM1 = CombineTH1F()
TM1.Histograms = [TMT1, PMT1]
TM1.Title = "Best Fitting Neutrino Solution for Top 1 Reconstruction"
TM1.xTitle = "Invariant Mass (GeV)"
TM1.yTitle = "Entries (arb.)"
TM1.xMin = 0
TM1.xMax = 220
TM1.xStep = 20
TM1.Filename = "Reconstructed_Top1_Mass"
TM1.SaveFigure()


# =================== Top 2 ====================== # 
PMT2 = TH1F()
PMT2.xData = Top2M_Python
PMT2.xStep = 1
PMT2.Title = "Python"

TMT2 = TH1F()
TMT2.xData = Top2M_Torch
TMT2.xStep = 1
TMT2.Title = "Torch"

TM2 = CombineTH1F()
TM2.Histograms = [TMT2, PMT2]
TM2.Title = "Best Fitting Neutrino Solution for Top 2 Reconstruction"
TM2.xTitle = "Invariant Mass (GeV)"
TM2.yTitle = "Entries (arb.)"
TM2.xMin = 0
TM2.xStep = 20
TM2.xMax = 220
TM2.Filename = "Reconstructed_Top2_Mass"
TM2.SaveFigure()


# =================== Delta Top 1 ====================== # 
PMT1 = TH1F()
PMT1.xData = delta_Top1M_Python
PMT1.xStep = 1
PMT1.Title = "Python"

TMT1 = TH1F()
TMT1.xData = delta_Top1M_Torch
TMT1.xStep = 1
TMT1.Title = "Torch"

TM1 = CombineTH1F()
TM1.Histograms = [TMT1, PMT1]
TM1.Title = "Delta Mass Between Top 1 Reconstruction and Truth Top 1 Mass"
TM1.xTitle = "(RecoT - Top) Invariant Mass (GeV)"
TM1.yTitle = "Entries (arb.)"
TM1.xStep = 10
TM1.xMin = int(min(delta_Top1M_Python + delta_Top1M_Torch)/10)*10
TM1.Filename = "Delta_Top1_Mass"
TM1.SaveFigure()


# =================== Top 2 ====================== # 
PMT2 = TH1F()
PMT2.xData = delta_Top2M_Python
PMT2.xStep = 1
PMT2.Title = "Python"

TMT2 = TH1F()
TMT2.xData = delta_Top2M_Torch
TMT2.xStep = 1
TMT2.Title = "Torch"

TM2 = CombineTH1F()
TM2.Histograms = [TMT2, PMT2]
TM2.Title = "Delta Mass Between Top 2 Reconstruction and Truth Top 2 Mass"
TM2.xTitle = "(RecoT - Top) Invariant Mass (GeV)"
TM2.yTitle = "Entries (arb.)"
TM2.xMin = int(min(delta_Top2M_Python + delta_Top2M_Torch)/10)*10
TM2.xStep = 10
TM2.Filename = "Delta_Top2_Mass"
TM2.SaveFigure()
