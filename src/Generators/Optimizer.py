from AnalysisG.Generators.SampleGenerator import RandomSamplers
from AnalysisG._cmodules.cWrapping import OptimizerWrapper
from AnalysisG._cmodules.cOptimizer import cOptimizer
from AnalysisG.Notification import _Optimizer
from .Interfaces import _Interface
from AnalysisG.Model import Model

class Optimizer(_Optimizer, _Interface, RandomSamplers):

    def __init__(self, inpt = None):
        RandomSamplers.__init__(self)
        self.Caller = "OPTIMIZER"
        _Optimizer.__init__(self)
        self._kOps = {}
        self._kModels = {}
        self._cmod = cOptimizer()
        self.triggered = False
        if inpt is None: return
        if not self.is_self(inpt): return
        else: self += inpt

    def __searchsplits__(self, sampletracer):
        sets = self.WorkingPath + "Training/DataSets/"
        sets += self.TrainingName
        if not self._cmod.GetHDF5Hashes(sets):
            sampletracer.GetAll = True
            self._cmod.UseAllHashes([i.hash for i in sampletracer.makelist()])
        self._searchdatasplits(sets)

    def __initialize__(self):
        if self._nomodel(): return False
        if len(self._cmod.kFolds): pass
        else: self._cmod.UseTheseFolds([1])

        k = next(iter(self._cmod.kFolds))
        graphs = next(iter(self._cmod.FetchTraining(k, self.BatchSize)))
        for k in self._cmod.kFolds:
            if len(graphs): pass
            else: return not self._nographs()

            self._kModels[k] = Model(self.Model)
            self._kModels[k].Path = self.WorkingPath + "machine-learning/"
            self._kModels[k].RunName = self.RunName
            self._kModels[k].KFold = k
            self._kModels[k].KinematicMap = self.KinematicMap

            if not len(self.ModelParams): pass
            else: self._kModels[k].__params__ = self.ModelParams

            self._kModels[k].device = self.Device
            if self._kModels[k].SampleCompatibility(graphs): pass
            else: return self._notcompatible()

            self._kOps[k] = OptimizerWrapper()
            self._kOps[k].Path = self.WorkingPath + "machine-learning/"
            self._kOps[k].RunName = self.RunName
            self._kOps[k].KFold = k

            self._kOps[k].Optimizer = self.Optimizer
            self._kOps[k].OptimizerParams = self.OptimizerParams

            self._kOps[k].Scheduler = self.Scheduler
            self._kOps[k].SchedulerParams = self.SchedulerParams
            self._kOps[k].model = self._kModels[k].model

            if self._kOps[k].setoptimizer(): pass
            else: return self._invalidoptimizer()

            if self._kOps[k].setscheduler(): pass
            else: return self._invalidscheduler()
        return True

    def Start(self, sample = None):
        if sample is None:
            self.RestoreTracer()
            sample = self
        else: self.ImportSettings(sample.ExportSettings())

        self._cmod.sampletracer = sample
        self.__searchsplits__(sample)
        kfolds = self._cmod.kFolds
        kfolds.sort()
        if not len(kfolds): kfolds += [1]
        gr = next(iter(self._cmod.FetchTraining(kfolds[0], self.BatchSize)))
        self.preiteration(sample)
        if self.__initialize__(): pass
        else: return

        self._findpriortraining()
        self._cmod.metric_plots = self.PlotLearningMetrics
        path = self.WorkingPath + "machine-learning/" + self.RunName
        for ep in range(self.Epochs):
            ep += 1
            kfold_map = {}
            for k in kfolds:
                base = path + "/Epoch-" + str(ep) + "/kFold-"
                if self.Epoch is None: pass
                elif k not in self.Epoch: pass
                elif self.Epoch[k] < ep: kfold_map[k] = False
                else:
                    kfold_map[k] = True
                    self._cmod.RebuildEpochHDF5(ep, base, k)
                    continue
                self.mkdir(base + str(k))
                self._kOps[k].Epoch = ep
                self._kModels[k].Epoch = ep

                self._kOps[k].Train = True
                self._kModels[k].Train = True
                self.__train__(k, ep)

                self._kOps[k].Train = False
                self._kModels[k].Train = False
                self.__validation__(k, ep)
                self._kOps[k].stepsc()

                self.__evaluation__(k, ep)
                self._showloss(ep, k)

                self._kOps[k].save()
                self._kModels[k].save()

                self._cmod.DumpEpochHDF5(ep, base, k)
            if self.PlotLearningMetrics:
                self.Success("Plotting: Epoch " + str(ep))
                self._cmod.BuildPlots(ep, path + "/Plots")
            self._showloss(ep, -1, True)

    def __train__(self, kfold, epoch):
        container = []
        batches = self._cmod.FetchTraining(kfold, self.BatchSize)
        msg = "Epoch (" + str(epoch) + ") Running k-Fold (training) -> " + str(kfold)
        if not self.DebugMode: _, bar = self._MakeBar(len(batches), msg)
        for graph in batches:
            self._kOps[kfold].zero()
            res = self._kModels[kfold](graph)
            self._kModels[kfold].backward()
            self._kOps[kfold].step()
            if not self.DebugMode:
                container.append(res)
                bar.update(1)
            else:
                self._cmod.AddkFold(epoch, kfold, res, self._kModels[kfold].out_map)
                del res

            if not batches.purge: continue
            self._cmod.FastGraphRecast(epoch, kfold, container, self._kModels[kfold].out_map)
            for i in container: del i
            container = []

        if self.DebugMode: return
        self._cmod.FastGraphRecast(epoch, kfold, container, self._kModels[kfold].out_map)
        for i in container: del i

    def __validation__(self, kfold, epoch):
        container = []
        batches = self._cmod.FetchValidation(kfold, self.BatchSize)
        msg = "Epoch (" + str(epoch) + ") Running k-Fold (validation) -> " + str(kfold)
        if not self.DebugMode: _, bar = self._MakeBar(len(batches), msg)
        for graph in batches:
            res = self._kModels[kfold](graph)
            if not self.DebugMode:
                container.append(res)
                bar.update(1)
            else:
                self._cmod.AddkFold(epoch, kfold, res, self._kModels[kfold].out_map)
                del res

            if not batches.purge: continue
            self._cmod.FastGraphRecast(epoch, kfold, container, self._kModels[kfold].out_map)
            for i in container: del i
            container = []

        if self.DebugMode: return
        self._cmod.FastGraphRecast(epoch, kfold, container, self._kModels[kfold].out_map)
        for i in container: del i

    def __evaluation__(self, kfold, epoch):
        container = []
        batches = self._cmod.FetchEvaluation(self.BatchSize)
        if not self.DebugMode: _, bar = self._MakeBar(len(batches), "Epoch (" + str(epoch) + ") Running leave-out")
        for graph in batches:
            res = self._kModels[kfold](graph)
            if not self.DebugMode:
                container.append(res)
                bar.update(1)
            else:
                self._cmod.AddkFold(epoch, kfold, res, self._kModels[kfold].out_map)
                del res

            if not batches.purge: continue
            self._cmod.FastGraphRecast(epoch, kfold, container, self._kModels[kfold].out_map)
            for i in container: del i
            container = []

        if self.DebugMode: return
        self._cmod.FastGraphRecast(epoch, kfold, container, self._kModels[kfold].out_map)
        for i in container: del i

    def preiteration(self, inpt = None):
        if inpt is not None: pass
        else: inpt = self

        if not len(inpt.ShowTrees) and not len(inpt.Tree):
            self._notree()
            self.RestoreTracer()
        if not len(inpt.Tree) and len(inpt.ShowTrees):
            inpt.Tree = inpt.ShowTrees[0]
        elif inpt.Tree in inpt.ShowTrees: pass
        else: self._nofailtree()

        if not len(inpt.ShowGraphs) and not len(inpt.GraphName):
            self._nographs()
            self.RestoreTracer()
        if not len(inpt.GraphName) and len(inpt.ShowGraphs):
            inpt.GraphName = inpt.ShowGraphs[0]
        elif inpt.GraphName in inpt.ShowGraphs: pass
        else: self._nofailgraphs()
        msg = "Using GraphName: " + inpt.GraphName
        msg += " with Tree: " + inpt.Tree
        self.Success(msg)
        return False

