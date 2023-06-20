from AnalysisTopGNN.Model import Model
from AnalysisTopGNN.Tools import Tools, RandomSamplers, Threading
from AnalysisTopGNN.Plotting.ModelComparisonPlots import (
    _Comparison,
    DataBlock,
    ModelComparisonPlots,
    PredictionContainer,
)
from AnalysisTopGNN.Plotting.NodeStatistics import SampleNode
from AnalysisTopGNN.Statistics import Reconstruction
from AnalysisTopGNN.IO import UnpickleObject, PickleObject
from AnalysisTopGNN.Samples import Epoch, SampleTracer
from .Settings import Settings
from AnalysisTopGNN.Notification import Evaluator_


class ModelEvaluator(
    Settings,
    SampleTracer,
    Evaluator_,
    Tools,
    ModelComparisonPlots,
    SampleNode,
    RandomSamplers,
):
    def __init__(self):
        self.Caller = "MODELEVALUATOR"
        Settings.__init__(self)
        SampleTracer.__init__(self)

        self._Container = {}
        self._Blocks = {}

    def AddAnalysis(self, analysis):
        self += analysis

    def AddModel(self, Directory, ModelInstance=None, BatchSize=None):
        Directory = self.AddTrailing(Directory, "/")
        Name = Directory.split("/")[-2]

        if Name in self._ModelDirectories:
            return

        self._ModelDirectories[Name] = [
            Directory + i for i in self.ls(Directory) if "Epoch-" in i
        ]
        self._ModelSaves[Name] = {"ModelInstance": ModelInstance}
        self._ModelSaves[Name] |= {"BatchSize": BatchSize}

    def __CompareTraining(self, Mode):
        Names = list(self._ModelDirectories)
        outdir = (
            self.OutputDirectory + "/" + self.ProjectName + "/Summary/" + Mode + "/"
        )
        epochs = list(self._TrainingContainer)
        epochs.sort()

        self.Colors = {m: None for m in Names}
        self.GetConsistentModeColor(self.Colors)
        self.Tables(self._TrainingContainer, Mode)

        for met in list(self._TrainingContainer[epochs[0]].ModelValues):
            Plots = []
            for m in Names:
                data = [
                    self._TrainingContainer[ep].ModelValues[met][m] for ep in epochs
                ]
                Err = [
                    self._TrainingContainer[ep].ModelValuesError[met][m]
                    for ep in epochs
                ]
                Lines = self.TemplateLine(m, epochs, data, Err, outdir)
                Lines.Color = self.Colors[m]
                Lines.Compile()
                Plots.append(Lines)

            plt = (
                self.PlotTime(Plots, met, outdir)
                if met.startswith("EpochTime")
                else None
            )
            plt = (
                self.PlotTime(Plots, met, outdir) if met.startswith("FoldTime") else plt
            )
            plt = (
                self.PlotTime(Plots, met, outdir)
                if met.startswith("NodeTimes")
                else plt
            )
            plt = self.PlotAUC(Plots, met, outdir) if met.startswith("AUC") else plt
            plt = self.PlotLoss(Plots, met, outdir) if met.startswith("Loss_") else plt
            plt = (
                self.PlotLoss(Plots, met, outdir)
                if met.startswith("TotalLoss_")
                else plt
            )
            plt = (
                self.PlotAccuracy(Plots, met, outdir)
                if met.startswith("Accuracy")
                else plt
            )

    def __ShowSampleDistribution(self):
        self.OutDir = self.OutputDirectory + "/" + self.ProjectName + "/NodeStatistics/"
        self.AddNodeSample(self)
        self.Process()

    def __ParticleReconstruction(self, model, sample, smpleprc, container):
        reco = Reconstruction(model)
        idx = 0
        index = 0
        for data in sample:
            prc = smpleprc[index]
            data.to(device=self.Device)

            reco.TruthMode = False
            pred = reco(data)

            reco.TruthMode = True
            truth = reco(data)

            for i in range(idx, idx + len(pred)):
                p = self.HashToROOT(prc[i - idx]).split("/")[-2]
                rec = {
                    o: reco.ParticleEfficiency(pred[i - idx][o], truth[i - idx][o], p)
                    for o in pred[i - idx]
                }
                container.ReconstructionEfficiency(rec, truth[i - idx], pred[i - idx])

            idx += len(pred)
            index += 1

    def __EvaluateSample(self, model, smple, Ep):
        for i in smple:
            Ep.EpochContainer.StartTimer()
            pred, truth, loss_acc = model.Prediction(i)
            Ep.EpochContainer.StopTimer()
            Ep.EpochContainer.Collect(pred, truth, loss_acc, Ep.Make)

    def __EvaluateSampleType(self, Type):
        for name in self._ModelSaves:
            if self._ModelSaves[name]["ModelInstance"] == None:
                continue
            BatchSize = (
                1
                if self._ModelSaves[name]["BatchSize"] == None
                else self._ModelSaves[name]["BatchSize"]
            )
            smple, prcsmple = self.MakeSample(
                {
                    i.Filename: i.Trees[self.Tree]
                    for i in self
                    if i.Train == Type or Type == None
                },
                True,
                BatchSize,
            )

            model = self._ModelSaves[name]["ModelInstance"]
            epochsDict = self._ModelSaves[name]["TorchSave"]
            epochs = list(epochsDict)
            epochs.sort()

            make = "Train" if Type == True else ""
            make = "Test" if Type == False else make
            make = "All" if Type == None else make

            if make not in self._Container:
                self._Container[make] = {}
            if name not in self._Container[make]:
                self._Container[make][name] = []

            self.NewModel(name)
            for ep in epochs:
                cacheDir = (
                    self.OutputDirectory
                    + "/"
                    + self.ProjectName
                    + "/TrainedModels/"
                    + name
                    + "/Epoch-"
                    + str(ep)
                    + "/"
                    + make
                    + "Sample"
                )

                self.MakingCurrentJob(make, name, ep)
                if self.IsFile(cacheDir + ".pkl"):
                    p = UnpickleObject(cacheDir)
                    self._Container[make][name].append(p)
                    continue

                mod = Model(model)
                mod.Device = self.Device
                mod.LoadModel(self.abs(epochsDict[ep]))

                p = PredictionContainer()
                p.OutputDirectory = self.OutputDirectory
                p.ModelName = name
                p.Epoch = ep
                p.Make = make
                p._MakeDebugPlots = self.PlotEpochDebug
                p.EpochContainer = Epoch(ep)
                p.EpochContainer.ModelOutputs += list(mod.GetModelOutputs())
                p.EpochContainer.MakeDictionary(make)
                p.EpochContainer.Fold = 1
                p.EpochContainer.FoldTime[1] = 0
                p.ProjectName = self.ProjectName

                self._Container[make][name].append(p)

                self.__ParticleReconstruction(mod, smple, prcsmple, p)
                self.__EvaluateSample(mod, smple, p)

                PickleObject(p, cacheDir)

    def __ProcessContainer(self, Container, Name):
        def function(inpt):
            for i in inpt:
                i[0].CompileEpoch()
            return inpt

        lst = [
            [i, mod + "_" + str(i.Epoch)] for mod in Container for i in Container[mod]
        ]
        for i in function(lst):
            mod = i[1].split("_")
            Container["_".join(mod[:-1])][int(mod[-1])] = i[0]

        self._TrainingContainer = {}
        ModelContainer = {}
        BlockContainer = {}
        self._Blocks[Name] = DataBlock("Models")
        for model in Container:
            epochs = Container[model]
            ModelContainer[model] = [ep.EpochContainer for ep in epochs]
            self.TrainingComparison(ModelContainer, self._TrainingContainer, model)
            BlockContainer[model] = sum(epochs)
            BlockContainer[model].CompileMergedEpoch()
            BlockContainer[model] = BlockContainer[model].Plots
        self._Blocks[Name].Plots = BlockContainer
        for ep in self._TrainingContainer:
            self._TrainingContainer[ep].Process()
        self.__CompareTraining(Name)

    def Compile(self):
        self.StartModelEvaluator()

        self._TrainingContainer = {}
        for names in self._ModelDirectories:
            Dict = {
                int(i.split("-")[-1]): i + "/TorchSave.pth"
                for i in self._ModelDirectories[names]
                if self.IsFile(i + "/TorchSave.pth")
            }
            self._ModelSaves[names]["TorchSave"] = Dict
            models = [
                UnpickleObject(i + "/Stats.pkl")
                for i in self._ModelDirectories[names]
                if self.IsFile(i + "/Stats.pkl")
            ]
            self._ModelDirectories[names] = models

            if self.PlotTrainingStatistics:
                self.TrainingComparison(
                    self._ModelDirectories, self._TrainingContainer, names
                )

        if self.PlotTrainingStatistics:

            def function(inpt):
                for i in inpt:
                    i[0].Process()
                return inpt

            lst = [[self._TrainingContainer[i], i] for i in self._TrainingContainer]
            th = Threading(lst, function, self.Threads, 2)
            th.VerboseLevel = self.VerboseLevel
            th.Start()
            for i in th._lists:
                self._TrainingContainer[i[1]] = i[0]

            self.MakingPlots("--- Processing the Statistics of Trained Models ---")
            self.__CompareTraining("Training")

        if self.PlotNodeStatistics:
            self.MakingPlots("--- Making Node Sample Distribution ---")
            self.__ShowSampleDistribution()

        if self.PlotTrainSample:
            self.MakingPlots("--- Processing the Training Sample ---")
            self.__EvaluateSampleType(True)
            self.__ProcessContainer(self._Container["Train"], "TrainingSample")

        if self.PlotTestSample:
            self.MakingPlots("--- Processing the Test (Withheld) Sample ---")
            self.__EvaluateSampleType(False)
            self.__ProcessContainer(self._Container["Test"], "TestSample")

        if self.PlotEntireSample:
            self.MakingPlots("--- Processing the Entire Sample ---")
            self.__EvaluateSampleType(None)
            self.__ProcessContainer(self._Container["All"], "CompleteSample")

        if len(self._Container) > 0 and self.PlotModelComparison:
            self.Verdict()
