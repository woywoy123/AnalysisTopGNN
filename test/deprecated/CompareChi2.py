from AnalysisTopGNN import Analysis
from AnalysisTopGNN.Events import Event
from AnalysisTopGNN.IO import UnpickleObject, PickleObject
import PyC.NuSol.Tensors as NuT
import PyC.NuSol.CUDA as NuC
from NeutrinoSolutionDeconstruct import *
from Checks import *
from time import time
import torch

torch.set_printoptions(precision=20)
torch.set_printoptions(linewidth=120)
import math
from AnalysisTopGNN.Plotting import TH1F, CombineTH1F


def ParticleCollectors(ev):
    t1 = [t for t in ev.Tops if t.LeptonicDecay][0]
    t2 = [t for t in ev.Tops if t.LeptonicDecay][1]

    out = []
    prt = {abs(p.pdgid): p for p in t1.Children}
    b = prt[5]
    lep = [prt[i] for i in [11, 13, 15] if i in prt][0]
    nu = [prt[i] for i in [12, 14, 16] if i in prt][0]
    out.append([b, lep, nu, t1])

    prt = {abs(p.pdgid): p for p in t2.Children}
    b = prt[5]
    lep = [prt[i] for i in [11, 13, 15] if i in prt][0]
    nu = [prt[i] for i in [12, 14, 16] if i in prt][0]
    out.append([b, lep, nu, t2])

    return out


Ana = Analysis()
Ana.InputSample(
    "bsm4t-1000-All", "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000"
)
# Ana.InputSample("bsm4t-1000", "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root")
Ana.Event = Event
# Ana.EventStop = 100
Ana.EventCache = True
Ana.DumpPickle = True
Ana.Tree = "nominal"
Ana.chnk = 100
Ana.VerboseLevel = 2
Ana.Launch()
vl = {"b": [], "lep": [], "nu": [], "ev": [], "t": []}

l = 0
for i in Ana:
    ev = i.Trees["nominal"]
    tops = [t for t in ev.Tops if t.LeptonicDecay]

    if len(tops) == 2:
        k = ParticleCollectors(ev)
        vl["b"].append([k[0][0], k[1][0]])
        vl["lep"].append([k[0][1], k[1][1]])
        vl["nu"].append([k[0][2], k[1][2]])
        vl["t"].append([k[0][3], k[1][3]])
        vl["ev"].append(ev)
        l += 1

T = SampleTensor(vl["b"], vl["lep"], vl["ev"], vl["t"], "cuda", [[100, 0], [0, 100]])
R = SampleVector(vl["b"], vl["lep"], vl["ev"], vl["t"])
t_solC = NuC.NuNuPtEtaPhiE(
    T.b, T.b_, T.mu, T.mu_, T.met, T.phi, T.mT, T.mW, T.mN, 1e-12
)
t_solCR = NuC.NuNuPtEtaPhiE(
    T.b_, T.b, T.mu_, T.mu, T.met, T.phi, T.mT, T.mW, T.mN, 1e-12
)

# b, b_, mu, mu_ as input
x_PyT = []
x_R = []

# b_, b, mu_, mu as input
x_PyTR = []
x_RR = []

# Assess the cases where the eigenvalues of the two ellipses are all imaginary - i.e. empty list
# b, b_, mu, mu_
x_RDiag = 0
x_PyTDiag = []

x_RDiagR = 0
x_PyTDiagR = []

it = 0
itR = 0
for t, tr, r in zip(t_solC[0], t_solCR[0], R):
    b, mu = r[0], r[1]
    _b, _mu = r[2], r[3]
    met_x, met_y = r[4], r[5]
    mT, mW, mNu = r[6], r[7], r[8]

    if t == False:
        sol = doubleNeutrinoSolutions(
            (b, _b), (mu, _mu), (met_x, met_y), mW**2, mT**2
        )
        diag_ = [math.log(k) for k in sol.diag if k > 0.0]
        diag_t = [math.log(k) for t in t_solC[6][it].tolist() for k in t if k > 0.0]
        it += 1

        if len(diag_) == 0:
            x_RDiag += 1
            x_PyTDiag += diag_t
        else:
            x_R += diag_
            x_PyT += diag_t

    if tr == False:
        sol = doubleNeutrinoSolutions(
            (_b, b), (_mu, mu), (met_x, met_y), mW**2, mT**2
        )
        diag_ = [math.log(k) for k in sol.diag if k > 0.0]
        diag_t = [math.log(k) for t in t_solCR[6][itR].tolist() for k in t if k > 0.0]
        itR += 1

        if len(diag_) == 0:
            x_RDiagR += 1
            x_PyTDiagR += diag_t
        else:
            x_RR += diag_
            x_PyTR += diag_t

