from .TemplateHistograms import TH1F, CombineTH1F
from .TemplateLines import TLine, CombineTLine
from AnalysisTopGNN.Tools import Tools, Tables
from AnalysisTopGNN.Statistics import Metrics


class _Comparison:
    def __init__(self):
        self.Epoch = None
        self.ModelStats = {}
        self.MinMetric = {}
        self.MaxMetric = {}
        self.ModelFeatures = {}
        self.Names = []
        self.ModelValues = {}
        self.ModelValuesError = {}

    def Process(self):
        metrics = []
        self.Names += list(self.ModelStats)

        for name in self.ModelStats:
            metrics += [m for m in list(self.ModelStats[name]) if m not in metrics]

        for m in metrics:
            self.__CompareMetric(
                m, [self.ModelStats[name][m] for name in self.Names], self.Names
            )

    def __CompareMetric(self, metric, values, names):
        valu = []
        if isinstance(values[0], dict):
            keys = list(set([t for k in values for t in k]))
            valu = {
                metric + "_" + str(t): [k[t][0] if t in k else 0 for k in values]
                for t in keys
            }
            errs = {
                metric + "_" + str(t): [k[t][1] if t in k else 0 for k in values]
                for t in keys
            }

        elif isinstance(values[0], list):
            valu = {metric: [v[0] for v in values]}
            errs = {metric: [v[1] for v in values]}

        else:
            valu = {metric: values}
            errs = {metric: [0 for m in values]}

        for m in valu:
            Min_ = min(valu[m])
            Max_ = max(valu[m])

            self.MinMetric[m] = [
                i for i, v in zip(range(len(valu[m])), valu[m]) if v == Min_
            ]
            self.MaxMetric[m] = [
                i for i, v in zip(range(len(valu[m])), valu[m]) if v == Max_
            ]

            self.ModelValues[m] = {}
            self.ModelValuesError[m] = {}

            for model, val, err in zip(names, valu[m], errs[m]):
                self.ModelValues[m][model] = val
                self.ModelValuesError[m][model] = err


class PredictionContainerPlots:
    def __init__(self):
        pass

    def GetConsistentModeColor(self, Color):
        Plt = CombineTLine()
        Line = TLine()
        for i in Color:
            Plt.ApplyRandomColor(Line)
            Color[i] = Line.Color
            Line.Color = None

    def TemplateLine(self, xData, yData, outdir, feature, up, down):
        Plots = {
            "xTitle": "Epoch",
            "xData": xData,
            "yData": yData,
            "up_yData": up,
            "down_yData": down,
            "Title": feature,
            "yMin": 0,
            "yMax": None if len(up) == 0 else max([k + i for k, i in zip(up, yData)]),
            "xMax": max(xData) + 1 if len(xData) != 0 else None,
            "xMin": min(xData) - 1 if len(xData) != 0 else None,
            "Style": "ATLAS",
            "OutputDirectory": outdir,
        }
        return Plots

    def TemplateHistograms(self, xTitle, xBins, outdir):
        Plots = {
            "xTitle": xTitle,
            "yTitle": "Entries",
            "xBins": xBins,
            "xMin": 0,
            "yMin": 0,
            "Style": "ATLAS",
            "OutputDirectory": outdir,
        }
        return Plots

    def MassPlot(self, Data, Title):
        Plots = self.TemplateHistograms("Invariant Mass (GeV)", 100, None)
        Plots["xData"] = Data
        Plots["Title"] = Title
        L1 = TH1F(**Plots)
        return L1

    def MergeMass(self, Title, Hists):
        Plots = self.TemplateHistograms("Invariant Mass (GeV)", 100, None)
        Plots["Title"] = Title
        Plots["Histograms"] = Hists
        Plots = CombineTH1F(**Plots)
        Plots.Compile()
        return Plots

    def EfficiencyHistogram(self, Data, Title):
        Plots = self.TemplateHistograms("Efficiency (GeV)", 100, None)
        Plots["xMax"] = 100
        Plots["Title"] = Title
        Plots["xData"] = Data
        Plots = TH1F(**Plots)
        return Plots

    def MergeEfficiencyHistogram(self, Title, Plots):
        Plots = self.TemplateHistograms("Efficiency (%)", 100, None)
        Plots["Title"] = Title
        Plots["Histograms"] = Plots
        Plots = CombineTH1F(**Plots)
        Plots.Compile()
        return Plots

    def EfficiencyLine(self, xData, yData, Title, Error=[]):
        Plots = self.TemplateLine(xData, yData, None, Title, Error, Error)
        Plots["yTitle"] = "Efficiency (%)"
        Plots["yMax"] = 101
        Plots = TLine(**Plots)
        Plots.Compile()
        return Plots

    def MergeEfficiencyLines(self, Title, Lines):
        Plots = self.TemplateLine(Lines[0].xData, [], None, Title, [], [])
        Plots["yTitle"] = "Efficiency (%)"
        Plots["Lines"] = Lines
        Plots["yMax"] = 101
        Plots = CombineTLine(**Plots)
        return Plots


