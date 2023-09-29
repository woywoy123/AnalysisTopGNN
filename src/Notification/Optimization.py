from .Notification import Notification
from AnalysisG.IO import UnpickleObject


class _Optimizer(Notification):
    def __init__(self):
        pass

    def _NoModel(self):
        if self.Model is not None:
            return False
        self.Warning("No Model was given.")
        return True

    def _NoSampleGraph(self):
        hashes = self.GetDataCacheHashes()
        l = len(hashes)
        self.RestoreTheseHashes(hashes[: self.BatchSize])
        if l == 0:
            return self.Warning("No Sample Graphs found")
        self.Success("Found " + str(l) + " Sample Graphs")
        return hashes

    def _notcompatible(self):
        return self.Failure("Model not compatible with given input graph sample.")

    def _setoptimizer(self):
        if not self._op.SetOptimizer():
            return self.Failure("Invalid Optimizer.")
        return not self.Success("Set the optimizer to: " + self._op.Optimizer)

    def _setscheduler(self):
        if not self._op.SetScheduler():
            return
        self.Success("Set the scheduler to: " + self._op.Scheduler)

    def _searchtraining(self):
        self.Epoch = 0
        pth = self._outDir + "/" + self.RunName
        epochs = self.ls(pth)
        kf = []
        if not self.ContinueTraining:
            return True
        if len(epochs) == 0:
            return self.Warning(
                "No prior training was found under: " + pth + ". Generating..."
            )
        epochs = [int(ep) for ep in epochs]
        epochs.sort()
        for ep in epochs:
            path = pth + "/" + str(ep) + "/"
            for k in self.ls(path):
                kPath = path + k + "/TorchSave.pth"
                if not self.IsFile(kPath):
                    continue
                if k not in self._kModels:
                    continue
                self._kModels[k]._pth = self._outDir + "/" + self.RunName
                self._kOp[k]._pth = self._outDir + "/" + self.RunName
                self._kModels[k].Epoch = str(ep) + "/" + k
                self._kOp[k].Epoch = str(ep) + "/" + k

        for i in self._kModels:
            if self._kModels[i].Epoch is None:
                self._kModels[i].Epoch = ""
                continue
            try:
                self.Success("Model loaded: " + self._kModels[i].load())
            except KeyError:
                return not self.Warning("Loading Model Failed. Skipping loading...")
            try:
                self.Success("Optimizer loaded: " + self._kOp[i].load())
            except KeyError:
                return not self.Warning("Loading Optimizer Failed. Skipping loading...")
        return True

    def _searchdatasplits(self):
        pth = self._outDir + "/DataSets/"
        ls = self.ls(pth)
        if len(ls) == 0 and self.kFold is not None:
            self.kFold = None
            return self.Warning(
                "No sample splitting found (k-Fold). Training on entire sample."
            )
        elif len(ls) == 0:
            self.Warning("Provided kFold not found. Training on entire sample.")
            self.kFold = None
            return
        if self.TrainingName + ".pkl" not in ls:
            return self.Warning(
                "The given training sample name was not found, but found the following: "
                + "\n-> ".join(ls)
            )

        f = UnpickleObject(pth + self.TrainingName)
        if isinstance(self.kFold, int):
            k = ["k-" + str(self.kFold)]
        elif isinstance(self.kFold, str):
            k = [self.kFold]
        elif isinstance(self.kFold, list):
            k = ["k-" + str(t) if isinstance(t, int) else t for t in self.kFold]
        elif self.kFold is None:
            k = [k for k in f if not k.endswith("_hashes")]
        else:
            k = [f]

        try:
            self.kFold = {kF: f[kF] for kF in k}
        except KeyError:
            msg = "Given k-Fold not found. But found the following folds: "
            l = len(msg)
            msg += "\n-> ".join([""] + list(f))
            self.Failure(msg)
            return self.FailureExit("=" * l)
        self.Success("Found the training sample: " + self.TrainingName)
        self.Success("Training Sets Detected: " + "\n-> ".join([""] + list(self.kFold)))

    def _showloss(self):
        string = ["Epoch-kFold: " + self._ep.Epoch]
        if self._op._sc is not None:
            string[-1] += " Current LR: {:.10f}".format(self._op._sc.get_lr()[0])
        for f in self.Model._l:
            string.append(
                "Feature: {}, Loss: {:.10f}, Accuracy: {:.10f}".format(
                    f, self.Model._l[f]["loss"], self.Model._l[f]["acc"]
                )
            )
        print("\n-> ".join(string))
