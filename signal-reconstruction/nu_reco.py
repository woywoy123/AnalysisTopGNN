import PyC.Transform.Floats as F
import torch
from AnalysisTopGNN.Particles.Particles import Neutrino
import PyC.NuSol.Tensors as NuT

mW = 80.385*1000 # MeV : W Boson Mass
mT = 172.5*1000  # MeV : t Quark Mass
mT_GeV = 172.5   # GeV : t Quark Mass
mW_GeV = 80.385  # GeV : W boson mass
mN = 0           # GeV : Neutrino Mass
device = "cpu"

# Transform all event properties into torch tensors

def MakeKinematics(obj):
    return torch.tensor([obj.pt/1000, obj.eta, obj.phi, obj.e/1000], dtype = torch.float64, device = self.device)

def MakeTensor(val):
    return torch.tensor([val], dtype = torch.float64, device = self.device)

def MakeParticle(inpt):
    # Nu = Neutrino()
    return Neutrino(inpt[0]*1000, inpt[1]*1000, inpt[2]*1000)
    # Nu.px = inpt[0]*1000
    # Nu.py = inpt[1]*1000
    # Nu.pz = inpt[2]*1000
#     # import vector as v
#     # vec = v.obj(x=inpt[0], y=inpt[1], z=inpt[2], m=0)
#     Nu.pt = Nu._pt#*1000
#     Nu.eta = Nu._eta
#     Nu.phi = Nu._phi
#     Nu.e = Nu._e#*1000
    # return Nu

def getNeutrinoSolutions(b0, b1, lep0, lep1, met, met_phi):
    try:
        s_ = NuT.NuNuDoublePtEtaPhiE(
            b0.pt/1000, b0.eta, b0.phi, b0.e/1000,
            b1.pt/1000, b1.eta, b1.phi, b1.e/1000,
            lep0.pt/1000, lep0.eta, lep0.phi, lep0.e/1000,
            lep1.pt/1000, lep1.eta, lep1.phi, lep1.e/1000,
            met/1000, met_phi, mT_GeV, mW_GeV, mN, 1e-12)
    except:
        # print('Singular')
        return []
    it = -1
    # Test if a solution was found
    if s_[0]:
        return None

    # Collect all solutions and choose one
    neutrinos = []
    # print(s_)
    nu1, nu2 = s_[1][0], s_[2][0]
    numSolutionsEvent = 0
    for k in range(len(nu1)):
        if sum(nu1[k] + nu2[k]) == 0:
            continue
        numSolutionsEvent += 1
        neutrino1 = MakeParticle(nu1[k].tolist())
        neutrino2 = MakeParticle(nu2[k].tolist())
        neutrinos.append([neutrino1, neutrino2])
    return neutrinos