class DataBlock(PredictionContainerPlots, Metrics):
    def __init__(self, feature):
        self.Feature = feature
        self.Truth = []
        self.Prediction = []
        self.Error = {}
        self.Epoch = None
        self.Plots = {}
        self.Process = None
        self.Efficiency = []
        self._Color = {}

    def MakeMass(self):
        p = self.MassPlot(self.Prediction, "Model")
        t = self.MassPlot(self.Truth, "Truth")
        t.Color = p.Color
        name = "Mass_" + self.Feature
        Title = (
            "Model Feature Prediction of Invariant Mass Distribution \nSuperimposed on Truth: "
            + self.Feature
            + " at Epoch "
            + str(self.Epoch)
        )
        self.Plots[name] = self.MergeMass(Title, [p, t])

    def MakeMassByProcess(self):
        DataP, DataT = {}, {}
        for prc in self.Process:
            prc_ = list(prc)[0]
            if prc_ not in DataP:
                DataP[prc_] = []
                DataT[prc_] = []
            DataP[prc_] += prc[prc_][1]
            DataT[prc_] += prc[prc_][0]

        self._Color = {prc: None for prc in DataP}
        self.GetConsistentModeColor(self._Color)
        for prc in DataP:
            DataP[prc] = self.MassPlot(DataP[prc], prc + "-model")
            DataT[prc] = self.MassPlot(DataT[prc], prc + "-truth")
            DataP[prc].Color = self._Color[prc]
            DataT[prc].Color = self._Color[prc]
            DataT[prc].Texture = True

        Title = (
            "Model Feature Prediction of Invariant Mass \n by Process: "
            + self.Feature
            + " at Epoch "
            + str(self.Epoch)
        )
        self.Plots["Mass_" + self.Feature + "_ByProcess"] = self.MergeMass(
            Title, list(DataP.values()) + list(DataT.values())
        )

    def MakeEfficiencyHistogram(self):
        Process = {}
        for prc in self.Process:
            Process[prc] = self.EfficiencyHistogram(self.Process[prc], prc)
        Title = (
            "Model Feature Prediction (" + self.Feature + ") Efficiency by Processes"
        )
        self.Plots[
            "EfficiencyHistogram_" + self.Feature + "_ByProcess"
        ] = self.MergeEfficiencyHistogram(Title, list(Process.values()))

    def MakeProcessEfficiency(self):
        self.Efficiency = {
            prc: self.EfficiencyLine(
                self.Epoch, self.Efficiency[prc], prc, self.Error[prc]
            )
            for prc in self.Efficiency
        }
        Title = (
            "Reconstruction Efficiency of Model Feature ("
            + self.Feature
            + ") by Processes"
        )
        self.Plots["EfficiencyProcess_" + self.Feature] = self.MergeEfficiencyLines(
            Title, list(self.Efficiency.values())
        )

    def MakeAverageEfficiency(self):
        self.Efficiency = self.EfficiencyLine(
            self.Epoch, self.Efficiency, self.Feature, self.Error
        )
        Title = "Average Reconstruction Efficiency using Model Feature: " + self.Feature
        self.Plots["AverageEfficiency_" + self.Feature] = self.MergeEfficiencyLines(
            Title, [self.Efficiency]
        )

    def MakeOverallParticleEfficiency(self):
        Prediction = self.EfficiencyLine(self.Epoch, self.Prediction, self.Feature, [])
        Title = "Reconstruction Efficiency using Model Feature: " + self.Feature
        self.Plots["OverallEfficiency_" + self.Feature] = self.MergeEfficiencyLines(
            Title, [Prediction]
        )

    def MergeBlockPlots(self):
        self._Color = {model: None for model in self.Plots}
        self.GetConsistentModeColor(self._Color)

        Output = {}
        for model in self.Plots:
            for figs in self.Plots[model]:
                if figs not in Output:
                    Output[figs] = {"Title": self.Plots[model][figs].Title}

                Line = self.Plots[model][figs].Lines
                for l in Line:
                    l.Color = self._Color[model]

                    if l.Title not in Output[figs]:
                        Output[figs][l.Title] = []
                    Output[figs][l.Title].append(l)
                    l.Title = model
        self.Plots = Output
        Out = {}
        for fig in self.Plots:
            feat = fig.split("_")[-1]
            self.Feature = feat
            for f in self.Plots[fig]:
                if f == "Title":
                    continue
                Out[fig + "_" + f] = self.MergeEfficiencyLines(
                    self.Plots[fig]["Title"], self.Plots[fig][f]
                )
        self.Plots = Out


