import warnings

warnings.filterwarnings("ignore")
from AnalysisG.Tools import Tools
from AnalysisG.Notification import _Plotting
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("agg")
import mplhep as hep
import math
import random


class BaseFunctions(Tools, _Plotting):
    def __init__(self):
        pass

    def DefineStyle(self):
        if self.Style == "ATLAS":
            hep.atlas.text(loc=2)
            hep.atlas.label(
                data=self.ATLASData,
                year=self.ATLASYear,
                lumi=round(self.ATLASLumi, 4),
                label="\n$N_{events}$ = "
                + str(len(self.xData) if self.NEvents == None else self.NEvents),
                com=self.ATLASCom,
            )
            self.PLT.style.use(hep.style.ATLAS)
        if self.Style == "ROOT":
            self.PLT.style.use(hep.style.ROOT)

    def MakeFigure(self):
        self.Figure, self.Axis = plt.subplots(
            figsize=(self.xScaling * 6.4, self.yScaling * 4.8)
        )
        self.Axis.set_autoscale_on(True)

    def ApplyToPLT(self):
        self.PLT.rcParams.update(
            {
                "font.size": self.FontSize,
                "axes.labelsize": self.LabelSize,
                "legend.fontsize": self.LegendSize,
                "figure.titlesize": self.TitleSize,
            }
        )
        self.PLT.rcParams["text.usetex"] = self.LaTeX

    def ResetPLT(self):
        plt.close("all")
        self.PLT = plt
        self.PLT.rcdefaults()
        self.MakeFigure()

    def DefineAxisData(self, Dim, JustData=False):
        self.Set(Dim + "Data", [])
        if JustData:
            return
        self.Set(Dim + "Min", None)
        self.Set(Dim + "Max", None)
        self.Set(Dim + "Weights", None)
        self.Set(Dim + "Title", None)
        self.Set(Dim + "TickLabels", None)

    def ApplyInput(self, args):
        for key, val in args.items():
            if self.InvalidVariableKey(key):
                continue
            self.__dict__[key] = val

    def Get(self, var):
        return self.__dict__[var]

    def Set(self, var, val):
        self.__dict__[var] = val

    def DumpDict(self, Varname=None):
        out = {}
        for i in self.__dict__:
            if i in ["PLT", "Figure", "Axis"]:
                continue
            obj = []
            if isinstance(self.__dict__[i], list):
                obj = {
                    hex(id(k)): k.DumpDict(i)
                    for k in self.__dict__[i]
                    if "AnalysisG" in type(k).__module__
                }
            if len(obj) == 0:
                out[i] = self.__dict__[i]
            else:
                out["Rebuild"] = obj
        out["_ID"] = hex(id(self))
        out["_TYPE"] = type(self).__name__
        if Varname != None:
            out["_Varname"] = Varname
        return out

    def SanitizeData(self, var):
        out = []
        for i in range(len(var)):
            if var[i] == None:
                continue
            if math.isinf(var[i]):
                continue
            if math.isnan(var[i]):
                continue
            out.append(var[i])
        return out

    def DefineCommonRange(self, Dims):
        x = self.SanitizeData(self.Get(Dims + "Data"))
        if len(x) == 0:
            self.Title = str(self.Title) if self.Title == None else self.Title
            if self.Get(Dims + "Weights") == None:
                self.NoDataGiven()
            elif len(self.Get(Dims + "Weights")) == 0:
                self.NoDataGiven()
            return
        self.Set(Dims + "Data", x)

        if self.Get(Dims + "Min") == None:
            self.Set(Dims + "Min", min(self.Get(Dims + "Data")))
        if self.Get(Dims + "Max") == None:
            self.Set(Dims + "Max", max(self.Get(Dims + "Data")))

    def ApplyRandomColor(self, obj):
        color = next(self.Axis._get_lines.prop_cycler)["color"]
        if obj.Color == None:
            obj.Color = color
            self.Colors.append(color)
        elif obj.Color in self.Colors:
            obj.Color = None
            self.ApplyRandomColor(obj)
            return

    def Precompiler(self):
        pass

    def SaveFigure(self, Dir=None):
        self.Precompiler()
        if Dir == None:
            Dir = self.OutputDirectory
        Dir = self.AddTrailing(Dir, "/")
        self.Filename = self.AddTrailing(self.Filename, ".png")
        self.mkdir(Dir)
        self.Compile()

        self.Axis.set_title(self.Title)
        self.PLT.xlabel(self.xTitle, size=self.LabelSize)
        self.PLT.ylabel(self.yTitle, size=self.LabelSize)

        self.PLT.tight_layout()
        self.PLT.savefig(Dir + "/" + self.Filename, dpi=self.DPI)
        self.PLT.close("all")

        self.SavingFigure(Dir + self.Filename)
