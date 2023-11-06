from .Notification import Notification

class _Optimizer(Notification):
    def __init__(self): pass

    def _searchdatasplits(self, path):
        if path.endswith(".hdf5"): pass
        else: path += ".hdf5"

        msg = "No sample splitting found (k-Fold). Training on entire sample."
        if self.IsFile(path): pass
        else: return self.Warning(msg)

        eval_fold = {}
        train_fold = {}
        leaveout_fold = {}
        maps = self._cmod.length()
        for k in maps:
            if not k.startswith("train"): pass
            else: train_fold[int(k.split("-k")[-1])] = maps[k]

            if not k.startswith("eval"): pass
            else: eval_fold[int(k.split("-k")[-1])] = maps[k]

            if not k.startswith("leave-out"): pass
            else: leaveout_fold["-".join(k.split("-")[:-1])] = maps[k]

        self.Success("\n"+"="*25 + " k-Fold Statistics " + "="*25)
        key = "Found the following training k-Folds in > " + self.TrainingName + " < :" + "\n"
        for i in sorted(train_fold):
            key += ":: kFold - " + str(i) + " (" + str(train_fold[i]) + ")"
            if not i%5: key += "\n"
        self.Success(key)

        key = "Found the following validation k-Folds in > " + self.TrainingName + " < :" + "\n"
        for i in sorted(eval_fold):
            key += ":: kFold - " + str(i) + " (" + str(eval_fold[i]) + ")"
            if not i%5: key += "\n"
        self.Success(key)

        key = "Found leave-out sub-sample > " + self.TrainingName + " < -> "
        for i in sorted(leaveout_fold): key += "(" + str(leaveout_fold[i]) + ")"
        self.Success(key + "\n" + "="*25 + " End Statistics " + "="*25)

        if self.kFold is None: self._cmod.UseTheseFolds(list(train_fold))
        elif isinstance(self.kFold, int): self._cmod.UseTheseFolds([self.kFold])
        else: self._cmod.UseTheseFolds([i for i in self.kFold if isinstance(i, int)])

    def _findpriortraining(self):
        path = self.WorkingPath + "/machine-learning/" + self.RunName
        if self.IsPath(path): pass
        else: self.mkdir(path)

        kfolds = self._cmod.kFolds
        kfolds.sort()
        epoch = {}
        for k in kfolds: epoch[k] = 0
        self.Epoch = epoch

        if not self.ContinueTraining: return
        max_map = {}
        msg = "No prior training was found under: " + path + ". Generating..."
        for f in self.lsFiles(path, ".pth"):
            ep, fold = f.lstrip(path).split("/")[:2]
            ep, fold = int(ep.split("-")[-1]), int(fold.split("-")[-1])
            if fold not in max_map: max_map[fold] = ep
            if max_map[fold] >= ep: continue
            max_map[fold] = ep

        if not len(max_map): return self.Warning(msg)
        for fold, ep in max_map.items():
            if fold not in self._kOps: continue
            if fold not in self._kModels: continue

            self._kOps[fold].KFold = fold
            self._kModels[fold].KFold = fold

            self._kOps[fold].Epoch = ep
            self._kModels[fold].Epoch = ep

            msg = "Failed to load Optimizer state... "
            msg += "(fold: " + str(fold) + " epoch:" + str(ep) + ")"
            try: self._kOps[fold].load()
            except ValueError:
                self.Failure("="*len(msg))
                self.FailureExit(msg)
            self._kModels[fold].load()
        self.Epoch = max_map

    def _nographs(self): return self.Warning("Missing Graph Name. Will check cache...")
    def _notree(self): return self.Warning("Missing Tree Name. Will check cache...")

    def _nofailgraphs(self): return self.Failure("Missing Graph Name...")
    def _nofailtree(self):   return self.Failure("Missing Tree Name...")

    def _nomodel(self):
        if self.Model is None: pass
        else: return False

        self.Warning("No Model was given.")
        return True

    def _notcompatible(self):
        self.Failure("Model not compatible with given input graph sample.")
        return False

    def _invalidoptimizer(self):
        self.Failure("Invalid Optimizer:" + self.Optimizer)
        return False

    def _invalidscheduler(self):
        self.Failure("Invalid Scheduler: " + self.Scheduler)
        return False

    def _showloss(self, epoch, kfold, override = False):
        if not self.DebugMode and not override: return

        string = ["Epoch-kFold: " + str(epoch)]
        if kfold != -1: string[-1] += " - " + str(kfold)
        if kfold == -1: lr = None
        elif self._kOps[kfold].scheduler is None: lr = None
        else: lr = self._kOps[kfold].scheduler.get_last_lr()[0]

        if lr is None: pass
        else: string[-1] += " Current LR: {:.10f}".format(lr)
        self.Success("\n->".join(string))
        report = self._cmod.reportable()
        if not len(report["loss_train"]): return
        outputs = {}
        for i, j in report.items():
            try: len(j)
            except: continue
            try: i = i.encode("UTF-8").split("_")
            except TypeError: i = i.split("_")
            met, mode = i[:2]
            mode = met + "-" + mode
            for k, l in j.items():
                if k not in outputs: outputs[k] = {}
                if mode not in outputs[k]: outputs[k][mode] = ""
                l  = str(round(l, 5))
                if i[-1] == "up": l = " (+" + l
                elif i[-1] == "down": l = " | -" + l + ")"
                outputs[k][mode] += l

        out = []
        for i in outputs:
            try: x = "(" + i + ") "
            except TypeError: x = "(" + i.decode("UTF-8") + ") "
            strings = {}
            for j, k in outputs[i].items():
                met, mode = j.split("-")
                if met not in strings: strings[met] = ""
                strings[met] += mode + ": " + k + " :: "
            out += [" -> " + x + j + " " + k for j, k in strings.items()]

        x = int(max([len(i) for i in out]) / 2) - 6
        self.Success("\n" + "="*(x-1) + " MODEL REPORT " + "="*(x-1))
        self.Success("\n".join([""] + out) + "\n")
