from AnalysisTopGNN.Model import Model
import torch


class Model(Model):
    def __init__(self, model):
        self._modelinputs = {}
        self._modeloutputs = {}
        self._modelloss = {}
        self._modelclassifiers = {}

        self._graphtruthkeys = {}
        self._nodetruthkeys = {}
        self._edgetruthkeys = {}
        self._keymapping = {}

        self._train = None
        self._prediction = None
        self._truth = False
        self.Device = None
        self._model = model

        self.GetModelInputs(self._model)
        self.GetModelOutputs(self._model)
        self.GetModelLossFunction(self._model)
        self.GetModelClassifiers(self._model)
