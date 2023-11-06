from AnalysisG.Plotting import TH1F, TH2F
from dataset_mapping import DataSets

def settings(output):
    setting = {
            "Style" : "ATLAS",
            "ATLASLumi" : None,
            "NEvents" : None,
            "OutputDirectory" : "./Plotting/Dilepton/" + output,
            "Histograms" : [],
            "Histogram" : None,
            "LegendLoc" : "upper right"
    }
    return {i : x for i, x in setting.items()}

def doubleleptonic_Plotting(inpt, truth):
    d = DataSets()
    params = settings(truth)
    params["NEvents"] = inpt.nPassedEvents
    for i in inpt.TopMasses:
        if len(inpt.TopMasses[i]) == 0: continue
        param_ = {}
        param_.update({"Title" : i, "xData" : inpt.TopMasses[i]})
        if i == "All": params["Histogram"] = TH1F(**param_)
        else: params["Histograms"].append(TH1F(**param_))

    params["ATLASLumi"] = inpt.Luminosity
    params["xBins"] = 100
    params["xStep"] = 40
    params["xMin"] = 100
    params["xMax"] = 300
    params["Alpha"] = 0.75
    params["Stack"] = True
    params["xTitle"] = "Mass of Tops (GeV)"
    params["yLogarithmic"] = True
    params["yTitle"] = "Entries"
    params["Title"] = "Reconstructed Resonant Top Masses Segmented into \n Top Decay Mode (Had - Hadronic, Lep - Leptonic)"
    params["Filename"] = "figure_1.a"
    th = TH1F(**params)
    th.SaveFigure()

    for x, f in zip(["Lep-Had", "Had-Had", "Lep-Lep"], ["a", "b", "c"]):
        params = settings(truth)
        params["ATLASLumi"] = inpt.Luminosity
        params["Title"] = "Reconstructed Resonance Mass from Matching Strategy \n (Decay Mode: " + x + " )"
        params["xTitle"] = "Mass of Resonance (GeV)"
        params["yTitle"] = "Entries"
        params["xMin"] = 0
        params["xMax"] = 2000
        params["xBins"] = 50
        params["xStep"] = 100
        params["Alpha"] = 0.75
        params["Stack"] = True
        params["Filename"] = "figure_2." + f

        samples = {}
        for i in inpt.ZPrime:
            fname = d.CheckThis(i)
            if x not in inpt.ZPrime[i]: continue
            if fname not in samples: samples[fname] = []
            else:samples[fname] += inpt.ZPrime[i][x]

        for i in samples:
            param_ = {}
            param_.update({"Title" : i, "xData" : samples[i]})
            params["Histograms"].append(TH1F(**param_))

        th = TH1F(**params)
        th.SaveFigure()

    jet_vs_mode = {}
    mode_smpl = {}
    for file in inpt.PhaseSpaceZ:
        fname = d.CheckThis(file)

        for jets in inpt.PhaseSpaceZ[file]:
            for lep_s, data in inpt.PhaseSpaceZ[file][jets].items():
                mode = ""
                if lep_s.count("+") and lep_s.count("-"): mode = "2l-OS"
                elif lep_s.count("+") == 2: mode = "2l-SS"
                elif lep_s.count("-") == 2: mode = "2l-SS"
                elif len(lep_s): mode = "1l"
                else: mode = "0l"

                if jets not in jet_vs_mode: jet_vs_mode[jets] = {}
                if mode not in jet_vs_mode[jets]: jet_vs_mode[jets][mode] = {}
                if fname not in jet_vs_mode[jets][mode]: jet_vs_mode[jets][mode][fname] = []

                if mode not in mode_smpl: mode_smpl[mode] = {}
                if fname not in mode_smpl[mode]: mode_smpl[mode][fname] = []

                jet_vs_mode[jets][mode][fname] += data
                mode_smpl[mode][fname] += data

    for mode, f in zip(mode_smpl, ["a", "b", "c", "d", "e", "f"]):
        params = settings(truth)
        params["ATLASLumi"] = round(inpt.Luminosity, 3)
        params["Title"] = "Reconstructed Resonance Mass from Matching Strategy \n (Decay Mode: " + mode + " )"
        params["xTitle"] = "Mass of Resonance (GeV)"
        params["yTitle"] = "Entries"
        params["xMin"] = 0
        params["xMax"] = 2000
        params["xBins"] = 50
        params["xStep"] = 100
        params["Alpha"] = 0.75
        params["Stack"] = True
        params["Filename"] = "figure_3." + f

        for smpl, data in mode_smpl[mode].items():
            param_ = {}
            param_.update({"Title" : smpl, "xData" : data})
            params["Histograms"].append(TH1F(**param_))
        th = TH1F(**params)
        th.SaveFigure()

    nevents = inpt.TotalEvents
    print("____ CUTFLOW REPORT _____")
    print("N-Events: ", nevents)
    for i in inpt.CutFlow:
        print("-> "+ i.replace(" -> ", "::"), (inpt.CutFlow[i]/nevents)*100, "%")


