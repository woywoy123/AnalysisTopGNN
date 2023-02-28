from AnalysisTopGNN.Plotting import CommonFunctions
from AnalysisTopGNN.Plotting.TemplateHistograms import TH1FStack
import math
import statistics
import random

class Functions(CommonFunctions):
    def __init__(self):
        CommonFunctions.__init__(self)

        # --- Cosmetic --- #
        self.LineStyle = None
        self.Marker = None
 
        # --- Line Properties --- #
        self.DefineAxisData("x")
        self.DefineAxisData("y")
        self.DefineAxisData("up_y", True)
        self.DefineAxisData("down_y", True)
        self.DoStatistics = False
   
    def DefineRange(self, Dims):
        if len(self.Get(Dims + "Data")) == 0:
            self.Set(Dims + "Min", 0)
        
        if len(self.Get(Dims + "Data")) == 0:
            self.Set(Dims + "Max", 1)
        self.DefineCommonRange(Dims)       

    def ApplyRandomMarker(self, obj):
        ptr = [",", ".", "-", "x", "o", "O"]
        if obj.Marker == True:
            random.shuffle(ptr)
        elif obj.Marker != None:
            return 
        obj.Marker = ptr[0] 
    
    def MakeStatistics(self, inpt):
        if isinstance(inpt, dict):
            xinpt = list(inpt.keys())
            inpt = list(inpt.values())
        else:
            xinpt = [i+1 for i in range(len(inpt))]            

        output = {}
        for i in range(len(inpt)):
            mean = statistics.mean(inpt[i])
            stdev = statistics.pstdev(inpt[i], mean)/math.sqrt(len(inpt[i]))
            output[xinpt[i]] = [mean, stdev]
        return output

class TLine(Functions):
    
    def __init__(self, **kwargs):
        Functions.__init__(self)
        self.ApplyInput(kwargs)
        self.Caller = "TLINE"
 
    def Compile(self, Reset = True):
        self.Precompiler()
        if Reset:
            self.ResetPLT()
            self.DefineStyle()
            self.ApplyToPLT()
        self.ApplyRandomMarker(self)
        
        if self.DoStatistics:
            self._temp = self.xData
            out = self.MakeStatistics(self.xData)
            self.xData = [i for i in out]
            self.yData = [out[i][0] for i in out]
            self.up_yData = [out[i][1] for i in out]
            self.down_yData = [out[i][1] for i in out]

        self.xData = self.SanitizeData(self.xData)
        self.yData = self.SanitizeData(self.yData)

        self.down_yData = self.SanitizeData(self.down_yData)
        self.up_yData = self.SanitizeData(self.up_yData)

        self.DefineRange("y")
        self.DefineRange("x")
        
        if len(self.xData) != len(self.yData):
            return 

        if len(self.up_yData) != 0 and len(self.down_yData) != 0:
            self.PLT.errorbar(x = self.xData, y = self.yData, yerr = [self.up_yData, self.down_yData], 
                        linestyle = self.LineStyle, color = self.Color, marker = self.Marker, 
                        linewidth = 1, capsize = 3, label = self.Title) 
        else:
            self.PLT.plot(self.xData, self.yData, marker = self.Marker, color = self.Color, linewidth = 1, label = self.Title)
        
        if Reset:
            self.PLT.title(self.Title)
            self.PLT.xlabel(self.xTitle)
            self.PLT.ylabel(self.yTitle)
            self.PLT.xlim(self.xMin, self.xMax)
            self.PLT.ylim(self.yMin, self.yMax)

        if self.Logarithmic:
            self.PLT.yscale("log")
        if self.DoStatistics:
            self.xData = self._temp

        if isinstance(self.xTickLabels, list):
            self.Axis.set_xticks(self.xData)
            self.Axis.set_xticklabels(self.xTickLabels)

