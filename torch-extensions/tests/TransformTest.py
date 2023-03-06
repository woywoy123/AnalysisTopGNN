import torch
import PyC.Transform.Floats as F
import PyC.Transform.Tensors as T
import PyC.Transform.CUDA as C
from AnalysisTopGNN import Analysis
from AnalysisTopGNN.Events import Event
from time import time
from Checks import *

Ana = Analysis()
Ana.InputSample("bsm4t-1000", "/home/tnom6927/Downloads/samples/tttt/DAOD_TOPQ1.21955717._000003.root")
Ana.Event = Event 
Ana.EventStop = 100
Ana.EventCache = True 
Ana.DumpPickle = True 
Ana.Launch()

_tmp = []
_tmp2 = []
for ev in Ana:
    event = ev.Trees["nominal"]
    top = event.Tops[0]

    AssertEquivalence(top._px, F.Px(top.pt, top.phi))
    AssertEquivalence(top._py, F.Py(top.pt, top.phi))
    AssertEquivalence(top._pz, F.Pz(top.pt, top.eta))

    AssertEquivalence(top.pt,  F.PT(top._px, top._py))
    AssertEquivalence(top.eta, F.Eta(top._px, top._py, top._pz))
    AssertEquivalence(top.phi, F.Phi(top._px, top._py))
    
    AssertEquivalenceRecursive([top.pt, top.eta, top.phi], F.PtEtaPhi(top._px, top._py, top._pz))
 
    t_pt = MakeTensor(top.pt)
    t_eta = MakeTensor(top.eta)
    t_phi = MakeTensor(top.phi)

    AssertEquivalence(top._px, T.Px(t_pt, t_phi))
    AssertEquivalence(top._py, T.Py(t_pt, t_phi))
    AssertEquivalence(top._pz, T.Pz(t_pt, t_eta))

    t_px = MakeTensor(top._px)
    t_py = MakeTensor(top._py)
    t_pz = MakeTensor(top._pz)

    AssertEquivalence(top.pt, T.PT(t_px, t_py)); 
    AssertEquivalence(top.eta, T.Eta(t_px, t_py, t_pz)); 
    AssertEquivalence(top.phi, T.Phi(t_px, t_py)); 
    
    c_pt = MakeTensor(top.pt, "cuda")
    c_eta = MakeTensor(top.eta, "cuda")
    c_phi = MakeTensor(top.phi, "cuda")

    AssertEquivalence(top._px, C.Px(c_pt, c_phi))
    AssertEquivalence(top._py, C.Py(c_pt, c_phi))
    AssertEquivalence(top._pz, C.Pz(c_pt, c_eta))
    
    c_px = MakeTensor(top._px, "cuda")
    c_py = MakeTensor(top._py, "cuda")
    c_pz = MakeTensor(top._pz, "cuda")

    AssertEquivalence(top.pt,  C.PT(c_px, c_py)[0])
    AssertEquivalence(top.eta, C.Eta(c_px, c_py, c_pz)[0])
    AssertEquivalence(top.phi, C.Phi(c_px, c_py)[0])

    l = [top._px, top._py, top._pz]
    AssertEquivalenceList(l, F.PxPyPz(top.pt, top.eta, top.phi))
    AssertEquivalenceList(l, T.PxPyPz(t_pt, t_eta, t_phi)[0])
    AssertEquivalenceList(l, C.PxPyPz(c_pt, c_eta, c_phi)[0])

    l = [top.pt, top.eta, top.phi] 
    AssertEquivalenceList(l, F.PtEtaPhi(top._px, top._py, top._pz))
    AssertEquivalenceList(l, T.PtEtaPhi(t_px, t_py, t_pz)[0])
    AssertEquivalenceList(l, C.PtEtaPhi(c_px, c_py, c_pz)[0])
     
    for c in event.TopChildren:
        _tmp.append([c.pt, c.eta, c.phi])
        _tmp2.append([c._px, c._py, c._pz])


# ===== Test the performance difference ===== #
CPU = torch.tensor(_tmp, device = "cpu")
CUDA = torch.tensor(_tmp, device = "cuda")
c_pt = CUDA[:, 0].clone()
c_eta = CUDA[:, 1].clone()
c_phi = CUDA[:, 2].clone()

t1 = time()
cpu_r = T.PxPyPz(CPU[:, 0], CPU[:, 1], CPU[:, 2])
diff1 = time() - t1

t1 = time()
cuda_r = C.PxPyPz(c_pt, c_eta, c_phi)
diff2 = time() - t1

AssertEquivalenceRecursive(cpu_r, cuda_r)

print("--- Testing Performance Between C++ and CUDA of PxPyPz ---")
print("Speed Factor (> 1 is better): ", diff1 / diff2)

CPU = torch.tensor(_tmp2, device = "cpu")
CUDA = torch.tensor(_tmp2, device = "cuda")
c_px = CUDA[:, 0].clone()
c_py = CUDA[:, 1].clone()
c_pz = CUDA[:, 2].clone()

t1 = time()
cpu_r = T.PtEtaPhi(CPU[:, 0], CPU[:, 1], CPU[:, 2])
diff1 = time() - t1

t1 = time()
cuda_r = C.PtEtaPhi(c_px, c_py, c_pz)
diff2 = time() - t1

AssertEquivalenceRecursive(cpu_r, cuda_r)
print("--- Testing Performance Between C++ and CUDA of PtEtaPhi ---")
print("Speed Factor (> 1 is better): ", diff1 / diff2)

