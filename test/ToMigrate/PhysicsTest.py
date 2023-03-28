import torch
import ROOT as r
from Checks import *
from AnalysisTopGNN import Analysis 
from AnalysisTopGNN.Events import Event
import PyC.Physics.Tensors.Cartesian as TC
import PyC.Physics.CUDA.Cartesian as CC
import PyC.Physics.Tensors.Polar as TP
import PyC.Physics.CUDA.Polar as CP
from time import time

def ParticleToROOT(part):
    _part = r.TLorentzVector()
    _part.SetPtEtaPhiE(part.pt, part.eta, part.phi, part.e)
    return _part

def ParticleToTorch(part):
    tx = torch.tensor([[part._px]], device = "cuda"); 
    ty = torch.tensor([[part._py]], device = "cuda"); 
    tz = torch.tensor([[part._pz]], device = "cuda"); 
    te = torch.tensor([[part._e]], device = "cuda"); 
    return tx, ty, tz, te

def PerformanceInpt(var, inpt = "(p_x, p_y, p_z)", Coord = "C"):
    strg_TC = "T" + Coord + "." + var + inpt
    strg_CC = "C" + Coord + "." + var + inpt
   
    t1 = time()
    res_c = eval(strg_TC)
    diff1 = time() - t1

    t1 = time()
    res = eval(strg_CC)
    diff2 = time() - t1
    
    print("--- Testing Performance Between C++ and CUDA of " + var + " ---")
    print("Speed Factor (> 1 is better): ", diff1 / diff2)
    AssertEquivalenceRecursive(res_c, res, 0.001)


Ana = Analysis()
Ana.InputSample("bsm4t-1000", "/home/tnom6927/Downloads/samples/tttt/DAOD_TOPQ1.21955717._000003.root")
Ana.Event = Event 
Ana.EventStop = 100
Ana.EventCache = True 
Ana.DumpPickle = True 
Ana.Launch()

_x, _y, _z, _e = [], [], [], []
_x1, _y1, _z1, _e1 = [], [], [], []

pt, eta, phi, e = [], [], [], []
pt1, eta1, phi1, e1 = [], [], [], []
for i in Ana:
    event = i.Trees["nominal"]
    top = event.Tops[0]
    top2 = event.Tops[1]
    tx, ty, tz, te = ParticleToTorch(top)
    top_r = ParticleToROOT(top)
    
    theta_r = top_r.Theta()
    theta_p = TC.Theta(tx, ty, tz)
    AssertEquivalenceRecursive([[theta_r]], theta_p) 
    
    p_r = top_r.P()
    p_p = TC.P(tx, ty, tz)
    AssertEquivalenceRecursive([[p_r]], p_p) 

    beta_r = top_r.Beta()
    beta_p = TC.Beta(tx, ty, tz, te)
    AssertEquivalenceRecursive([[beta_r]], beta_p) 

    m_r = top_r.M()
    m_p = TC.M(tx, ty, tz, te)
    AssertEquivalenceRecursive([[m_r]], m_p) 

    mt_r = top_r.Mt()
    mt_p = TC.Mt(tz, te)
    AssertEquivalenceRecursive([[mt_r]], mt_p)   
    
    for k in range(100):
        _x.append([top._px]), _y.append([top._py])
        _z.append([top._pz]), _e.append([top._e])

        _x1.append([top2._px]), _y1.append([top2._py])
        _z1.append([top2._pz]), _e1.append([top2._e])

        pt.append([top.pt]), eta.append([top.eta])
        phi.append([top.phi]), e.append([top._e])

        pt1.append([top2.pt]), eta1.append([top2.eta])
        phi1.append([top2.phi]), e1.append([top2._e])


print(" ======= Cartesian stuff ======= ")
p_x = torch.tensor(_x, device = "cuda")
p_y = torch.tensor(_y, device = "cuda")
p_z = torch.tensor(_z, device = "cuda")
p_e = torch.tensor(_e, device = "cuda")

p2_x = torch.tensor(_x1, device = "cuda")
p2_y = torch.tensor(_y1, device = "cuda")
p2_z = torch.tensor(_z1, device = "cuda")
p2_e = torch.tensor(_e1, device = "cuda")

PerformanceInpt("P2")
PerformanceInpt("P")
print("")
PerformanceInpt("Beta2", "(p_x, p_y, p_z, p_e)")
PerformanceInpt("Beta", "(p_x, p_y, p_z, p_e)")
print("")
PerformanceInpt("M2", "(p_x, p_y, p_z, p_e)")
PerformanceInpt("M", "(p_x, p_y, p_z, p_e)")
print("")
PerformanceInpt("Mt2", "(p_z, p_e)")
PerformanceInpt("Mt", "(p_z, p_e)")
print("")
PerformanceInpt("Theta")
PerformanceInpt("DeltaR","(p_x, p2_x, p_y, p2_y, p_z, p2_z)")
print("")

print(" ======= Polar stuff ======= ")
_pt = torch.tensor(pt, device = "cuda")
_eta = torch.tensor(eta, device = "cuda")
_phi = torch.tensor(phi, device = "cuda")
_e = torch.tensor(e, device = "cuda")

_pt2 = torch.tensor(pt1, device = "cuda")
_eta2 = torch.tensor(eta1, device = "cuda")
_phi2 = torch.tensor(phi1, device = "cuda")
_e2 = torch.tensor(e1, device = "cuda")

PerformanceInpt("P2", "(_pt, _eta, _phi)", "P")
PerformanceInpt("P", "(_pt, _eta, _phi)", "P")
print("")
PerformanceInpt("Beta2", "(_pt, _eta, _phi, _e)", "P")
PerformanceInpt("Beta", "(_pt, _eta, _phi, _e)", "P")
print("")
PerformanceInpt("M2", "(_pt, _eta, _phi, _e)", "P")
PerformanceInpt("M", "(_pt, _eta, _phi, _e)", "P")
print("")
PerformanceInpt("Mt2", "(_pt, _eta, _e)", "P")
PerformanceInpt("Mt", "(_pt, _eta, _e)", "P")
print("")
PerformanceInpt("Theta", "(_pt, _eta, _phi)", "P")
PerformanceInpt("DeltaR", "(_eta, _eta2, _phi, _phi2)", "P")