class Plots:
    def __init__(self):
        pass

    def GetConsistentModeColor(self, Color):
        Plt = CombineTLine()
        Line = TLine()
        for i in Color:
            Plt.ApplyRandomColor(Line)
            Color[i] = Line.Color
            Line.Color = None

    def TemplateLine(self, Title, xData, yData, err, outdir):
        Plots = {
            "xTitle": "Epoch",
            "Title": Title,
            "xData": xData,
            "yData": yData,
            "up_yData": err,
            "down_yData": err,
            "yMin": 0,
            "xMax": max(xData) + 1 if len(xData) > 0 else None,
            "xMin": min(xData) - 1 if len(xData) > 0 else None,
            "yMax": max([k + i for k, i in zip(err, yData)]) if len(err) > 0 else None,
            "Style": "ATLAS",
            "OutputDirectory": outdir,
        }
        if len(yData) != 0:
            return TLine(**Plots)
        else:
            return Plots

    def PlotTime(self, figs, metric, outdir):
        Plots = self.TemplateLine(
            metric.replace("_", " "), figs[0].xData, [], [], outdir + "Time"
        )
        Plots["yTitle"] = "Time in Seconds (Lower is Better)"
        Plots["Lines"] = figs
        Plots["Filename"] = metric
        Plots["yMax"] = max([k + i for t in figs for k, i in zip(t.up_yData, t.yData)])
        com = CombineTLine(**Plots)
        com.SaveFigure()

    def PlotAUC(self, figs, metric, outdir):
        Plots = self.TemplateLine(
            metric.replace("_", " "), figs[0].xData, [], [], outdir + "AUC"
        )
        Plots["yTitle"] = "Area under ROC Curve (Higher is Better)"
        Plots["Lines"] = figs
        Plots["Filename"] = metric
        Plots["yMax"] = 1
        com = CombineTLine(**Plots)
        com.SaveFigure()

    def PlotLoss(self, figs, metric, outdir):
        Plots = self.TemplateLine(
            metric.replace("_", " "), figs[0].xData, [], [], outdir + "Loss"
        )
        Plots["yTitle"] = "Loss of Model (a.u) (Lower is Better)"
        Plots["Lines"] = figs
        Plots["Filename"] = metric
        Plots["yMax"] = max([k + i for t in figs for k, i in zip(t.up_yData, t.yData)])
        com = CombineTLine(**Plots)
        com.SaveFigure()

    def PlotAccuracy(self, figs, metric, outdir):
        Plots = self.TemplateLine(
            metric.replace("_", " "), figs[0].xData, [], [], outdir + "Accuracy"
        )
        Plots["yTitle"] = "Loss of Accuracy (%) (Higher is Better)"
        Plots["Lines"] = figs
        Plots["Filename"] = metric
        Plots["yMax"] = 100
        com = CombineTLine(**Plots)
        com.SaveFigure()


