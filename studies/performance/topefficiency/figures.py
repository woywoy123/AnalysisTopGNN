from torchmetrics.classification import MulticlassAUROC, BinaryAUROC
from AnalysisG.core.plotting import TH1F, TH2F, TLine
from AnalysisG.core import Meta
from pathlib import Path
from .algorithms import *
import pickle

global figure_path
def path(hist, subx = ""):
    hist.Style = "ATLAS"
    hist.OutputDirectory = figure_path + "/topefficiency" + subx
    return hist

def top_kinematic_region(stacks, data = None):
    if data is not None: return top_pteta(stacks, data)

    prc_topscore = {}
    top_score_mass = {}
    ks_topscore_eta_pt = {}
    pt_topmass_prc = {"truth" : {}, "prediction" : {}}

    meta_cache = {}
    for kin in set(list(stacks["truth"]) + list(stacks["prediction"])):
        pt_r = kin.split(",")[0]
        tru_h = None

        if pt_r not in pt_topmass_prc["truth"]: pt_topmass_prc["truth"][pt_r] = {"v" : [], "w" : []}
        if kin in stacks["truth"]:
            prx = list(stacks["truth"][kin])

            tru_h = TH1F()
            tru_h.Title = "Truth"
            tru_h.xData   = sum([stacks["truth"][kin][f]["value"]   for f in prx], [])
            tru_h.Weights = sum([stacks["truth"][kin][f]["weights"] for f in prx], [])
            tru_h.Hatch = "\\\\////"
            tru_h.Color = "black"
            pt_topmass_prc["truth"][pt_r]["v"] += sum([stacks["truth"][kin][f]["value"]   for f in prx], [])
            pt_topmass_prc["truth"][pt_r]["w"] += sum([stacks["truth"][kin][f]["weights"] for f in prx], [])

        if kin not in stacks["prediction"]: stacks["prediction"][kin] = {}

        hists = {}
        for prc in stacks["prediction"][kin]:
            try: meta = meta_cache[prc]
            except KeyError:
                spl = prc.split(".")
                meta = Meta()
                meta.MetaCachePath = "meta.h5"
                meta.FetchMeta(int(spl[2]), spl[5])
                meta_cache[prc] = meta
            _, tl = mapping(meta.DatasetName)

            if tl not in hists: hists[tl] = {"value": [], "weights" : []}
            hists[tl]["value"]   += stacks["prediction"][kin][prc]["value"]
            hists[tl]["weights"] += stacks["prediction"][kin][prc]["weights"]

            if pt_r not in pt_topmass_prc["prediction"]: pt_topmass_prc["prediction"][pt_r] = {}
            if tl not in pt_topmass_prc["prediction"][pt_r]: pt_topmass_prc["prediction"][pt_r][tl] = {"v" : [], "w" : []}
            pt_topmass_prc["prediction"][pt_r][tl]["v"] += stacks["prediction"][kin][prc]["value"]
            pt_topmass_prc["prediction"][pt_r][tl]["w"] += stacks["prediction"][kin][prc]["weights"]

            if pt_r not in top_score_mass: top_score_mass[pt_r] = {"mass" : {"v" : [], "w" : []}, "score" : {"v" : [], "w" : []}}
            top_score_mass[pt_r]["mass"]["v"]  += stacks["prediction"][kin][prc]["value"]
            top_score_mass[pt_r]["score"]["v"] += stacks["top_score"][kin][prc]["value"]

            top_score_mass[pt_r]["mass"]["w"]  += stacks["prediction"][kin][prc]["weights"]
            top_score_mass[pt_r]["score"]["w"] += stacks["top_score"][kin][prc]["weights"]

            if pt_r not in prc_topscore: prc_topscore[pt_r] = {}
            if tl not in prc_topscore[pt_r]: prc_topscore[pt_r][tl] = {"v" : [], "w" : []}
            prc_topscore[pt_r][tl]["v"] += stacks["top_score"][kin][prc]["value"]
            prc_topscore[pt_r][tl]["w"] += stacks["top_score"][kin][prc]["weights"]
            stacks["top_score"][kin][prc] = []
            stacks["prediction"][kin][prc] = []

        for prc in hists:
            prc_h = TH1F()
            prc_h.Title   = prc
            prc_h.xData   = hists[prc]["value"]
            prc_h.Weights = hists[prc]["weights"]
            hists[prc] = prc_h

        tlt = kin.replace("_", " \\leq p^{top}_T (GeV) \\leq ")
        tlt = tlt.replace("-", " \\leq | \\eta_{top} | \\leq ")

        reco = path(TH1F(), "/" + kin.split(",")[0])
        reco.Title = "Reconstructed Invariant Mass of Top Candidate within \n Kinematic Region: $" + tlt + "$"
        reco.Histograms = list(hists.values())
        reco.Histogram = tru_h
        reco.Stacked = True
        reco.xStep = 20
        reco.Overflow = False
        reco.xTitle = "Invariant Mass of Candidate Top (GeV)"
        reco.yTitle = "Entries / ($1$ GeV)"
        reco.xMin = 0
        reco.xMax = 400
        reco.xBins = 400
        reco.Filename = kin.split(", ")[1]
        reco.SaveFigure()

        try: ks = float(reco.KStest(tru_h).pvalue)
        except: ks = 0

        ks_topscore_eta_pt[kin] = ks

    for kin in set(list(pt_topmass_prc["truth"]) + list(pt_topmass_prc["prediction"])):
        tru = TH1F()
        tru.Title = "Truth"
        tru.xData   = pt_topmass_prc["truth"][kin]["v"]
        tru.Weights = pt_topmass_prc["truth"][kin]["w"]
        tru.Hatch = "\\\\////"
        tru.Color = "black"

        hists = []
        for prc in pt_topmass_prc["prediction"][kin]:
            prc_h = TH1F()
            prc_h.Title   = prc
            prc_h.xData   = pt_topmass_prc["prediction"][kin][prc]["v"]
            prc_h.Weights = pt_topmass_prc["prediction"][kin][prc]["w"]
            hists.append(prc_h)

        tlt = kin.replace("_", " \\leq p^{top}_T (GeV) \\leq ")
        reco = path(TH1F(), "/aggregated-pt/")
        reco.Title = "Reconstructed Invariant Mass of Top Candidate with \n Transverse Momentum: $" + tlt + "$"
        reco.Histograms = hists
        reco.Histogram = tru
        reco.xStep = 20
        reco.Stacked = True
        reco.Overflow = False
        reco.xTitle = "Invariant Mass of Candidate Top (GeV)"
        reco.yTitle = "Entries / ($1$ GeV)"
        reco.xMin = 0
        reco.xMax = 400
        reco.xBins = 400
        reco.Filename = kin.split(", ")[0]
        reco.SaveFigure()

    for kin in prc_topscore:

        hists = []
        for prc in prc_topscore[kin]:
            prc_h = TH1F()
            prc_h.Title   = prc
            prc_h.xData   = prc_topscore[kin][prc]["v"]
            prc_h.Weights = prc_topscore[kin][prc]["w"]
            hists.append(prc_h)

        tlt = kin.replace("_", " \\leq p^{top}_T (GeV) \\leq ")
        s_s = path(TH1F(), "/pt-score")
        s_s.Histograms = hists
        s_s.Title = "Reconstructed Top Candidate Score with \n Transverse Momentum $" + tlt + "$"
        s_s.xTitle = "MVA Score of Candidate Top (Arb.)"
        s_s.yTitle = "Entries / ($0.01$)"

        s_s.xMin = 0
        s_s.xMax = 1
        s_s.xBins = 100
        s_s.xStep = 0.05
        s_s.Stacked = True

        s_s.Filename = "mva-score_" + kin
        s_s.SaveFigure()


    for kin in top_score_mass:
        tlt = kin.replace("_", " \\leq p^{top}_T (GeV) \\leq ")

        mass_s = path(TH2F(), "/score-mass")
        mass_s.Title = "Reconstructed Top Candidate Score as a \n function of Invariant Mass for $" + tlt + "$"
        mass_s.xTitle = "Reconstructed Top Candidate Invariant Mass / ($1$ GeV)"
        mass_s.yTitle = "MVA Score of Candidate Top / ($0.01$)"

        mass_s.xMin = 0
        mass_s.xMax = 400
        mass_s.xBins = 400
        mass_s.xStep = 20

        mass_s.yMin = 0
        mass_s.yMax = 1
        mass_s.yStep = 0.05
        mass_s.yBins = 100

        mass_s.xData   = top_score_mass[kin]["mass"]["v"]
        mass_s.yData   = top_score_mass[kin]["score"]["v"]
        mass_s.Weights = top_score_mass[kin]["score"]["w"]
        mass_s.Filename = "pt_range_" + kin
        mass_s.SaveFigure()

    eta_pt_ks = path(TH2F(), "/statistics")
    eta_pt_ks.Title = "Kolmogorov-Smirnov Test Statistic for Candidate to Truth Top \n Distribution for Various Kinematic Regions"
    eta_pt_ks.xTitle = "Reconstructed Top Candidate $p_T$ / ($100$ GeV)"
    eta_pt_ks.yTitle = "Pseudorapidity of Top Candidate / ($0.05 \\eta$)"

    eta_pt_ks.xMin = 0
    eta_pt_ks.xMax = 1500
    eta_pt_ks.xBins = 15
    eta_pt_ks.xStep = 100

    eta_pt_ks.yMin = 0
    eta_pt_ks.yMax = 6
    eta_pt_ks.yStep = 0.5
    eta_pt_ks.yBins = 12

    eta_pt_ks.xData = [float(k.split(",")[0].split("_")[0]) for k in ks_topscore_eta_pt]
    eta_pt_ks.yData = [float(k.split(",")[1].split("-")[0]) for k in ks_topscore_eta_pt]
    eta_pt_ks.Weights = list(ks_topscore_eta_pt.values())
    eta_pt_ks.Filename = "ks_score_eta_pt"
    eta_pt_ks.SaveFigure()

