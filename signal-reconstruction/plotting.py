from AnalysisTopGNN.Plotting import TH1F, TH2F, CombineTH1F

def TemplatePlotsTH1F(x):
    Plots = {
                "NEvents" : x.NEvents, 
                "ATLASLumi" : x.Luminosity, 
                "Style" : "ATLAS", 
                "LaTeX": False,
                "OutputDirectory" : "./Figures/", 
                "yTitle" : "Entries (a.u.)", 
                "yMin" : 0, "xMin" : 0
            }
    return Plots

def PlotEfficiency(x):
    for i,efficiency_dict in enumerate([x.efficiencies, x.efficiency_avg]):
        for object_type in efficiency_dict.keys():
            for method in range(2):
                Plots_ = TemplatePlotsTH1F(x)
                Plots_["Title"] = f"Efficiency per top group ({object_type}, method {method+1})"
                Plots_["xTitle"] = "Efficiency"
                Plots_["Histograms"] = []
                for case_num in efficiency_dict[object_type].keys():
                    Plots = {}
                    Plots["Title"] = f"{object_type} {case_num}"
                    if i == 0:
                        xdata = [num for sublist in efficiency_dict[object_type][case_num][method] for num in sublist]
                    else:
                        xdata = efficiency_dict[object_type][case_num][method]
                    Plots["xData"] = xdata
                    thc = TH1F(**Plots)
                    Plots_["Histograms"].append(thc)
                Plots_["xMin"] = 0
                Plots_["xMax"] = 1
                Plots_["xStep"] = 0.1
                Plots_["Filename"] = f"{'Efficiency_group' if i == 0 else 'Efficiency_event'}_{object_type}_case{case_num}_method{method+1}"
                tc = CombineTH1F(**Plots_)
                tc.SaveFigure()