class PredictionContainer(Metrics):
    def __init__(self):
        self.Make = None
        self.ProjectName = None
        self.OutputDirectory = "./"

        self.ModelName = None
        self.Epoch = None
        self.EpochContainer = None
        self._MakeDebugPlots = True

        self._MassBlocks = {}
        self._RecoBlocks = {}
        self._RecoEpoch = {}

    def ReconstructionEfficiency(self, inpt, Truth, Pred):
        for f in Pred:
            if f not in self._MassBlocks:
                self._MassBlocks[f] = DataBlock(f)
                self._MassBlocks[f].Epoch = self.Epoch
                self._MassBlocks[f].Process = []

                self._RecoBlocks[f] = DataBlock(f)
                self._RecoBlocks[f].Process = {}

                self._RecoEpoch[f] = DataBlock(f)

            prc = inpt[f]["Prc"]
            eff = inpt[f]["%"]
            if prc not in self._RecoBlocks[f].Process:
                self._RecoBlocks[f].Process[prc] = []

            self._MassBlocks[f].Truth += Truth[f]
            self._MassBlocks[f].Prediction += Pred[f]
            self._MassBlocks[f].Process += [{prc: [Truth[f], Pred[f]]}]

            self._RecoBlocks[f].Process[prc].append(eff)

            self._RecoEpoch[f].Efficiency.append(eff)
            self._RecoEpoch[f].Truth.append(inpt[f]["ntru"])
            self._RecoEpoch[f].Prediction.append(inpt[f]["nrec"])

    def CompileEpoch(self):
        outdir = (
            self.OutputDirectory
            + "/"
            + self.ProjectName
            + "/Summary/SampleModes/"
            + self.Make
            + "/"
            + self.ModelName
        )
        Plots = {}
        for f in self._MassBlocks:
            self._MassBlocks[f].MakeMass()
            self._MassBlocks[f].MakeMassByProcess()
            self._RecoBlocks[f].MakeEfficiencyHistogram

            Plots |= self._MassBlocks[f].Plots
            Plots |= self._RecoBlocks[f].Plots

            self._RecoEpoch[f].Efficiency = self.MakeStatics(
                self._RecoEpoch[f].Efficiency
            )
            self._RecoEpoch[f].Prediction = (
                float(
                    sum(self._RecoEpoch[f].Prediction) / sum(self._RecoEpoch[f].Truth)
                )
                * 100
            )

            self._RecoBlocks[f].Process = {
                prc: self.MakeStatics(self._RecoBlocks[f].Process[prc])
                for prc in self._RecoBlocks[f].Process
            }

        for fig in Plots:
            Plots[fig].Filename = fig
            Plots[fig].OutputDirectory = outdir + "/Epoch-" + str(self.Epoch)
            Plots[fig].SaveFigure()

        self.EpochContainer.OutDir = outdir
        self.EpochContainer.Process(self._MakeDebugPlots)

    def __radd__(self, other):
        if other == 0:
            self._PrcEfficiency = {self.Epoch: self._RecoBlocks}
            self._RecoEpoch = {self.Epoch: self._RecoEpoch}
            return self
        else:
            self.__add__(other)

    def __add__(self, other):
        self._PrcEfficiency[other.Epoch] = other._RecoBlocks
        self._RecoEpoch[other.Epoch] = other._RecoEpoch
        return self

    def CompileMergedEpoch(self):
        PrcEfficiency = {}
        RecoEfficiency = {}
        for epoch in self._PrcEfficiency:
            for feat in self._PrcEfficiency[epoch]:
                if feat not in PrcEfficiency:
                    PrcEfficiency[feat] = DataBlock(feat)
                    PrcEfficiency[feat].Epoch = []
                    PrcEfficiency[feat].Efficiency = {}

                    RecoEfficiency[feat] = DataBlock(feat)
                    RecoEfficiency[feat].Epoch = []
                    RecoEfficiency[feat].Error = []

                prc_dic = self._PrcEfficiency[epoch][feat].Process
                for prc in prc_dic:
                    if prc not in PrcEfficiency[feat].Efficiency:
                        PrcEfficiency[feat].Efficiency[prc] = []
                        PrcEfficiency[feat].Error[prc] = []

                    PrcEfficiency[feat].Efficiency[prc].append(prc_dic[prc][0])
                    PrcEfficiency[feat].Error[prc].append(prc_dic[prc][1])

                RecoEfficiency[feat].Prediction.append(
                    self._RecoEpoch[epoch][feat].Prediction
                )
                RecoEfficiency[feat].Efficiency.append(
                    self._RecoEpoch[epoch][feat].Efficiency[0]
                )
                RecoEfficiency[feat].Error.append(
                    self._RecoEpoch[epoch][feat].Efficiency[1]
                )

                PrcEfficiency[feat].Epoch.append(epoch)
                RecoEfficiency[feat].Epoch.append(epoch)

        self.Plots = {}
        for feat in PrcEfficiency:
            PrcEfficiency[feat].MakeProcessEfficiency()
            RecoEfficiency[feat].MakeAverageEfficiency()
            RecoEfficiency[feat].MakeOverallParticleEfficiency()
            self.Plots |= PrcEfficiency[feat].Plots
            self.Plots |= RecoEfficiency[feat].Plots

        for p in self.Plots:
            fig = self.Plots[p]
            fig.Filename = p
            fig.OutputDirectory = (
                self.OutputDirectory
                + "/"
                + self.ProjectName
                + "/Summary/Efficiency/"
                + self.Make
                + "/"
                + self.ModelName
            )
            fig.SaveFigure()


