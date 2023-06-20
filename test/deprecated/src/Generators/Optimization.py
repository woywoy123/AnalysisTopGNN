from AnalysisTopGNN.Tools import Tools, RandomSamplers
from AnalysisTopGNN.Samples import SampleTracer, Epoch
from AnalysisTopGNN.Model import Model, Optimizer, Scheduler
from AnalysisTopGNN.IO import PickleObject
from .Settings import Settings

from AnalysisTopGNN.Notification import Optimization_


class Optimization(Optimization_, Settings, SampleTracer, Tools, RandomSamplers):
    def __init__(self):
        self.Caller = "OPTIMIZATION"
        Settings.__init__(self)
        SampleTracer.__init__(self)
        self._Samples = {}

    def __MakeSample(self):
        for smpl in self:
            key = "All"
            if self.SplitSampleByNode:
                key = smpl.Trees[self.Tree].num_nodes.item()

            if key not in self._Samples:
                self._Samples[key] = []
            smpl.Trees[self.Tree].to(self.Device, non_blocking=True)

            self._Samples[key].append(smpl.Trees[self.Tree])

    def AddAnalysis(self, analysis):
        self += analysis

    def kFoldTraining(self, sample):
        folds = self.MakekFolds(sample, self.kFolds, self.BatchSize)
        if folds == None:
            return

        for f in folds:
            train = folds[f][0]
            validation = folds[f][1]

            self.StartKfoldInfo(train, validation, f, len(folds))

            self.Model.train()
            self._EpochObj.Fold = f

            if f not in self._EpochObj.FoldTime:
                self._EpochObj.FoldTime[f] = 0

            self.Model.train()
            for i in train:
                self._EpochObj.StartTimer()
                pred, truth, loss_acc = self.Model.Prediction(i)
                self._EpochObj.StopTimer()
                self._EpochObj.Collect(pred, truth, loss_acc, "Train")
                loss = self._EpochObj.TotalLoss

                self.TrainingInfo(
                    len(train), self._EpochObj, pred, truth, loss_acc, self.DebugMode
                )

                self.Optimizer(step=False)
                loss.backward()
                self.Optimizer(step=True)

            self.Model.eval()
            for i in validation:
                self._EpochObj.StartTimer()
                pred, truth, loss_acc = self.Model.Prediction(i)
                self._EpochObj.StopTimer()
                self._EpochObj.Collect(pred, truth, loss_acc, "Validation")

    def Train(self):
        for epoch in range(self.Epochs):
            self.ShowEpoch(epoch, self.Epochs)
            outputDir = (
                self.OutputDirectory
                + "/"
                + self.ProjectName
                + "/TrainedModels/"
                + self.RunName
                + "/Epoch-"
                + str(epoch)
            )

            if self.IsFile(outputDir + "/TorchSave.pth") and self.ContinueTraining:
                self.Optimizer.LoadState(outputDir)
                self.Model.LoadModel(outputDir + "/TorchSave.pth")
                continue
            else:
                self.ContinueTraining = False

            self._EpochObj = Epoch(epoch)
            self._EpochObj.ModelOutputs += list(self.Model.GetModelOutputs())
            self._EpochObj.MakeDictionary("Train")
            self._EpochObj.MakeDictionary("Validation")
            self._EpochObj.OutDir = (
                self.OutputDirectory
                + "/"
                + self.ProjectName
                + "/TrainedModels/"
                + self.RunName
            )

            for nodes in self._Samples:
                self.TrainingNodes(nodes)
                self.kFoldTraining(self._Samples[nodes])

            self._EpochObj.Process()

            self.Optimizer.DumpState(outputDir)
            self.Model.DumpModel(outputDir)

            PickleObject(self._EpochObj, outputDir + "/Stats")

            if self.Scheduler != None:
                self.Scheduler()

    def Launch(self):
        self.Model = self.CopyInstance(self.Model)
        if self._dump:
            return

        self.__MakeSample()
        self.CheckGivenSample(self._Samples)

        sample = list(self._Samples.values())[0][-1]
        optim = list(self.Optimizer)[0]
        self.Optimizer = Optimizer(self.Model, optim, self.Optimizer[optim])

        if self.Scheduler != None:
            scheduler = list(self.Scheduler)[0]
            self.Scheduler = Scheduler(
                self.Optimizer.optimizer, scheduler, self.Scheduler[scheduler]
            )

        self.Model = Model(self.Model)
        self.Model.Device = self.Device
        train, pred = self.Model.SampleCompatibility(sample)

        self.Train()
