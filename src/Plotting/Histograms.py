from .BaseFunctions import BaseFunctions
from AnalysisG.Settings import Settings
import numpy as np
import mplhep as hep
import random


class Functions(BaseFunctions, Settings):
    def __init__(self):
        self.Caller = "PLOTTING"
        BaseFunctions.__init__(self)
        Settings.__init__(self)
        self.ResetPLT()

    def DefineAxisBins(self, Dim):
        self.Set(Dim + "Bins", None)
        self.Set(Dim + "BinCentering", False)
        self.Set(Dim + "Range", None)
        self.Set(Dim + "Step", None)

    def ApplyRandomTexture(self):
        if self.Texture == True:
            ptr = ["/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]
            random.shuffle(ptr)
            return ptr[0]
        elif self.Texture != False:
            return self.Texture
        return

    def GetBinWidth(self, Dims):
        if self.Get(Dims + "Min") == None or self.Get(Dims + "Max") == None:
            return False
        d_max, d_min, d_bin = (
            self.Get(Dims + "Max"),
            self.Get(Dims + "Min"),
            self.Get(Dims + "Bins"),
        )
        return (
            float((d_max - d_min) / d_bin)
            if self.Get(Dims + "Step") == None
            else self.Get(Dims + "Step")
        )

    def CenteringBins(self, Dims):
        wb = self.GetBinWidth(Dims)
        self.Set(
            Dims + "Range",
            (self.Get(Dims + "Min") - wb * 0.5, self.Get(Dims + "Max") - wb * 0.5),
        )

    def DefineRange(self, Dims):
        self.DefineCommonRange(Dims)

        trig = False
        if self.Get(Dims + "Bins") != None:
            trig = True
        if (
            isinstance(self.Get(Dims + "TickLabels"), list)
            and len(self.Get(Dims + "TickLabels")) != 0
        ):
            self.Set(Dims + "Bins", len(self.Get(Dims + "TickLabels")))
            self.Set(Dims + "TickLabels", self.Get(Dims + "TickLabels") + [""])
            self.Set(Dims + "Max", self.Get(Dims + "Bins"))
            self.Set(Dims + "Min", 0)

        if self.Get(Dims + "Weights") == None:
            pass
        elif len(self.Get(Dims + "Data")) == 0 and len(self.Get(Dims + "Weights")) != 0:
            self.Set(Dims + "Bins", len(self.Get(Dims + "Weights")))
            self.Set(Dims + "Data", [i for i in range(len(self.Get(Dims + "Weights")))])
            self.DefineCommonRange(Dims)
            trig = False

        if self.Get(Dims + "Bins") == None:
            p = set(self.Get(Dims + "Data"))
            dif = (max(p) if len(p) != 0 else 1) - (min(p) if len(p) != 0 else 0) + 1
            self.Set(Dims + "Bins", int(dif))
            trig = True

        if self.Get(Dims + "Step") != None and trig == False:
            self.Set(
                Dims + "Bins",
                1
                + int(
                    (self.Get(Dims + "Max") - self.Get(Dims + "Min"))
                    / self.Get(Dims + "Step")
                ),
            )
            self.Set(
                Dims + "Max",
                self.Get(Dims + "Min")
                + self.Get(Dims + "Step") * (self.Get(Dims + "Bins")),
            )

        if self.Get(Dims + "Range") == None:
            self.Set(Dims + "Range", (self.Get(Dims + "Min"), self.Get(Dims + "Max")))

        if self.Get(Dims + "BinCentering"):
            self.CenteringBins(Dims)

        if self.Get(Dims + "Max") != None and self.IncludeOverflow:
            max_ = self.Get(Dims + "Max")
            data = self.Get(Dims + "Data")
            data = [i if i < max_ else max_ for i in data]
            self.Set(Dims + "Data", data)


class TH1F(Functions):
    def __init__(self, **kargs):
        Functions.__init__(self)
        self.Caller = "TH1F"

        self.DefineAxisData("x")
        self.DefineAxisBins("x")

        self.DefineAxisData("y")
        self.DefineAxisBins("y")

        self.ApplyInput(kargs)
        self.Caller = "TH1F"

    def ApplyFormat(self):
        obj, err, legen = hep.histplot(
            self.NPHisto,
            density=self.Normalize,
            label=self.Title,
            binticks=True,
            linewidth=self.LineWidth,
            alpha=self.Alpha,
            edgecolor=self.Color,
            color=self.Color,
            histtype=self.FillHist,
            hatch=self.ApplyRandomTexture(),
        )[0]

    def Compile(self, Reset=True):
        if Reset:
            self.ResetPLT()
            self.DefineStyle()
            self.ApplyToPLT()

        if len(self.xData) == 0 and self.xWeights == None:
            self.Warning("EMPTY DATA.")
        elif len(self.xData) == 0 and len(self.xWeights) == 0:
            self.Warning("EMPTY DATA.")

        self.DefineRange("x")
        self.NPHisto = np.histogram(
            self.xData, bins=self.xBins, range=self.xRange, weights=self.xWeights
        )
        self.ApplyFormat()

        if self.xBinCentering:
            self.Axis.set_xticks(self.xData)
        if self.xStep != None:
            self.Axis.set_xticks(
                [self.xMin + self.xStep * i for i in range(self.xBins)]
            )
        if isinstance(self.xTickLabels, list):
            self.Axis.set_xticklabels(self.xTickLabels)


class TH2F(Functions):
    def __init__(self, **kargs):
        Functions.__init__(self)
        self.Caller = "TH2F"

        self.DefineAxisData("x")
        self.DefineAxisBins("x")

        self.DefineAxisData("y")
        self.DefineAxisBins("y")

        self.DefineAxisData("z")
        self.DefineAxisBins("z")

        self.ApplyInput(kargs)

    def ApplyFormat(self):
        H, yedges, xedges = hep.hist2dplot(self.NPHisto)

    def Compile(self):
        self.ResetPLT()
        self.DefineStyle()
        self.ApplyToPLT()

        self.DefineRange("x")
        self.DefineRange("y")
        self.NPHisto = np.histogram2d(
            self.xData,
            self.yData,
            bins=[self.xBins, self.yBins],
            range=[[self.xMin, self.xMax], [self.yMin, self.yMax]],
        )
        self.ApplyFormat()

        if self.xStep != None:
            self.Axis.set_xticks(
                [
                    self.xMin + self.xStep * i
                    for i in range(int((self.xMax - self.xMin) / self.xStep) + 1)
                ]
            )
        if isinstance(self.xTickLabels, list):
            self.Axis.set_xticklabels(self.xTickLabels)
        if self.yStep != None:
            self.Axis.set_yticks(
                [
                    self.yMin + self.yStep * i
                    for i in range(int((self.yMax - self.yMin) / self.yStep) + 1)
                ]
            )
        if isinstance(self.yTickLabels, list):
            self.Axis.set_yticks(
                [
                    i + 0.5 if self.yBinCentering else i
                    for i in range(len(self.yTickLabels))
                ]
            )
            self.Axis.set_yticklabels(self.yTickLabels)


class CombineTH1F(Functions):
    def __init__(self, **kargs):
        Functions.__init__(self)

        self.DefineAxisData("x")
        self.DefineAxisBins("x")

        self.DefineAxisData("y")
        self.DefineAxisBins("y")

        self.Histograms = []
        self.Colors = []

        self.Histogram = None
        self.Stack = False

        self.Caller = "Combine-TH1F"
        self.ApplyInput(kargs)

    def ConsistencyCheck(self):
        H = [self.Histogram] if self.Histogram != None else []
        H += self.Histograms
        for i in H:
            self.xData += i.xData

        self.DefineRange("x")

        reorder = {}
        for i in range(len(self.Histograms)):
            if len(self.Histograms[i].xData) not in reorder:
                reorder[len(self.Histograms[i].xData)] = []
            reorder[len(self.Histograms[i].xData)].append(i)

        reorg = sorted(reorder)
        reorg.reverse()
        self.Histograms = [self.Histograms[k] for i in reorg for k in reorder[i]]

        bins = set([i.xBins for i in self.Histograms if i.xBins != None])
        # if self.xBinCentering and len(bins) == 0: self.xBins -= 1
        bins = self.xBins if len(bins) == 0 else max(bins)
        for i in self.Histograms:
            i.xBins = bins
            i.xMin = self.xMin
            i.xMax = self.xMax
            i.xRange = self.xRange
            i.IncludeOverflow = self.IncludeOverflow
            i.xBinCentering = self.xBinCentering
            self.ApplyRandomColor(i)
            i.Compile()

    def Compile(self):
        self.ConsistencyCheck()

        self.ResetPLT()
        self.DefineStyle()
        self.ApplyToPLT()

        Labels, Numpies = [], []
        Sum = 1
        if self.Normalize == "%" and self.Histogram != None:
            Sum = self.Histogram.NPHisto[0].sum() * 0.01
            self.Normalize = False
        elif self.Normalize and self.Histogram != None:
            Sum = self.Histogram.NPHisto[0].sum()
        elif self.Normalize == True:
            Sum = sum([i.NPHisto[0].sum() for i in self.Histograms]) / len(
                self.Histograms
            )
        elif self.Normalize == "%" and self.Histogram == None:
            Sum = (
                sum([i.NPHisto[0].sum() for i in self.Histograms])
                / len(self.Histograms)
                * 0.01
            )

        if self.Histogram != None:
            try:
                self.Histogram.NPHisto
            except AttributeError:
                self.Histogram.Compile()
            self.Histogram.NPHisto = (
                self.Histogram.NPHisto[0] / Sum,
                self.Histogram.NPHisto[1],
            )
            self.Histogram.ApplyFormat()
            Labels.append(self.Histogram.Title)

        for i in self.Histograms:
            Labels.append(i.Title)
            i.NPHisto = (i.NPHisto[0] / Sum, i.NPHisto[1])
            Numpies.append(i.NPHisto)
            if self.Stack:
                continue
            i.ApplyFormat()

        if self.Stack:
            hep.histplot(
                Numpies,
                density=self.Normalize if self.Normalize == True else False,
                histtype=self.FillHist,
                alpha=self.Alpha,
                stack=self.Stack,
                label=Labels,
                binticks=True,
            )

        self.PLT.legend()
        if self.xMin == self.xMax:
            self.xStep = 0.1
            self.xMax = self.xBins / self.xStep
        if self.Logarithmic:
            self.PLT.yscale("log")
        if self.xBinCentering:
            self.Axis.set_xticks(self.xData)
        if self.xStep != None:
            self.Axis.set_xticks(
                [self.xMin + self.xStep * i for i in range(self.xBins)]
            )
        if isinstance(self.xTickLabels, list):
            self.Axis.set_xticks(self.xData)
            self.Axis.set_xticklabels(self.xTickLabels)

        self.PLT.xlim(self.xMin, self.xMax)
        self.PLT.ylim(self.yMin, self.yMax)


class TH1FStack(CombineTH1F):
    def __init__(self, **kargs):
        self.Histogram = None
        self.Data = {}
        CombineTH1F.__init__(self, **kargs)

    def __Recursive(self, inpt, search):
        if isinstance(inpt, dict) == False:
            return inpt
        if search in inpt:
            if isinstance(inpt[search], list):
                return inpt[search]
            out = []
            for k in inpt[search]:
                out += [k] * inpt[search][k]
            return out
        return [l for i in inpt for l in self.__Recursive(inpt[i], search)]

    def __Organize(self):
        Hists = {}
        try:
            Hists |= {key: None for key in self.Histograms}
        except TypeError:
            Hists = self.Histograms
        if isinstance(self.Histogram, str):
            Hists |= {self.Histogram: None}
        elif isinstance(self.Histogram, dict):
            self.Histogram = TH1F(**self.Histogram)

        self.Histograms = {}
        for i in Hists:
            if isinstance(i, str):
                params = {"xData": self.__Recursive(self.Data, i), "Title": i}
            else:
                params = i
                i = params["Title"]
            self.Histograms[i] = params

    def Precompiler(self):
        self.__Organize()
        hists = []
        for i in self.Histograms:
            if self.Histogram == i:
                self.Histogram = TH1F(**self.Histograms[i])
            else:
                hists.append(TH1F(**self.Histograms[i]))
        self.Histograms = hists
