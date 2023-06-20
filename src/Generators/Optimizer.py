from AnalysisG.Model.Optimizers import OptimizerWrapper
from AnalysisG.Notification import _Optimizer
from AnalysisG.Evaluation.Epoch import Epoch
from .SampleGenerator import RandomSamplers
from AnalysisG.Tools import Code, Threading
from AnalysisG.Tracer import SampleTracer
from AnalysisG.Model import ModelWrapper
from AnalysisG.Settings import Settings
from torch_geometric.data import Batch
from .Interfaces import _Interface
from multiprocessing import Process
import torch


class Optimizer(_Optimizer, _Interface, SampleTracer, RandomSamplers):
    def __init__(self, inpt):
        self.Caller = "OPTIMIZER"
        Settings.__init__(self)
        SampleTracer.__init__(self)
        _Optimizer.__init__(self)
        if issubclass(type(inpt), SampleTracer):
            self += inpt
        if issubclass(type(inpt), Settings):
            self.ImportSettings(inpt)

    @property
    def GetCode(self):
        if "Model" in self._Code:
            return self._Code["Model"]
        self._Code["Model"] = Code(self.Model)
        return self.GetCode

    @property
    def Launch(self):
        self.DataCache = True
        if self._NoModel:
            return False
        if self._NoSampleGraph:
            return False
        self._outDir = self.OutputDirectory + "/Training"
        self.Model = ModelWrapper(self.GetCode.clone)
        self.Model.OutputDirectory = self._outDir
        self.Model.RunName = self.RunName

        for smpl in self:
            break
        smpl = self.BatchTheseHashes([smpl.hash], "test", self.Device)
        if not self.Model.SampleCompatibility(smpl):
            return self._notcompatible

        self._op = OptimizerWrapper()
        self._op.ImportSettings(self)
        self._op._mod = self.Model._Model
        if self._setoptimizer:
            return
        self._setscheduler
        self._searchdatasplits
        self._op = None
        self.Model = None

        self._kModels = {}
        self._kOp = {}
        self._DataLoader = {}
        self._nsamples = {}
        if self.kFold is None:
            self.kFold = {"train": {"all": self.GetDataCacheHashes}}
        for k in self.kFold:
            self._kModels[k] = ModelWrapper(self._Code["Model"].clone)
            self._kModels[k].OutputDirectory = self._outDir
            self._kModels[k].RunName = self.RunName
            self._kModels[k].SampleCompatibility(smpl)
            self._kModels[k].device = self.Device

            self._kOp[k] = OptimizerWrapper()
            self._kOp[k].ImportSettings(self)
            self._kOp[k].OutputDirectory = self._outDir
            self._kOp[k]._mod = self._kModels[k]._Model
            self._kOp[k].SetOptimizer
            self._kOp[k].SetScheduler
            self._nsamples[k] = {}
            self._DataLoader[k] = {}

        if not self._searchtraining:
            return
        self._threads = []
        self.__train__
        self.__dump_plots__()

    @property
    def __train__(self):
        def ApplyMode(k_):
            try:
                mode = next(self._it)
            except:
                return False
            if mode not in self._DataLoader[k_]:
                self.ForceTheseHashes(self.kFold[k_][mode])
                self._DataLoader[k_][mode] = self.MakeDataLoader(
                    self, self.SortByNodes, self.BatchSize
                )
                self._nsamples[k_][mode] = len(self._DataLoader[k_][mode])
            self._dl = self._DataLoader[k_][mode]
            self._len = self._nsamples[k_][mode]
            self.mode = mode
            return True

        def Train(_train):
            self.Model.train = _train
            self._ep.train = _train
            self._op.train = _train

        for ep in range(self.Epoch, self.Epochs):
            for k in self._kModels:
                _ep = str(ep + 1) + "/" + str(k)
                if self.ContinueTraining:
                    mod = self._kModels[k].Epoch
                    if mod is None:
                        pass
                    elif mod == "":
                        pass
                    elif mod.endswith(_ep):
                        continue
                    elif int(mod.split("/")[0]) > ep + 1:
                        continue

                self._it = iter(self.kFold[k])

                self.mkdir(self._outDir + "/" + self.RunName + "/" + _ep)
                self._op = self._kOp[k]
                self._op.Epoch = _ep

                self.Model = self._kModels[k]
                self.Model.Epoch = _ep

                self._ep = Epoch()
                self._ep.o_model = self.Model.o_mapping
                self._ep.i_model = self.Model.i_mapping
                self._ep.RunName = self.RunName
                self._ep.OutputDirectory = self._outDir
                self._ep.init
                self._ep.Epoch = _ep

                ApplyMode(k)
                Train(True)
                self.__this_epoch__

                if ApplyMode(k):
                    Train(False)
                else:
                    self._len = 0
                self.__this_epoch__

                self._op.stepsc
                self._op.dump
                self.Model.dump
                if not self.DebugMode:
                    self.__dump_plots__(self._ep)

    @property
    def __this_epoch__(self):
        if self._len == 0:
            return
        kF = self._ep.Epoch.split("/")[1]
        if not self.DebugMode:
            title = "(Training) " if self.Model.train else "(Validation) "
            title += "Epoch " + str(self._ep.Epoch).split("/")[0] + "/"
            title += str(self.Epochs) + " k-Fold: " + kF
            _, bar = self._MakeBar(self._len, title, True)

        kF = "-" + str(kF) + "-" + self.mode
        for smpl, index in zip(self._dl, range(len(self._dl))):
            smpl = self.BatchTheseHashes(smpl, str(index) + kF, self.Device)
            self._op.zero
            self._ep.start
            pred, loss = self.Model(smpl)
            self._ep.end
            self.Model.backward
            self._op.step

            if not self.DebugMode:
                bar.update(1)
            if not self.DebugMode:
                self._ep.Collect(smpl, pred, loss)
            if self.DebugMode:
                self._showloss
            if self.Device != "cpu" and self.GPUMemory > 80:
                self.FlushBatchCache
            if not self.EnableReconstruction:
                continue
            self.Model.TruthMode = True
            truth = self.Model.mass

            self.Model.TruthMode = False
            pred = self.Model.mass

            eff = self.Model.ParticleEfficiency
            dc = self._ep._train if self._ep.train else self._ep._val
            for b in range(len(truth)):
                for f in truth[b]:
                    dc[f]["mass_t"] += truth[b][f]
                for f in pred[b]:
                    dc[f]["mass"] += pred[b][f]
                for f in eff[b]:
                    dc[f]["nrec"] += [eff[b][f]["nrec"]]
                for f in eff[b]:
                    dc[f]["ntru"] += [eff[b][f]["ntru"]]

    def __dump_plots__(self, inpt=None):
        if inpt is None:
            while len(self._threads) > 0:
                self._threads = [t for t in self._threads if t.is_alive()]
            return

        while len(self._threads) > self.Threads:
            self._threads = [t for t in self._threads if t.is_alive()]

        def func(inpt):
            inpt.dump

        th = Process(target=func, args=(inpt,))
        th.start()
        self._threads.append(th)