class ModelComparisonPlots(Plots):
    def __init__(self):
        pass

    def Tables(self, Container, Mode):
        ep = list(Container)[0]
        minimize = ["TotalLoss", "Loss", "EpochTime"]
        minimize = {
            i: 0 for k in minimize for i in Container[ep].MinMetric if i.startswith(k)
        }
        maximize = ["AUC", "Accuracy"]
        maximize = {
            i: 0 for k in maximize for i in Container[ep].MaxMetric if i.startswith(k)
        }
        Names = Container[ep].Names

        Tbl = Tables()
        Tbl.Title = "SUMMARY"
        Tbl.AddColumnTitle("Metrics \ Models")

        for n in Names:
            for k in list(maximize) + list(minimize):
                Tbl.AddValues(k.replace("_", " "), n, 0)

        for ep in Container:
            for m in minimize:
                model = [Names[i] for i in Container[ep].MinMetric[m]]
                for k in model:
                    Tbl.AddValues(m.replace("_", " "), k, 1)

            for m in maximize:
                model = [Names[i] for i in Container[ep].MaxMetric[m]]
                for k in model:
                    Tbl.AddValues(m.replace("_", " "), k, 1)

        Tbl.Compile()
        Tbl.DumpTableToFile(
            self.OutputDirectory
            + "/"
            + self.ProjectName
            + "/Summary/"
            + Mode
            + "/TrainingComparison"
        )
        epochs = list(Container)
        epochs.sort()

        for i in Names:
            Tbl = Tables()
            Tbl.Title = i
            Tbl.Sum = False
            Tbl.MinMax = True
            Tbl.AddColumnTitle("Epoch \ Metric")
            for ep in epochs:
                dic = Container[ep].ModelValues
                for metric in dic:
                    if metric.startswith("NodeTimes"):
                        continue
                    Tbl.AddValues(ep, metric, dic[metric][i])

            Tbl.Compile()
            Tbl.DumpTableToFile(
                self.OutputDirectory
                + "/"
                + self.ProjectName
                + "/Summary/"
                + Mode
                + "/"
                + i
                + "/EpochSummary"
            )

        SummedEpoch = {}
        for i in Names:
            SummedEpoch[i] = sum(self._ModelDirectories[i])
            SummedEpoch[i].Compile(
                self.OutputDirectory
                + "/"
                + self.ProjectName
                + "/Summary/"
                + Mode
                + "/"
                + i
            )

    def TrainingComparison(self, ModelResults, TrainContainer, names):
        for epch in ModelResults[names]:
            if epch.Epoch not in TrainContainer:
                TrainContainer[epch.Epoch] = _Comparison()
            TrainContainer[epch.Epoch].Epoch = epch.Epoch
            TrainContainer[epch.Epoch].ModelStats[names] = epch._Package[epch.Epoch]
            TrainContainer[epch.Epoch].ModelFeatures[names] = epch._Package[
                "OutputNames"
            ]

    def Verdict(self):
        Tbl = Tables()
        Tbl.Title = "Performance of Different Models for the Reconstruction Efficiency of Particles"
        Tbl.AddColumnTitle("Epoch \ Models (Sample)")
        Tbl.Sum = False
        Tbl.MinMax = True
        for i in self._Blocks:
            self._Blocks[i].MergeBlockPlots()
            for k in self._Blocks[i].Plots:
                self._Blocks[i].Plots[k].Filename = k.split("_")[0]
                self._Blocks[i].Plots[k].OutputDirectory = (
                    self.OutputDirectory
                    + "/"
                    + self.ProjectName
                    + "/Summary/Efficiency/"
                    + i
                    + "/"
                    + k.split("_")[-1]
                )
                self._Blocks[i].Plots[k].SaveFigure()

                if k.split("_")[0] != "OverallEfficiency":
                    continue
                Lines = self._Blocks[i].Plots[k].Lines
                for l in Lines:
                    model = l.Title
                    for ep, val in zip(l.xData, l.yData):
                        Tbl.AddValues(ep, model + " (" + i + ")", val)
        Tbl.Compile()
        Tbl.DumpTableToFile(
            self.OutputDirectory
            + "/"
            + self.ProjectName
            + "/Summary/Efficiency/"
            + i
            + "/EfficiencyTable.txt"
        )
