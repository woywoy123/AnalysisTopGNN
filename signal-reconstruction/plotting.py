from AnalysisG.Plotting import TH1F, TH2F, CombineTH1F

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

def PlotEfficiency(x, overlay='case'):
    object_types = ["Children", "TruthJet", "Jet"]
    cases = [i for i in range(10)]
    if overlay == "case":
        outer_var = object_types
        inner_var = cases
    else:
        outer_var = cases
        inner_var = object_types
    for i,efficiency_dict in enumerate([x.efficiencies, x.efficiency_avg]):
        for outer in outer_var:
            for method in range(2):
                Plots_ = TemplatePlotsTH1F(x)
                Plots_["Title"] = f"Efficiency per top group ({outer if overlay == 'case' else 'case '+str(outer)}, method {method+1})"
                Plots_["xTitle"] = "Efficiency"
                Plots_["Histograms"] = []
                for inner in inner_var:
                    object_type = outer if overlay == "case" else inner 
                    case_num = inner if overlay == "case" else outer
                    if not object_type in efficiency_dict.keys(): 
                        continue
                    if not case_num in efficiency_dict[object_type].keys(): 
                        continue
                    Plots = {}
                    Plots["Title"] = f"{object_type} {case_num}" 
                    dictdata = efficiency_dict[object_type][case_num][method] 
                    xdata = [num for sublist in dictdata for num in sublist] if isinstance(dictdata[0], list) else dictdata
                    Plots["xData"] = xdata
                    thc = TH1F(**Plots)
                    Plots_["Histograms"].append(thc)
                Plots_["xMin"] = 0
                Plots_["xMax"] = 1
                Plots_["xStep"] = 0.1
                Plots_["Filename"] = f"{'Efficiency_group' if i == 0 else 'Efficiency_event'}_{object_type if overlay == 'case' else 'case '+str(case_num)}_method{method+1}"
                tc = CombineTH1F(**Plots_)
                tc.SaveFigure()
