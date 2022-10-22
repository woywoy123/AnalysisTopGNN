import torch
from torch_geometric.data import Data

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
            return accuracy(truth.view(-1), pred.max(1)[1].view(-1))
        
        return {"loss" : torch.nn.CrossEntropyLoss(), "func" : lossfunction, "accuracy" : accuracyfunction}
    
    def MeanSquareErrorLoss(self, pred = None, truth = None):
        return torch.nn.MSELoss()

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

class Model:

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

    def GetModelInputs(self, model):
        code = model.forward.__code__
        inputs = code.co_varnames[1:code.co_argcount]
        self._modelinputs |= {key : None for key in inputs}
        return self._modelinputs
    
    def _GetModelParameters(self, model, Prefix):
        return {key : model.__dict__[key] for key in list(model.__dict__) if key.startswith(Prefix)}

    def GetModelOutputs(self, model = None):
        if len(self._modeloutputs) != 0:
            return self._modeloutputs
        self._modeloutputs |= self._GetModelParameters(model, "O_")
        return self._modeloutputs

    def GetModelLossFunction(self, model):
        if len(self._modelloss) != 0:
            return self._modelloss
        self._modelloss = self._GetModelParameters(model, "L_")
        self._modelloss = {key : LossFunctions(self._modelloss[key]) for key in list(self._modelloss)}
        return self._modelloss
    
    def GetModelClassifiers(self, model):
        return self._GetModelParameters(model, "C_")

    def SampleCompatibility(self, sample):
        self._model = self._model.to(self.Device)
        def MakeKey(smpl, key_T, modeldict):
            return {key : "O_" + key[len(key_T):] for key in smplkeys if "O_" + key[len(key_T):] in modeldict}
        
        def Compatible(smpl, mdl):
            sdic = list(smpl.values())
            if sum([1 for i in mdl if i in sdic]) == 0:
                return {}
            return smpl
        
        if self._train == self._prediction != None:
            return self._train, self._prediction

        smplkeys = list(sample.to_dict())
        self._graphtruthkeys |= MakeKey(smplkeys, "G_T_", self._modeloutputs)
        self._nodetruthkeys |= MakeKey(smplkeys, "N_T_", self._modeloutputs)
        self._edgetruthkeys |= MakeKey(smplkeys, "E_T_", self._modeloutputs)

        self._keymapping |= self._graphtruthkeys
        self._keymapping |= self._nodetruthkeys 
        self._keymapping |= self._edgetruthkeys 
        self._truth = len(self._keymapping) >= len(self._modeloutputs)
        
        out = {}
        out |= Compatible(self._graphtruthkeys, self._modeloutputs)
        out |= Compatible(self._nodetruthkeys, self._modeloutputs)
        out |= Compatible(self._edgetruthkeys, self._modeloutputs)
        
        self._train = True if len(out) == len(self._modelinputs) else False    
        self._prediction = len(MakeKey(smplkeys, "O_", self._modelinputs)) == len(self._modelinputs)
            
        return self._train, self._prediction
        
    def Prediction(self, data):
        self._model(**{k : data.to_dict()[k] for k in self._modelinputs})
        Pred = {feat[2:] : self._model.__dict__[feat] for feat in self._keymapping.values()}
        Pred["edge_index"] = data.edge_index
        Pred["batch"] = data.batch
        
        if self._truth == False:
            return Data().from_dict(Pred), None, None
       
        data = data.to_dict()
        Truth = {feat[4:] : data[feat] for feat in self._keymapping}
        Truth["edge_index"] = data["edge_index"]
        Truth["batch"] = data["batch"]
        
        output = {key[2:] : self._modelloss["L_" + key[2:]](Pred[key[2:]], Truth[tru[4:]]) 
                    for tru, key in zip(self._keymapping, self._keymapping.values())} 

        return  Data().from_dict(Pred), Data().from_dict(Truth), output

    def eval(self):
        self._model.eval()

    def train(self):
        self._model.train()