# Case for b, b_, mu, mu_ as input to double neutrino
print("--> Discrepency number (%): ", (x_RDiag / l) * 100)
Th = TH1F()
Th.xData = x_PyTDiag
Th.xStep = 1
Th.xMin = -100
Th.Title = "PyTorch/Original Yielding non-Imaginary/Empty Entries"

ThT = TH1F()
ThT.xData = x_PyT
ThT.xStep = 1
ThT.xMin = -100
ThT.Title = "PyTorch"

ThR = TH1F()
ThR.xData = x_R
ThR.Texture = True
ThR.xStep = 1
ThR.xMin = -100
ThR.Title = "Original"

CH = CombineTH1F()
CH.Histograms = [ThR, ThT, Th]
CH.xMin = -100
CH.xStep = 10
CH.Title = "Diagonal Eigenvalues from Ellipse Intersections"
CH.xTitle = "log(diagonal)"
CH.yTitle = "Entries (arb.)"
CH.Filename = "Eigenvalues-Common"
CH.SaveFigure()

# Case for b_, b, mu_, mu as input to double neutrino
print("--> (Reversed) Discrepency number (%): ", (x_RDiagR / l) * 100)
Th_ = TH1F()
Th_.xData = x_PyTDiagR
Th_.xStep = 1
Th_.xMin = -100
Th_.Title = "PyTorch/Original Yielding non-Imaginary/Empty Entries"

ThT_ = TH1F()
ThT_.xData = x_PyTR
ThT_.xStep = 1
ThT_.xMin = -100
ThT_.Title = "PyTorch"

ThR_ = TH1F()
ThR_.xData = x_RR
ThR_.Texture = True
ThR_.xStep = 1
ThR_.xMin = -100
ThR_.Title = "Original"

CH = CombineTH1F()
CH.Histograms = [ThR_, ThT_, Th_]
CH.xMin = -100
CH.xStep = 10
CH.Title = "Diagonal Eigenvalues from Ellipse Intersections - Reversed Particle Input"
CH.xTitle = "log(diagonal)"
CH.yTitle = "Entries (arb.)"
CH.Filename = "Eigenvalues-Common-Reversed"
CH.SaveFigure()


# ======= Individual Plots for comparison ======= #
Th_.Title = "Reversed"
Th.Title = "Non-Reversed"
CH = CombineTH1F()
CH.Histograms = [Th, Th_]
CH.xMin = -100
CH.xStep = 10
CH.Title = "Discrepency Generation by From Reversed Particle Input"
CH.xTitle = "log(diagonal)"
CH.yTitle = "Entries (arb.)"
CH.Filename = "Discrepency"
CH.SaveFigure()

ThT_.Title = "Reversed"
ThT.Title = "Non-Reversed"
CH = CombineTH1F()
CH.Histograms = [ThT_, ThT]
CH.xMin = -100
CH.xStep = 10
CH.Title = "Diagonal Eigenvalues from Ellipse Intersections from PyTorch \n Reversed/non-Reversed Particle Input"
CH.xTitle = "log(diagonal)"
CH.yTitle = "Entries (arb.)"
CH.Filename = "PyTorch"
CH.SaveFigure()

ThR_.Title = "Reversed"
ThR.Title = "Non-Reversed"
CH = CombineTH1F()
CH.Histograms = [ThR_, ThR]
CH.xMin = -100
CH.xStep = 10
CH.Title = "Diagonal Eigenvalues from Ellipse Intersections from Original \n Reversed/non-Reversed Particle Input"
CH.xTitle = "log(diagonal)"
CH.yTitle = "Entries (arb.)"
CH.Filename = "Original"
CH.SaveFigure()
