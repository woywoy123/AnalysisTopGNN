from AnalysisG.Plotting import TH2F

def TemplateTH2F(Title, Data, f_title):
    th2 = TH2F()
    th2.Title = Title
    th2.xData = Data["Mass"]
    th2.yData = Data["PT"]
    th2.xTitle = "Z/H-Prime Mass (GeV)"
    th2.yTitle = "Transverse Momentum of Z/H-Prime (GeV)"
    th2.Filename = "ZPrimeMatrix-" + f_title
    th2.xBins = 750
    th2.yBins = 500
    th2.xMin = 0
    th2.yMin = 0
    th2.xMax = 1500
    th2.yMax = 1000
    th2.OutputDirectory = "Figures/ZPrimeMatrix"
    th2.SaveFigure()

def Plotting(x):
    TemplateTH2F("Z/H-Prime Mass-PT Matrix with no Selection - Truth Tops", x.ZMatrixTops, "TruthTops")
    TemplateTH2F("Z/H-Prime Mass-PT Matrix with no Selection - Truth Children", x.ZMatrixChildren, "TruthChildren")
    TemplateTH2F("Z/H-Prime Mass-PT Matrix with no Selection - Truth Jets", x.ZMatrixTJ, "TruthJets")
    TemplateTH2F("Z/H-Prime Mass-PT Matrix with no Selection - Jets", x.ZMatrixJ, "Jets")