def roc_data(stacks, data = None):
    if data is not None: return roc_data_get(stacks, data)
    return 
    import torch
    t_ntops  = torch.tensor(stacks["n-tops_t"])
    p_ntops  = torch.tensor(stacks["n-tops_p"])
    t_signal = torch.tensor(stacks["signal_t"])
    p_signal = torch.tensor(stacks["signal_p"])
    t_top_edge = torch.tensor(stacks["edge_top_t"])
    p_top_edge = torch.tensor(stacks["edge_top_p"])

    metric = MulticlassAUROC(num_classes = 5, average = None)
    auc_ntops = metric(p_ntops, t_ntops)
    fig_, ax_ = metric.plot()


    print(p_top_edge.size())
    print(t_top_edge.size())
    metric = BinaryAUROC()
    auc_top_edge = metric(p_top_edge[:, 1], t_top_edge)
    fig_, ax_ = metric.plot()

    metric = BinaryAUROC()
    auc_signal = metric(p_signal[:, 1], t_signal)
    fig_, ax_ = metric.plot()

    print(auc_top_edge, auc_ntops, auc_signal)

def ntops_reco(stacks, data = None):
    return stacks
    if data is not None: return ntops_reco_compl(stacks, data, 2)
    w2 = sum(stacks["cls_ntop_w"][2])
    et = sum(stacks["e_ntop"][2]) / float(w2)
    pt = sum(stacks["e_ntop"][2]) / sum(stacks["p_ntop"][2])
    print(et, pt)

def TopEfficiency(ana):
    p = Path(ana)
    files = [str(x) for x in p.glob("**/*.pkl") if str(x).endswith(".pkl")]
    files = list(set(files))
    files = files[:1]

    stack_roc = {}
    stack_topkin = {}
    stack_ntops = {}
    for i in range(len(files)):
        print(files[i], (i+1) / len(files))
        pr = pickle.load(open(files[i], "rb"))
        stack_roc = roc_data(stack_roc, pr)
        stack_topkin = top_kinematic_region(stack_topkin, pr)
        stack_ntops = ntops_reco(stack_ntops, pr)

    ntops_reco(stack_ntops)
    roc_data(stack_roc)
    top_kinematic_region(stack_topkin)

