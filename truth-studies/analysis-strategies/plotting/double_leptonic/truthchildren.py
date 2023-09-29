from AnalysisG.Plotting import TH1F, CombineTH1F

setting = {
        "Style" : "ATLAS",
        "ATLASLumi" : None,
        "NEvents" : None,
        "OutputDirectory" : "./Plotting/Dilepton/TruthChildren",
        "Histograms" : [],
        "Histogram" : None,
        "LegendLoc" : "upper right"
}



def doubleleptonic_Plotting(inpt, truth):
    params = dict(setting)
    params["NEvents"] = inpt.NEvents
    params["ATLASLumi"] = inpt.Luminosity

    for i in inpt.TopMasses:
        if len(inpt.TopMasses[i]) == 0: continue
        param_ = {}
        param_.update({"Title" : i, "xData" : inpt.TopMasses[i]})
        if i == "All": params["Histogram"] = TH1F(**param_)
        else: params["Histograms"].append(TH1F(**param_))

    params["xBins"] = 200
    params["NEvents"] = inpt.NEvents
    params["xMin"] = 100
    params["xMax"] = 300
    params["xTitle"] = "Mass of Tops (GeV)"
    params["yTitle"] = "Entries"
    params["Title"] = "Reconstructed Resonant Top Masses Segmented into \n Top Decay Mode (Had - Hadronic, Lep - Leptonic)"
    params["Filename"] = "figure_1.a"

    th = CombineTH1F(**params)
    th.SaveFigure()


    translation = {"ttbar" : [], "singletop" : [], "SM4tops" : [], "tttt" : [], "ttH" : [], "tt" : [], "Other" : []}
    reverse_trans = {}
    for i in inpt.ZPrime:
        if i == "All": continue
        keys = i.split("_")
        found = False
        for t in translation:
            for k in keys:
                if t not in k: continue
                found = True
                translation[t].append(i)
                reverse_trans[i] = t
                break
            if found: break
        if not found:
            translation["Other"].append(i)
            reverse_trans[i] = "Other"

    params["Histograms"] = []
    params["Histogram"] = None
    for i in inpt.ZPrime:
        if i == "All": continue
        rev_name = reverse_trans[i]
        data = []
        for sel in inpt.ZPrime[i]:
            data += inpt.ZPrime[i][sel]
        param_ = {"Title" : rev_name, "xData" : data}
        params["Histograms"].append(TH1F(**param_))

    params["Title"] = "Reconstructed Resonance Mass from Matching Strategy \n Segmented by Samples"
    params["xTitle"] = "Mass of Resonance (GeV)"
    params["yTitle"] = "Entries"
    params["xBins"] = 500
    params["xMin"] = 0
    params["xMax"] = 2000
    params["xStep"] = 100
    params["Filename"] = "figure_1.b"
    th = CombineTH1F(**params)
    th.SaveFigure()

    nevents = inpt.TotalEvents
    print("____ CUTFLOW REPORT _____")
    print("N-Events: ", nevents)
    for i in inpt.CutFlow:
        print("-> "+ i.replace(" -> ", "::"), (inpt.CutFlow[i]/nevents)*100, "%")

    print("")
    print("________ ERRORS _________")
    for i in inpt.Errors:
        print("ERROR: " + i, inpt.Error[i])
    if len(inpt.Errors) == 0: print("NONE")



