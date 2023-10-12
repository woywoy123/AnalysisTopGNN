import pyc.Transform as F
import torch
from AnalysisG.Particles.Particles import Neutrino
import pyc

mW = 80.385*1000 # MeV : W Boson Mass
mT = 172.5*1000  # MeV : t Quark Mass
mT_GeV = 172.5   # GeV : t Quark Mass
mW_GeV = 80.385  # GeV : W boson mass
mN = 0           # GeV : Neutrino Mass
device = "cpu"

# Transform all event properties into torch tensors

coef = 1 # 1e-3 for GeV, 1 for MeV

def MakeKinematics(obj):
    return [[obj.pt*coef, obj.eta, obj.phi, obj.e*coef]]

def MakeTensor(val):
    return torch.tensor([val], dtype = torch.float64, device = self.device)

def MakeParticle(inpt):
    # Nu = Neutrino()
    return Neutrino(inpt[0]/coef, inpt[1]/coef, inpt[2]/coef)
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
    # try:
    # print('reconstructing...')
    scale = 1000
    s_ = pyc.NuSol.Polar.NuNu(
            MakeKinematics(b0), MakeKinematics(b1), MakeKinematics(lep0), MakeKinematics(lep1), [[met*coef, met_phi]], [[mW*coef, mT*coef, mN*coef]])
    # except:
    #     print('Singular')
    #     return []
    it = -1
    # Test if a solution was found
    if not s_[-1]:
        # print('failed :(')
        return None
    # print('succeeded :)')
    # for i in s_:
    #     print(i)
    # Collect all solutions and choose one
    neutrinos = []
    nu1, nu2 = s_[0][0], s_[1][0]
    for k in range(len(nu1)):
        neutrino1 = MakeParticle(nu1[k].tolist())
        neutrino2 = MakeParticle(nu2[k].tolist())
        # print('made two neutrinos', neutrino1, neutrino2)
        neutrinos.append([neutrino1, neutrino2])
    return neutrinos
