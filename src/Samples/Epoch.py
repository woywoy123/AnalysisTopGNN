import time 
import torch
from AnalysisTopGNN.Statistics import Metrics
from AnalysisTopGNN.Tools import Tools
from AnalysisTopGNN.Plotting.EpochPlots import EpochPlots, Container

class Epoch(EpochPlots, Metrics, Tools):

    def __init__(self, epoch = None):
        self.EpochTime = time.time()
        self.Epoch = epoch
        self.ModelOutputs = []
        self.OutDir = "./"
        
        self.NodeTimes = {} 
        
        self.FoldTime = {}
        self.Fold = None
        
        self.t_e = 0
        self.t_s = 0

        self.names = []
        self._Package = {}

    def MakeDictionary(self, name):
        setattr(self, "Accuracy_"+name, {k[2:] : [] for k in self.ModelOutputs})
        setattr(self, "Loss_"+name, {k[2:] : [] for k in self.ModelOutputs})
        setattr(self, "TotalLoss_" + name, [])
        setattr(self, "ROC_"+name, {k[2:] : {"truth" : [], "p_score" : []} for k in self.ModelOutputs})
        self.names.append(name)

    def Collect(self, pred, truth, loss_acc, name):
        ROC = self.__dict__["ROC_" + name]
        Loss = self.__dict__["Loss_" + name]
        Accuracy = self.__dict__["Accuracy_" + name]
        TotalLoss = self.__dict__["TotalLoss_" + name]

        indx = pred.batch.unique()
        sub_pred = [pred.subgraph(pred.batch == b) for b in indx]

        # Get the average node time 
        av_n = (self.t_e - self.t_s) / pred.num_nodes
        for i in sub_pred:
            if i.num_nodes not in self.NodeTimes:
                self.NodeTimes[i.num_nodes] = []
            self.NodeTimes[i.num_nodes].append(i.num_nodes*av_n) 
        
        # Get the loss for this prediction
        self.TotalLoss = 0
        for key in Accuracy: 
            Accuracy[key].append(loss_acc[key][1].detach().cpu().tolist())
            self.TotalLoss = self.TotalLoss + loss_acc[key][0] 
            Loss[key].append(loss_acc[key][0].detach().cpu().item())
        TotalLoss += [self.TotalLoss.detach().cpu().item()]

        for key in ROC:
            ROC[key]["truth"] += truth[key].view(-1).detach().cpu().to(dtype = torch.int).tolist()
            ROC[key]["p_score"].append(pred[key].softmax(dim = 1).detach().cpu())
        self.FoldTime[self.Fold] += (self.t_e - self.t_s)
    
    def StartTimer(self):
        self.t_s = time.time()

    def StopTimer(self):
        self.t_e = time.time()
    
    def Process(self, MakeFigure = True):
        self.EpochTime = time.time() - self.EpochTime
        self.TotalLoss = None
        
        if MakeFigure:
            self.NodeTimingHistograms()
            self.AccuracyHistograms(self.ModelOutputs)
            self.LossHistograms(self.ModelOutputs)
        try:
            self.CompileROC(self.names, self.ModelOutputs)
        except:
            pass

        self._Package[self.Epoch] = {}
        self._Package[self.Epoch] |= {"Accuracy_" + i : self.MakeStatics(self.__dict__["Accuracy_" + i]) for i in self.names }
        self._Package[self.Epoch] |= {"Loss_" + i : self.MakeStatics(self.__dict__["Loss_" + i]) for i in self.names }
        self._Package[self.Epoch] |= {"TotalLoss_" + i : self.MakeStatics(self.__dict__["TotalLoss_" + i]) for i in self.names }
        self._Package[self.Epoch] |= {"EpochTime" : self.EpochTime}
        self._Package[self.Epoch] |= {"AUC_" + i + "_" + k : self.__dict__["ROC_" + i][k]["auc"] for i in self.names for k in self.__dict__["ROC_" + i]} 
        self._Package[self.Epoch] |= {"NodeTimes" : self.MakeStatics(self.NodeTimes)}
        self._Package[self.Epoch] |= {"FoldTime" : self.MakeStatics([i for i in self.FoldTime.values()])}
        self._Package["OutputNames"] = self.ModelOutputs
        self._Package["Names"] = self.names

        for i in self.names:
            setattr(self, "Accuracy_" + i, None)           
            setattr(self, "Loss_" + i, None)
            setattr(self, "TotalLoss_" + i, None)           
            setattr(self, "ROC_" + i, None)
        self.NodeTimes = None
        self.FoldTime = None

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __add__(self, other):
        self._Package |= other._Package
        return self
    
    def Compile(self, outdir):
        epochs = [i for i in list(self._Package) if isinstance(i, int)]
        epochs.sort()
        
        features = [i[2:] for i in self._Package["OutputNames"]]
        names = self._Package["Names"]
        
        Merge = {}
        for i in epochs:
            for j in self._Package[i]:
                if j not in Merge:
                    Merge[j] = Container()
                Merge[j].Add(self._Package[i][j])
        
        Combined = {} 
        for i in Merge:
            if len(Merge[i].yData) != 0:
                Combined[i] = Merge[i]
            else:
                Combined |= {i + "_" + str(j) : Merge[i].FeatureContainer[j] for j in Merge[i].FeatureContainer}
        
        Compile = {}
        NodeTimes = []
        Accuracy = {i : [] for i in features}
        Loss = {i : [] for i in features}
        Loss["Total"] = []
        AUC = {i : [] for i in features}
        for i in Combined:
            cont = Combined[i]
            if i == "EpochTime":
                cont.Plots = self.EpochTimePlot(epochs, cont.yData, outdir)
                Compile[i] = cont
           
            elif i.startswith("NodeTimes"):
                cont.Plots = self.NodeTimePlot(epochs, cont.yData, outdir, i.split("_")[-1], cont.errData, cont.errData)
                NodeTimes.append(cont)

            elif i.startswith("FoldTime"):
                cont.Plots = self.FoldTimePlot(epochs, cont.yData, outdir, cont.errData, cont.errData)
                Compile[i] = cont

            elif i.startswith("Accuracy"):
                cont.Plots = self.AccuracyPlot(epochs, cont.yData, outdir, i.split("_")[1], i.split("_")[-1], cont.errData, cont.errData)
                Accuracy[i.split("_")[-1]].append(cont)

            elif i.startswith("AUC"):
                cont.Plots = self.AUCPlot(epochs, cont.yData, outdir, i.split("_")[1])
                AUC[i.split("_")[-1]].append(cont)
            
            elif i.startswith("TotalLoss"):
                cont.Plots = self.LossPlot(epochs, cont.yData, outdir, i.split("_")[-1], cont.errData, cont.errData)
                Loss["Total"].append(cont)

            elif i.startswith("Loss_"):
                cont.Plots = self.LossPlot(epochs, cont.yData, outdir, i.split("_")[1], cont.errData, cont.errData)
                Loss[i.split("_")[-1]].append(cont)

        self.Markers = {m : None for m in names}
        self.GetConsistentModeMarker(self.Markers)

        self.Colors = {m : None for m in features}
        self.GetConsistentModeColor(self.Colors)

        for i in Compile:
            Compile[i].Plots.SaveFigure()
        
        Com = self.MergeNodeTimes(NodeTimes, outdir)
        Com.SaveFigure()
        
        Com = self.MergeAUC(AUC, self.Colors, self.Markers, outdir)
        Com.SaveFigure()
        
        Com1, Com2 = self.MergeLoss(Loss, self.Colors, self.Markers, outdir)
        Com1.SaveFigure()
        Com2.SaveFigure()

        Com = self.MergeAccuracy(Accuracy, self.Colors, self.Markers, outdir)
        Com.SaveFigure()


