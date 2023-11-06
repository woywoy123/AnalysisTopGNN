from torchmetrics.classification import MulticlassAccuracy
import torch

class LossFunctions:
    def __init__(self, _loss, _class=False):
        self._loss = _loss
        self._class = _class

        if _loss.upper() == "CEL": self.CrossEntropyLoss()
        elif _loss.upper() == "MSEL": self.MeanSquareErrorLoss()
        elif _loss.upper() == "HEL": self.HingeEmbeddingLoss()
        elif _loss.upper() == "KLD": self.KLDivergenceLoss()
        else: self.NoDefault()
        if self._class: self._class = self.ToDigit

    def ToDigit(self, inpt): return torch.round(inpt)

    def CrossEntropyLoss(self):
        def accuracyfunction(truth, pred):
            acc = MulticlassAccuracy(num_classes=pred.size()[1])
            return 100 * acc(pred.max(1)[1].view(-1), truth.view(-1))
        def funct(truth, pred): return truth.view(-1).to(dtype=torch.long), pred

        self._loss = torch.nn.CrossEntropyLoss()
        self._func = funct
        self._acc = accuracyfunction
        self._class = False

    def MeanSquareErrorLoss(self):
        def accuracyfunction(truth, pred): return truth.view(-1) - pred.view(-1)
        def funct(truth, pred): return truth.view(-1).to(dtype=torch.float), pred.view(-1)

        self._loss = torch.nn.MSELoss()
        self._func = funct
        self._acc = accuracyfunction

    def HingeEmbeddingLoss(self):
        def funct(truth, pred): return truth, pred
        def accuracyfunction(truth, pred): return self.loss

        self._loss = torch.nn.HingeEmbeddingLoss()
        self._func = funct
        self._acc = accuracyfunction

    def KLDivergenceLoss(self):
        def funct(truth, pred): return truth, pred
        def accuracyfunction(truth, pred): return self.loss

        self._loss = torch.nn.HingeEmbeddingLoss()
        self._func = funct
        self._acc = accuracyfunction

    def NoDefault(self):
        def funct(truth, pred): return truth, pred
        def accuracyfunction(truth, pred): return -1

        self._func = funct
        self._acc = accuracyfunction

    @property
    def loss(self):
        t, p = self._func(self.truth, self.pred)
        return self._loss(p, t)

    @property
    def accuracy(self):
        truth, pred = self.truth.clone().to("cpu"), self.pred.clone().detach().to("cpu")
        return self._acc(truth, pred)

    def __call__(self, pred, truth):
        self.pred, self.truth = pred, truth
        if self._class == False: pass
        else: self.pred = self._class(self.pred)
        return {"loss": self.loss, "acc": self.accuracy}
