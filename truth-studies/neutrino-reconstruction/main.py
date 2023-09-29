from selection import NeutrinoReconstruction
from AnalysisG.Plotting import TH1F, CombineTH1F, TH2F
from AnalysisG.Events import Event
from AnalysisG.IO import nTupler
from AnalysisG import Analysis

import os
smpl = os.environ["Samples"]

mass = "900"
Ana = Analysis()
Ana.OutputDirectory = "./Reconstruction"
Ana.InputSample("bsm" + mass, smpl+"/ttZ-" + mass + "/")
Ana.AddSelection("neutrino", NeutrinoReconstruction)
#Ana.EventStop = 1000
Ana.Event = Event
Ana.Threads = 12
Ana.chnk = 1000
Ana.EventCache = True
Ana.Launch

x = nTupler()
x.InputSelection("Reconstruction/UNTITLED/Selections/neutrino")
x.This("neutrino -> ", "nominal")
x.Threads = 12
nu = x.merged["NeutrinoReconstruction"]

# Compare the number of solutions for GeV and MeV 
thc = CombineTH1F()
thc.xMin = 0
thc.xBins = 6
thc.xStep = 1
thc.xBinCentering = True
thc.Title = "Number of Neutrino Solutions Using MeV vs GeV"
thc.xTitle = "Number of Solutions"
thc.Filename = "neutrino-solutions"
thc.OutputDirectory = "./Plotting"

for key in nu.num_sols:
    th = TH1F()
    th.Title = "NSols-" + key
    th.xData = nu.num_sols[key]
    thc.Histograms.append(th)
thc.SaveFigure()


# Compare the mass distribution of the reconstructed tops to the truth
thc = CombineTH1F()
thc.xMin = 0
thc.xBins = 100
thc.xStep = 20
thc.xMax = 400
thc.Logarithmic = True
thc.Title = "Reconstructed Top Invariant Mass Distribution From Neutrinos \n (Dilepton Channel)"
thc.xTitle = "Invariant Mass (GeV)"
thc.OutputDirectory = "./Plotting"
thc.Filename = "top-dilepton"

for key in nu.top_mass_r2l:
    th = TH1F()
    th.Title = "reco using " + key
    th.xData = nu.top_mass_r2l[key]
    thc.Histograms.append(th)

th = TH1F()
th.Title = "truth"
th.xData = nu.top_mass_t2l["children"]
thc.Histogram = th

thc.SaveFigure()

# Compare the mass distribution of the reconstructed tops to the truth
thc = CombineTH1F()
thc.xMin = 0
thc.xBins = 100
thc.xStep = 20
thc.xMax = 400
thc.Logarithmic = True
thc.Title = "Reconstructed Top Invariant Mass Distribution From Neutrinos \n (Single Lepton Channel)"
thc.xTitle = "Invariant Mass (GeV)"
thc.OutputDirectory = "./Plotting"
thc.Filename = "top-singlelepton"

for key in nu.top_mass_r1l:
    th = TH1F()
    th.Title = "reco using " + key
    th.xData = nu.top_mass_r1l[key]
    thc.Histograms.append(th)

th = TH1F()
th.Title = "truth"
th.xData = nu.top_mass_t1l["children"]
thc.Histogram = th

thc.SaveFigure()

# Compare the mass distribution of the reconstructed H to the truth
thc = CombineTH1F()
thc.xMin = 0
thc.xBins = 500
thc.xStep = 200
thc.xMax = 2200
thc.Logarithmic = True
thc.Normalize = True
thc.Title = "Reconstructed Scalar H Invariant Mass Distribution \n From Neutrinos (Dilepton Channel)"
thc.xTitle = "Invariant Mass (GeV)"
thc.OutputDirectory = "./Plotting"
thc.Filename = "H-dilepton"

for key in nu.top_mass_r1l:
    th = TH1F()
    th.Title = "reco using " + key
    th.xData = nu.H_mass_r2l[key]
    thc.Histograms.append(th)

th = TH1F()
th.Title = "truth"
th.xData = nu.H_mass_t2l["children"]
thc.Histogram = th

thc.SaveFigure()

# ______ Compare the kinematics between MeV and GeV with truth ___________ #
# ================================== px - py ======================================= 
th2 = TH2F()
th2.Title = "Difference in {x, y}-Momenta between Reconstructed and Truth Tops \n From Neutrinos using MeV (Dilepton Channel)"
th2.xTitle = "$100 x |\\Delta px_{MeV}|/(px_{truth})$ - (%)"
th2.yTitle = "$100 x |\\Delta py_{MeV}|/(py_{truth})$ - (%)"
th2.xBins = 100
th2.yBins = 100

th2.xMin = 0
th2.xMax = 100

th2.yMin = 0
th2.yMax = 100

th2.xData = nu.top_kin_r2l["mev"]["px"]
th2.yData = nu.top_kin_r2l["mev"]["py"]
th2.Filename = "top-double-kin-px_py-mev"
th2.OutputDirectory = "./Plotting/"
th2.SaveFigure()

th2 = TH2F()
th2.Title = "Difference in {x, y}-Momenta between Reconstructed and Truth Tops \n From Neutrinos using GeV (Dilepton Channel)"
th2.xTitle = "$100 x |\\Delta px_{GeV}|/(px_{truth})$ - (%)"
th2.yTitle = "$100 x |\\Delta py_{GeV}|/(py_{truth})$ - (%)"
th2.xBins = 100
th2.yBins = 100

th2.xMin = 0
th2.xMax = 100

th2.yMin = 0
th2.yMax = 100

th2.xData = nu.top_kin_r2l["gev"]["px"]
th2.yData = nu.top_kin_r2l["gev"]["py"]
th2.Filename = "top-double-kin-px_py-gev"
th2.OutputDirectory = "./Plotting/"
th2.SaveFigure()

# ================================== e - pz ======================================= 
th2 = TH2F()
th2.Title = "Difference in {e, z}-Momenta between Reconstructed and Truth Tops \n From Neutrinos using MeV (Dilepton Channel)"
th2.xTitle = "$100 x |\\Delta pz_{MeV}|/(pz_{truth})$ - (%)"
th2.yTitle = "$100 x |\\Delta e_{MeV}|/(e_{truth})$ - (%)"
th2.xBins = 100
th2.yBins = 100

th2.xMin = 0
th2.xMax = 100

th2.yMin = 0
th2.yMax = 100

th2.xData = nu.top_kin_r2l["mev"]["pz"]
th2.yData = nu.top_kin_r2l["mev"]["e"]
th2.Filename = "top-double-kin-pz_e-mev"
th2.OutputDirectory = "./Plotting/"
th2.SaveFigure()

th2 = TH2F()
th2.Title = "Difference in {e, z}-Momenta between Reconstructed and Truth Tops \n From Neutrinos using GeV (Dilepton Channel)"
th2.xTitle = "$100 x |\\Delta pz_{GeV}|/(pz_{truth})$ - (%)"
th2.yTitle = "$100 x |\\Delta e_{GeV}|/(e_{truth})$ - (%)"
th2.xBins = 100
th2.yBins = 100

th2.xMin = 0
th2.xMax = 100

th2.yMin = 0
th2.yMax = 100

th2.xData = nu.top_kin_r2l["gev"]["pz"]
th2.yData = nu.top_kin_r2l["gev"]["e"]
th2.Filename = "top-double-kin-pz_e-gev"
th2.OutputDirectory = "./Plotting/"
th2.SaveFigure()



