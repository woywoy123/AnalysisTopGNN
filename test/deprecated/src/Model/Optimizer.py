import torch
from AnalysisTopGNN.IO import PickleObject, UnpickleObject


class Optimizer:
    def __init__(self, model, keyword, parameters):
        self.optimizer = None
        self.optimizer = (
            self.ADAM(model, parameters) if keyword == "ADAM" else self.optimizer
        )
        self.optimizer = (
            self.StochasticGradientDescent(model, parameters)
            if keyword == "SGD"
            else self.optimizer
        )
        self.name = keyword
        self.params = parameters

    def ADAM(self, model, params):
        return torch.optim.Adam(model.parameters(), **params)

    def StochasticGradientDescent(self, model, params):
        return torch.optim.SGD(model.parameters(), **params)

    def __call__(self, step):
        if step:
            self.optimizer.step()
        else:
            self.optimizer.zero_grad()

    def DumpState(self, OutputDir):
        PickleObject(self.optimizer.state_dict(), OutputDir + "/OptimizerState")

    def LoadState(self, InputDir):
        self.optimizer.load_state_dict(UnpickleObject(InputDir + "/OptimizerState"))