class CombineTLine(Functions):

    def __init__(self, **kwargs):
        Functions.__init__(self)

        self.Lines = []
        self.Colors = []
        self.LegendOn = True
        
        self.ApplyInput(kwargs)
        self.Caller = "COMBINED-TLINE"

        self.ResetPLT()
    
    def ConsistencyCheck(self):
        for i in self.Lines:
            i.Compile()
            self.yData += i.yData
            self.xData += i.xData
        self.xData = self.SanitizeData(self.xData)
        self.yData = self.SanitizeData(self.yData)
         
        self.DefineRange("x")
        self.DefineRange("y")
        
        for i in self.Lines:
            i.xMin = self.xMin
            i.xMax = self.xMax
            i.yMin = self.yMin
            i.yMax = self.yMax

            if self.xTitle == None:
                self.xTitle = i.xTitle
            if self.yTitle == None:
                self.yTitle = i.yTitle
            
            self.ApplyRandomColor(i)
            self.ApplyRandomMarker(i)

    def Compile(self):

        self.ConsistencyCheck()

        self.ResetPLT()
        self.DefineStyle()
        self.ApplyToPLT()
       
        for i in self.Lines:
            i.Compile(False)
        
        if self.LegendOn:
            self.PLT.legend()
        if self.Logarithmic:
            self.PLT.yscale("log")

        self.PLT.title(self.Title)
        self.PLT.xlabel(self.xTitle)
        self.PLT.ylabel(self.yTitle)
        self.PLT.xlim(self.xMin, self.xMax)
        self.PLT.ylim(self.yMin, self.yMax)

        if isinstance(self.xTickLabels, list):
            self.Axis.set_xticks(self.xData)
            self.Axis.set_xticklabels(self.xTickLabels)

class TLineStack(CombineTLine):
    def __init__(self, **kargs):
        self.Data = []
        self.MakeStaticHistograms = True
        self.ROC = False
        CombineTLine.__init__(self, **kargs)
    
    def __Recursive(self, inpt, search):
        if isinstance(inpt, dict) == False:
            return inpt
        if search in inpt:
            if isinstance(inpt[search], list):
                return inpt[search]
            out = []
            for k in inpt[search]:
                out += [k]*inpt[search][k]
            return out
        return [l for i in inpt for l in self.__Recursive(inpt[i], search)]

    def __Organize(self):
        def ScanDict(string, dic):
            for i in range(len(string)):
                return ScanDict(string[i+1:], dic[string[i]]) 
            return dic

        def Switch(inpt):
            if isinstance(inpt, str):
                return ScanDict(inpt.split("/"), self.Data)
            else:
                return inpt

        self._Hists = {}
        self.Lines = { T : {} for T in self.Lines }
        for x, y, t in zip(self.xData, self.yData, self.Lines):
            data_x = Switch(x)
            data_y = Switch(y)

            params = {
                        "xData" : [float(i) if isinstance(i, str) else i for i in self.__Recursive(data_x, x)], 
                        "yData" : [float(i) if isinstance(i, str) else i for i in self.__Recursive(data_y, y)],
                        "Title" : t,
                    }

            if self.DoStatistics:
                sort = {}
                for y, x in zip(params["yData"], params["xData"]):
                    if x not in sort:
                        sort[x] = []
                    sort[x].append(y)
                params["xData"] = sort
                params["yData"] = []
                
            params["DoStatistics"] = self.DoStatistics
            self.Lines[t] = params
        
   
        if self.DoStatistics and self.MakeStaticHistograms:
            for t in self.Lines:
                Plot = {}
                Plot["xBins"] = 100
                Plot["Title"] = "Distribution of Data Points for " + t
                Plot["Histograms"] = []
                for p in self.Lines[t]["xData"]:
                    Plot["Histograms"] += [{ "Title" : p, "xData" : self.Lines[t]["xData"][p] }]
                Plot["Filename"] = "xProjection_" + t
                Plot["xTitle"] = self.yTitle # This is correct. We are projecting along the x-axis
                Plot["OutputDirectory"] = self.OutputDirectory + "/ProjectionPlots/" + self.Filename
                self._Hists[t] = TH1FStack(**Plot)
            
            Plot = {}
            Plot["xBins"] = 100
            Plot["xTitle"] = self.yTitle
            Plot["Title"] = "Data Points Summed Along the x-Axis: " + self.Filename 
            Plot["Histograms"] = [{"Title" :  t,
                                   "xData" : [k for val in list(self.Lines[t]["xData"].values()) for k in val]} 
                                   for t in self.Lines]
            Plot["Filename"] = "xProjection_" + self.Filename
            Plot["OutputDirectory"] = self.OutputDirectory + "/ProjectionPlots/" + self.Filename
            self._Hists["Projections"] = TH1FStack(**Plot) 

    def Precompiler(self):
        self.__Organize()
        tmp = []
        for i in self._Hists:
            self._Hists[i].SaveFigure()
        for i in self.Lines:
            x = TLine(**self.Lines[i])
            x.Compile()
            tmp.append(x)
        self.Lines = tmp
        self.xData = []
        self.yData = []


