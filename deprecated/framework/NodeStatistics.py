from AnalysisTopGNN.Tools import Tables
from .TemplateHistograms import TH1F, CombineTH1F


class _Container(object):
    def __init__(self):
        self.ROOTNames = {}
        self.Nodes = []
        self._Comp = False
        self._lumi = 0

    def Add(self, prc, nodes, lumi):
        if prc not in self.ROOTNames:
            self.ROOTNames[prc] = []
        self.ROOTNames[prc].append(int(nodes))
        self.Nodes.append(int(nodes))
        self._Comp = True
        self._lumi += float(lumi)

    def Process(self):
        self.lenROOT = {}
        self.lenNodes = {}
        self.lenAllNodes = {}
        if self._Comp == False:
            return
        for i in self.ROOTNames:
            self.lenROOT[i] = len(self.ROOTNames[i])

        for i in self.ROOTNames:
            unique_nodes = set(self.ROOTNames[i])
            self.lenNodes[i] = {}
            for n in unique_nodes:
                self.lenNodes[i][n] = len([k for k in self.ROOTNames[i] if n == k])

        for i in set(self.Nodes):
            self.lenAllNodes[i] = len([k for k in self.Nodes if i == k])


class SampleNode:
    def __init__(self):
        self.SampleNodes = {}
        self.Training = {}
        self.TestSample = {}
        self.OutDir = "./"

    def MakeTable(self, var):
        Tbl = Tables()
        Tbl.AddColumnTitle("Samples \ Nodes")
        for n in var:
            Nodes = var[n]
            for node in Nodes:
                Tbl.AddValues(n, node, Nodes[node])
        return Tbl

    def MakeSummary(self, Sample, Title, out):
        Sample.Process()
        tbl = self.MakeTable(Sample.lenNodes)
        tbl.Title = Title
        tbl.Compile()
        out += tbl.output
        out += [""]
        return (out, tbl)

    def TemplateHistogramSetting(self):
        Plots = {}
        Plots["xTitle"] = "Nodes"
        Plots["yTitle"] = "Entries"
        Plots["Style"] = "ATLAS"
        return Plots

    def MakeHistograms(self, Title, Filename, Sample):
        Plots = self.TemplateHistogramSetting()
        Plots["Title"] = Title
        Plots["Filename"] = Filename
        Plots["OutputDirectory"] = self.OutDir
        Plots["xStep"] = 1
        Plots["xMin"] = 0
        Plots["xBinCentering"] = True
        Plots["ATLASLumi"] = Sample._lumi
        THStck = CombineTH1F(**Plots)

        Plots = self.TemplateHistogramSetting()
        Plots["xData"] = Sample.Nodes
        Plots["Title"] = "All"
        Plots["xBins"] = max(Sample.Nodes)
        T = TH1F(**Plots)
        THStck.Histogram = T

        for prc in Sample.ROOTNames:
            Plots = self.TemplateHistogramSetting()
            Plots["Title"] = prc
            Plots["xData"] = Sample.ROOTNames[prc]
            THStck.Histograms.append(TH1F(**Plots))
        THStck.SaveFigure()

    def AddNodeSample(self, analysis):
        for i in analysis:
            if i.Compiled == False:
                continue
            for tr in i.Trees:
                if tr not in self.SampleNodes:
                    self.SampleNodes[tr] = _Container()
                    self.Training[tr] = _Container()
                    self.TestSample[tr] = _Container()
                prc = analysis.HashToROOT(i.Filename).split("/")[-2]
                nodes = i.Trees[tr].num_nodes
                lumi = i.Trees[tr].Lumi

                self.SampleNodes[tr].Add(prc, nodes, lumi)
                if i.Train == True:
                    self.Training[tr].Add(prc, nodes, lumi)
                if i.Train == False:
                    self.TestSample[tr].Add(prc, nodes, lumi)

    def Process(self):
        for tr in self.SampleNodes:
            out = []

            TitleAll = (
                "All Samples: Node Summary by Process for "
                + tr
                + " tree - Integrated Luminosity "
                + str(self.SampleNodes[tr]._lumi)
            )
            out, tbl = self.MakeSummary(self.SampleNodes[tr], TitleAll, out)

            TitleTraining = (
                "Training Samples: Node Summary by Process for "
                + tr
                + " tree - Integrated Luminosity "
                + str(self.Training[tr]._lumi)
            )
            out, tbl = self.MakeSummary(self.Training[tr], TitleTraining, out)

            TitleTest = (
                "Test Samples: Node Summary by Process for "
                + tr
                + " tree - Integrated Luminosity "
                + str(self.TestSample[tr]._lumi)
            )
            out, tbl = self.MakeSummary(self.TestSample[tr], TitleTest, out)

            tbl.output = out
            tbl.DumpTableToFile(self.OutDir + "/SampleNodeStatistics_" + tr)

            self.MakeHistograms(
                "Complete Sample Node Distribution \n Superimposed by Process ("
                + tr
                + ")",
                "AllSampleNodeDistribution_" + tr,
                self.SampleNodes[tr],
            )

            self.MakeHistograms(
                "Training Sample Node Distribution \n Superimposed by Process ("
                + tr
                + ")",
                "TrainingSampleNodeDistribution_" + tr,
                self.Training[tr],
            )

            self.MakeHistograms(
                "Test Sample Node Distribution \n Superimposed by Process (" + tr + ")",
                "TestSampleNodeDistribution_" + tr,
                self.TestSample[tr],
            )
