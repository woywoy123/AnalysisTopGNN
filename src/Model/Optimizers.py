import torch
from torch.optim.lr_scheduler import ExponentialLR, CyclicLR
from AnalysisG.Settings import Settings


class OptimizerWrapper(Settings):
    def __init__(self):
        self.Caller = "OPTIMIZER"
        Settings.__init__(self)
        self.train = False
        self._op = None
        self._sc = None
        self._mod = None

    def SetOptimizer(self):
        self._pth = self.OutputDirectory + "/" + self.RunName
        if len(self.OptimizerParams) == 0:
            return False
        if self.Optimizer == "ADAM":
            self._op = torch.optim.Adam(self._mod.parameters(), **self.OptimizerParams)
        elif self.Optimizer == "SDG":
            self._op = torch.optim.SGD(self._mod.parameters(), **self.OptimizerParams)
        else:
            return False
        return True

    def dump(self):
        dct = {}
        dct["epoch"] = self.Epoch
        dct["optim"] = self._op.state_dict()
        if self._sc is not None:
            dct["sched"] = self._sc.state_dict()
        torch.save(dct, self._pth + "/" + str(self.Epoch) + "/TrainingState.pth")

    def load(self):
        v = torch.load(self._pth + "/" + str(self.Epoch) + "/TrainingState.pth")
        self.Epoch = v["epoch"]
        self._op.load_state_dict(v["optim"])
        if self._sc is not None:
            self._sc.load_state_dict(v["sched"])
        return self._pth + " @ " + str(self.Epoch)

    def step(self):
        if not self.train:
            return
        self._op.step()

    def zero(self):
        if not self.train:
            return
        self._op.zero_grad()

    def SetScheduler(self):
        self.SchedulerParams["optimizer"] = self._op
        if self.Scheduler == "ExponentialLR":
            self._sc = ExponentialLR(**self.SchedulerParams)
        if self.Scheduler == "CyclicLR":
            self._sc = CyclicLR(**self.SchedulerParams)
        if len(self.SchedulerParams) == 0:
            return False
        if self._sc == None:
            return False
        return True

    def stepsc(self):
        if self._sc is None:
            return
        self._sc.step()
