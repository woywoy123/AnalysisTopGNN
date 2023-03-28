import torch
from torchmetrics.functional import accuracy

class LossFunctions:

    def __init__(self, keyword = None):
        self.loss = None
        if keyword == "CEL":
            self.loss = self.CrossEntropyLoss()
        elif keyword == "MSEL":
            self.loss = self.MeanSquareErrorLoss()
        elif keyword == "HEL":
            self.loss = self.HingeEmbeddingLoss()
        elif keyword == "KLD":
            self.loss = self.KLDivergenceLoss()
        self.name = keyword

    def CrossEntropyLoss(self):
        def lossfunction(truth, pred):
            return truth.view(-1).to(dtype = torch.long), pred
        
        def accuracyfunction(truth, pred):
            return 100*accuracy(truth.view(-1), pred.max(1)[1].view(-1))
        
        return {"loss" : torch.nn.CrossEntropyLoss(), "func" : lossfunction, "accuracy" : accuracyfunction}
    
    def MeanSquareErrorLoss(self, pred = None, truth = None):
        def lossfunction(truth, pred):
            return truth.view(-1).to(dtype = torch.float), pred.view(-1)
        
        def accuracyfunction(truth, pred):
            return truth.view(-1) - pred.view(-1)
        return {"loss" : torch.nn.MSELoss(), "func" : lossfunction, "accuracy" : accuracyfunction}

    def HingeEmbeddingLoss(self, pred = None, truth = None):
        return torch.nn.HingeEmbeddingLoss()

    def KLDivergenceLoss(self, pred = None, truth = None):
        return torch.nn.KLDivLoss()
    
    def __call__(self, pred, truth):
        loss = self.loss["loss"]
        l_func = self.loss["func"]
        a_func = self.loss["accuracy"]
        truth, pred = l_func(truth, pred)

        return [loss(pred, truth), a_func(truth, pred)]


