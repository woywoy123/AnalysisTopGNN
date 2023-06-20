from conftest import clean_dir


def test_th1f():
    from AnalysisG.Plotting import TH1F

    t = TH1F()
    t.LaTeX = False
    t.xData = [1, 1, 2, 3, 3, 5]
    t.xBinCentering = True
    t.xMin = 0
    t.xMax = 6
    t.xBins = 6
    t.Filename = "th1f"
    t.SaveFigure()

    clean_dir()


def test_th2f():
    from AnalysisG.Plotting import TH2F

    t = TH2F()
    t.LaTeX = False
    t.xData = [1, 2, 3, 4, 5]
    t.yData = [1, 2, 3, 4, 5]
    t.Filename = "th2f"
    t.SaveFigure()

    clean_dir()


def test_th1Combine():
    from AnalysisG.Plotting import TH1F, CombineTH1F

    t1 = TH1F()
    t1.LaTeX = False
    t1.xData = [1, 1, 2, 3, 3, 5]
    t1.Title = "hello"
    t1.xBinCentering = True
    t1.xBins = 6

    t2 = TH1F()
    t2.LaTeX = False
    t2.xData = [1, 1, 1, 1, 2, 3, 3, 5]
    t2.Title = "world"
    t2.xBinCentering = True
    t2.xBins = 6

    TH = CombineTH1F()
    TH.LaTeX = False
    TH.Histograms = [t1, t2]
    TH.xMin = 0
    TH.xMax = 6
    TH.xBinCentering = True
    TH.Filename = "Combined"
    TH.SaveFigure()

    clean_dir()


def test_tline():
    from AnalysisG.Plotting import TLine

    t = TLine()
    t.LaTeX = False
    t.xData = [1, 2, 3, 4, 5, 6]
    t.yData = [1, 2, 3, 4, 5, 6]
    t.Filename = "tline"
    t.SaveFigure()

    t = TLine()
    t.LaTeX = False
    t.xData = [[i * k for i in range(10)] for k in range(10)]
    t.yData = [[i * k for i in range(10)] for k in range(10)]
    t.DoStatistics = True
    t.Filename = "tline-stats"
    t.Title = "hello"
    t.SaveFigure()

    clean_dir()


def test_tlineCombine():
    from AnalysisG.Plotting import TLine, CombineTLine

    tc = CombineTLine()
    tc.LaTeX = False
    tc.Title = "test-Combine"
    tc.MakeStatisticHistograms = True
    for i in range(10):
        t = TLine()
        t.xData = [k + 1 for k in range(10)]
        t.yData = [k + i for k in range(10)]
        t.Title = str(i + 1)
        tc.Lines.append(t)
    tc.Filename = "combiend"
    tc.SaveFigure()

    clean_dir()


if __name__ == "__main__":
    test_th1f()
    test_th2f()
    test_th1Combine()
    test_tline()
    test_tlineCombine()
    pass
