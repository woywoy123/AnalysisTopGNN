# distutils: language = c++
# cython: language_level = 3
# cython: c_string_type=unicode, c_string_encoding=utf8

from cython.operator cimport dereference
from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map, pair
from libcpp cimport bool

from cyplotting cimport CyPlotting
from cytools cimport env, enc
from cyplotstruct cimport *

import numpy as np
import math

import matplotlib.pyplot as plt
import boost_histogram as bh
from typing import Union
import mplhep as hep
import os

cdef class BasePlotting:
    cdef CyPlotting* ptr
    cdef paint_t* pn
    cdef figure_t* fig
    cdef io_t* io

    cdef matpl
    cdef _ax
    cdef _fig
    cdef dict data_axis
    cdef list underlying_hists
    cdef list _labels
    cdef cummulative_hist
    cdef boosted_axis
    cdef boosted_data
    cdef axis_t x
    cdef axis_t y

    def __cinit__(self):
        self.ptr = new CyPlotting()
        self.pn = &self.ptr.painter_params
        self.io = &self.ptr.file_params
        self.fig = &self.ptr.figure_params
        self.data_axis = {}
        self.boosted_axis = {}
        self.boosted_data = {}
        self.underlying_hists = []
        self._labels = []
        self.cummulative_hist = None
        self.matpl = plt

        self.x = axis_t()
        self.y = axis_t()

        self.x.dim = b"x-axis"
        self.y.dim = b"y-axis"

        self.x.title = b"x-axis"
        self.y.title = b"y-axis"

    def __dealloc__(self): del self.ptr
    def __init__(self): pass
    cdef __atlas__(self):
        try: hep.atlas.text(loc = self.pn.atlas_loc)
        except: return
        cdef dict dic = {}
        if self.pn.atlas_data: dic["data"] = self.pn.atlas_data
        if self.pn.atlas_com > 0: dic["com"] = self.pn.atlas_com
        if self.pn.atlas_lumi > 0: dic["lumi"] = self.pn.atlas_lumi
        if self.pn.atlas_year > 0: dic["year"] = int(self.pn.atlas_year)
        if self.pn.n_events > 0: dic["label"] = "\n$N_{events}$ = " + str(self.pn.n_events)
        hep.atlas.label(**dic)
        self.matpl.style.use(hep.style.ATLAS)

    cdef __root__(self):
        self.matplt.style.use(hep.style.ROOT)

    cdef __style__(self):
        if self.pn.atlas_style: self.__atlas__()
        if self.pn.root_style: self.__root__()

    cdef __makefigure__(self):
        cdef dict com = {}
        com["figsize"] = (self.xScaling, self.yScaling)
        self._fig, self._ax = self.matpl.subplots(**com)
        self._ax.set_autoscale_on(self.autoscale)

        com = {}
        com["font.size"] = self.FontSize
        com["axes.labelsize"] = self.LabelSize
        com["legend.fontsize"] = self.LegendSize
        com["figure.titlesize"] = self.TitleSize
        com["text.usetex"] = self.LaTeX
        self.matpl.rcParams.update(com)

    cdef __resetplt__(self):
        self.matpl.close("all")
        self.matpl = plt
        self.matpl.rcdefaults()
        self.__makefigure__()

    cdef add_data(self, str name, list data):
        try: data += self.data_axis[name]
        except KeyError: pass
        self.data_axis[name] = data

    def __precompile__(self): pass
    def __compile__(self): pass
    def __postcompile__(self): pass

    def SaveFigure(self, dirc = None):
        if dirc is not None: pass
        else: dirc = env(self.io.outputdir)

        self.__precompile__()
        self.__style__()
        self.__makefigure__()

        self.__compile__()
        self._ax.set_title(self.Title)
        self.__postcompile__()

        self.matpl.xlabel(self.xTitle, size = self.LabelSize)
        self.matpl.ylabel(self.yTitle, size = self.LabelSize)

        if dirc.endswith("/"): pass
        else: dirc += "/"
        if "/" not in self.Filename: pass
        else:
            dirc = os.path.abspath(dirc + self.Filename)
            self.Filename = self.Filename.split("/")[-1]
            dirc = dirc.rstrip(self.Filename)

        try: os.makedirs(dirc)
        except FileExistsError: pass
        try:
            self.matpl.tight_layout()
            self.matpl.savefig(dirc + self.Filename, dpi = self.DPI)
            self.matpl.close("all")
        except:
            self.LaTeX = False
            self.SaveFigure()
        print("Saving Figure to: "+ dirc + self.Filename)
        self.matpl.clf()
        self.matpl.cla()
        self.matpl.close()

    @property
    def OutputDirectory(self): return env(self.io.outputdir)

    @OutputDirectory.setter
    def OutputDirectory(self, str val): self.io.outputdir = enc(val)

    @property
    def Filename(self): return env(self.io.filename)
    @Filename.setter
    def Filename(self, val):
        if val.endswith(".png"): pass
        else: val += ".png"
        self.io.filename = enc(val)

    @property
    def DPI(self): return self.io.dpi
    @DPI.setter
    def DPI(self, val): self.io.dpi = val

    @property
    def FontSize(self): return self.pn.font_size
    @FontSize.setter
    def FontSize(self, val): self.pn.font_size = val

    @property
    def LabelSize(self): return self.pn.label_size
    @LabelSize.setter
    def LabelSize(self, val): self.pn.label_size = val

    @property
    def LaTeX(self): return self.pn.latex
    @LaTeX.setter
    def LaTeX(self, val): self.pn.latex = val

    @property
    def TitleSize(self): return self.pn.title_size
    @TitleSize.setter
    def TitleSize(self, val): self.pn.title_size = val

    @property
    def LegendSize(self): return self.pn.legend_size
    @LegendSize.setter
    def LegendSize(self, val): self.pn.legend_size = val

    @property
    def LegendLoc(self): return env(self.pn.legend_loc)
    @LegendLoc.setter
    def LegendLoc(self, val): self.pn.legend_loc = enc(val)


    @property
    def NEvents(self): return self.pn.n_events
    @NEvents.setter
    def NEvents(self, val):
        self.pn.n_events = -1 if val is None else val

    @property
    def xScaling(self): return self.pn.xscaling
    @xScaling.setter
    def xScaling(self, float val): self.pn.xscaling = val

    @property
    def yScaling(self): return self.pn.yscaling
    @yScaling.setter
    def yScaling(self, float val): self.pn.yscaling = val

    @property
    def Alpha(self): return self.pn.alpha
    @Alpha.setter
    def Alpha(self, float val): self.pn.alpha = val

    @property
    def LineWidth(self): return self.pn.line_width
    @LineWidth.setter
    def LineWidth(self, float val): self.pn.line_width = val


    @property
    def HistFill(self): return env(self.pn.hist_fill)
    @HistFill.setter
    def HistFill(self, str val): self.pn.hist_fill = enc(val)

    @property
    def Color(self):
        if len(self.pn.color): return env(self.pn.color)
        self.Color = next(self._ax._get_lines.prop_cycler)["color"]
        return self.Color

    @Color.setter
    def Color(self, str val): self.pn.color = enc(val)

    @property
    def Colors(self): return [env(i) for i in self.pn.colors]
    @Colors.setter
    def Colors(self, vals: Union[list, str, int]):
        cdef str i
        if isinstance(vals, list):
            for i in vals: self.pn.colors.push_back(enc(i))
        elif isinstance(vals, str): self.pn.colors.push_back(enc(vals))
        elif isinstance(vals, int):
            for _ in range(vals):
                self.Colors = next(self._ax._get_lines.prop_cycler)["color"]

    @property
    def Texture(self): return env(self.pn.texture)
    @Texture.setter
    def Texture(self, str val): self.pn.texture = enc(val)

    @property
    def Marker(self): return env(self.pn.marker)
    @Marker.setter
    def Marker(self, str val): self.pn.marker = enc(val)

    @property
    def Textures(self):
        cdef string i
        return [env(i) for i in self.pn.textures]

    @Textures.setter
    def Textures(self, list val):
        cdef str i
        self.pn.textures = [enc(i) for i in val]

    @property
    def Markers(self):
        cdef string i
        return [env(i) for i in self.pn.markers]

    @Markers.setter
    def Markers(self, list val):
        cdef str i
        self.pn.markers = [enc(i) for i in val]

    @property
    def autoscale(self): return self.pn.autoscale
    @autoscale.setter
    def autoscale(self, bool val): self.pn.autoscale = val

    @property
    def xLogarithmic(self): return self.x.logarithmic
    @xLogarithmic.setter
    def xLogarithmic(self, bool val): self.x.logarithmic = val

    @property
    def yLogarithmic(self): return self.y.logarithmic
    @yLogarithmic.setter
    def yLogarithmic(self, bool val): self.y.logarithmic = val

    @property
    def Title(self): return env(self.fig.title)
    @Title.setter
    def Title(self, val): self.fig.title = enc(val)

    @property
    def xTitle(self): return env(self.x.title)
    @xTitle.setter
    def xTitle(self, val): self.x.title = enc(val)

    @property
    def xBinCentering(self): return self.x.bin_centering
    @xBinCentering.setter
    def xBinCentering(self, bool val): self.x.bin_centering = val

    @property
    def xBins(self):
        if not self.x.bins: return None
        else: return self.x.bins

    @xBins.setter
    def xBins(self, val): self.x.bins = val

    @property
    def yTitle(self): return env(self.y.title)
    @yTitle.setter
    def yTitle(self, val): self.y.title = enc(val)


    @property
    def Style(self):
        if self.pn.atlas_style: return "ATLAS"
        if self.pn.root_style: return "ROOT"
        if self.pn.mpl_style: return "MPL"
        return None

    @Style.setter
    def Style(self, val):
        cdef str x = val.upper()
        if x == "ATLAS": self.pn.atlas_style = True
        if x == "ROOT": self.pn.root_style = True
        if x == "MPL": self.pn.mpl_style = True

    @property
    def xMin(self):
        if not self.x.set_start: return None
        else: return self.x.start

    @xMin.setter
    def xMin(self, val):
        if val is not None: self.x.start = val
        self.x.set_start = val is not None

    @property
    def xMax(self):
        if not self.x.set_end: return None
        else: return self.x.end

    @xMax.setter
    def xMax(self, val):
        if val is not None: self.x.end = val
        self.x.set_end = val is not None

    @property
    def yMin(self):
        if not self.y.set_start: return None
        else: return self.y.start

    @yMin.setter
    def yMin(self, val):
        if val is not None: self.y.start = val
        self.y.set_start = val is not None

    @property
    def yMax(self):
        if not self.y.set_end: return None
        else: return self.y.end

    @yMax.setter
    def yMax(self, val):
        if val is not None: self.y.end = val
        self.y.set_end = val is not None

    @property
    def xStep(self):
        if self.x.step: return self.x.step
        else: return None

    @xStep.setter
    def xStep(self, val): self.x.step = val

    @property
    def yStep(self):
        if self.y.step: return self.y.step
        else: return None

    @yStep.setter
    def yStep(self, val): self.y.step = val

    @property
    def xData(self):
        try: return self.data_axis["x-data"]
        except KeyError: return None

    @xData.setter
    def xData(self, inpt):
        self.add_data("x-data", inpt)

    @property
    def yData(self):
        try: return self.data_axis["y-data"]
        except KeyError: return None

    @yData.setter
    def yData(self, inpt):
        self.add_data("y-data", inpt)

    @property
    def xLabels(self):
        cdef str key
        cdef list val
        cdef dict output = {}
        for key, val in self.data_axis.items():
            if not key.startswith("x:"): continue
            output[key[2:]] = val
        return output

    @xLabels.setter
    def xLabels(self, dict val):
        cdef str key
        cdef list content
        self.fig.label_data = True
        for key, c in val.items():
            if isinstance(c, float): content = [c]
            elif isinstance(c, int): content = [key]*c
            elif isinstance(c, list): content = c
            else: self.xLabels = c; continue
            self.add_data("x:" + key, content)

    @property
    def yLabels(self):
        cdef str key
        cdef list val
        cdef dict output = {}
        for key, val in self.data_axis.items():
            if not key.startswith("y:"): continue
            output[key[2:]] = val
        return output

    @yLabels.setter
    def yLabels(self, dict val):
        cdef str key
        cdef list content
        self.fig.label_data = True
        for key, c in val.items():
            if isinstance(c, float): content = [c]
            elif isinstance(c, int): content = [key]*c
            elif isinstance(c, list): content = c
            else: self.yLabels = c; continue
            self.add_data("y:" + key, content)

    @property
    def ATLASLumi(self): return self.pn.atlas_lumi

    @ATLASLumi.setter
    def ATLASLumi(self, val: Union[None, float, int]):
        if val is None: val = 0
        self.pn.atlas_lumi = val

    @property
    def ATLASData(self): return self.pn.atlas_data

    @ATLASData.setter
    def ATLASData(self, bool val): self.pn.atlas_data = val

    @property
    def ATLASYear(self): return self.pn.atlas_year

    @ATLASYear.setter
    def ATLASYear(self, int val): self.pn.atlas_year = val

    @property
    def ATLASCom(self): return self.pn.atlas_com

    @ATLASCom.setter
    def ATLASCom(self, float val): self.pn.atlas_com = val






cdef class TH1F(BasePlotting):
    cdef bool _stack
    cdef bool _norm

    def __init__(self, **kwargs):
        self.fig.histogram = True
        cdef str key
        for key, val in kwargs.items():
            setattr(self, key, val)

    cpdef __histapply__(self):
        cdef dict _comm = {}
        _comm["H"] = []
        _comm["histtype"] = self.HistFill
        _comm["linewidth"] = self.LineWidth
        _comm["stack"] = self.Stack
        _comm["yerr"] = False
        _comm["edgecolor"] = "black"
        _comm["alpha"] = self.Alpha
        _comm["binticks"] = True
        _comm["density"] = self._norm

        l = len(self.underlying_hists)
        if self.Histogram is not None: l += 1
        if l > len(self._labels): self._labels.append("sum")

        if self.Histogram is None: pass
        else:
            _comm["H"] = [self.Histogram]
            _comm["label"] = [self._labels.pop()]
            hep.histplot(**_comm)

        if len(self.underlying_hists):
            _comm["H"] = [i.Histogram for i in self.underlying_hists]
            _comm["label"] = self._labels
            hep.histplot(**_comm)

    cpdef __makelabelaxis__(self):
        cdef list labels = list(self.xLabels)
        if self.cummulative_hist is not None: return
        self.cummulative_hist = bh.Histogram(bh.axis.StrCategory(labels))
        self.cummulative_hist.fill(bh.axis.StrCategory(sum(self.xLabels.values(), [])))

    cpdef __fixrange__(self):

        if self.xData is not None: arr = np.array(self.xData)
        elif not len(self.underlying_hists): return
        else:
            data = []
            for i in self.underlying_hists:
                if i.xData is None: continue
                data.append(np.array(i.xData))
            arr = np.concatenate(data)

        min_, max_ = self.xMin, self.xMax
        if max_ is None: self.xMax = arr.max()
        if min_ is None: self.xMin = arr.min()
        if self.xStep is not None and self.xBins is None:
            x = 0
            while x+self.xMin < self.xMax: x += self.xStep
            self.xBins = int(x/self.xStep)+1
            self.xMax = x + self.xStep
        elif self.xBins is None: self.xBins = int((self.xMax - self.xMin))

        if self.cummulative_hist is not None: return
        elif self.xData is not None: pass
        else: return

        cdef dict com = {}
        com["bins"] = self.xBins
        com["start"] = self.xMin
        com["stop"] = self.xMax
        com["underflow"] = self.UnderFlow
        com["overflow"] = self.OverFlow
        self.cummulative_hist = bh.Histogram(bh.axis.Regular(**com))
        if self.yData is None: self.cummulative_hist.fill(self.xData)
        elif len(self.yData) != len(self.xData): self.cummulative_hist.fill(self.xData)
        else: self.cummulative_hist.fill(self.xData, weight = self.yData)

    cpdef __aggregate__(self):
        cdef TH1F dist
        cdef list data = []
        cdef str x
        cdef dict k, k_all
        for dist in self.underlying_hists:
            if self.fig.label_data: data.append(dist.xLabels)
            else: data += dist.xData
        if not self.fig.label_data: self.xData = data; return
        if not len(data): return
        data.append(self.xLabels)
        k_all = {}
        for k in data:
            for x in k:
                try: k_all[x] += k[x]
                except KeyError: k_all[x] = k[x]
        self.xLabels = k_all
        k_all = {x : 0 for x in k_all}
        self.xBinCentering = True
        for dist in self.underlying_hists:
            dist.xBinCentering = True
            dist.xLabels = k_all

    def __precompile__(self):
        if not self.OverlayHists: pass
        elif not len(self.underlying_hists): pass
        else: self.__aggregate__()

        if self.xBins is not None: self.__fixrange__()
        elif self.fig.label_data: self.__makelabelaxis__()
        else: self.__fixrange__()

    cdef __inherit_compile__(self, inpt):
        if inpt is None: return
        elif not hasattr(inpt, "Histogram"): return False
        elif inpt.Histogram is None: pass
        elif issubclass(inpt.Histogram.__class__, TH1F): pass
        else: return False

        if inpt.Histogram is None: h = inpt
        else: h = inpt.Histogram

        if self.xBins is None: pass
        else: h.xBins = self.xBins

        if self.xMin is None: pass
        else: h.xMin = self.xMin

        if self.xMax is None: pass
        else: h.xMax = self.xMax
        h.__precompile__()
        return True

    def __compile__(self):
        cdef int i
        cdef TH1F hist
        self._labels = []
        if len(self.underlying_hists):
            self.Colors = len(self.underlying_hists)+1
            self.Color = self.Colors[-1]

        for i in range(len(self.underlying_hists)):
            h = self.underlying_hists[i]
            h.Color = self.Colors[i]
            self._labels += [h.Title]
            self.__inherit_compile__(h)

        self.__inherit_compile__(self.Histogram)
        if self.Histogram is None: pass
        elif not hasattr(self.Histogram, "Histogram"): pass
        else:
            self._labels += [self.Histogram.Title]
            self.Histogram = self.Histogram.Histogram

        if self.cummulative_hist is None: pass
        else: self.__histapply__()

    def __postcompile__(self):
        if self._ax is None: return
        if self.cummulative_hist is not None: pass
        else: self.__histapply__()
        self.__style__()
        self.matpl.legend(loc=self.LegendLoc)
        self.matpl.setp(
                self._ax.get_xticklabels(),
                rotation = 30,
                horizontalalignment = "right")

        if len(self.xLabels):
            self._ax.set_xticks([0.5 + i for i in range(len(self.xLabels))])
            self._ax.set_xticklabels(list(self.xLabels))

        elif self.xBins is not None:
            hist = self.cummulative_hist
            if hist is None: hist = self.underlying_hists[0].Histogram

            width = set(hist.axes.widths[0])
            if len(width): w = int(round(list(width)[0], 0))
            else: w = 0

            unit = "<unit>"
            if not self.yTitle.endswith(unit) or not w: pass
            else: self.yTitle = self.yTitle[:-len(unit)] + " / " + str(w) + " ($GeV/c^2$)"

            h = hist.axes.edges[0]

            if not self.xBinCentering: pass
            else: h = hist.axes.centers[0]


            if not self.xBinCentering: lb = h
            else:
                h  = [i for i in h]
                lb = [i-w/2 for i in h]

            if self.xStep is not None:
                x = self.xMin
                hi_, lbi_ = [], [x]
                for h_, lb_ in zip(h, lb):
                    if x > h_: continue
                    x += self.xStep
                    x = int(x*10**4)/(10**4)
                    hi_.append(h_)
                    lbi_.append(x)
                h = hi_
                lb = lbi_[:-1]

            self._ax.set_xticks(h)
            self._ax.set_xticklabels(lb)

        else: self.matpl.xticks([i for i in range(10)], range(10))
        self._ax.tick_params(axis = "x", which = "minor", bottom = False)
        if self.xLogarithmic: self.matpl.xscale("log")
        if self.yLogarithmic: self.matpl.yscale("log")

    @property
    def UnderFlow(self): return self.x.underflow
    @UnderFlow.setter
    def UnderFlow(self, val): self.x.underflow = val

    @property
    def OverFlow(self): return self.x.overflow
    @OverFlow.setter
    def OverFlow(self, val): self.x.overflow = val

    @property
    def OverlayHists(self): return self.fig.overlay
    @OverlayHists.setter
    def OverlayHists(self, bool val): self.fig.overlay = val

    @property
    def Histograms(self): return self.underlying_hists

    @Histograms.setter
    def Histograms(self, val):
        if isinstance(val, list): pass
        else: val = [val]
        self.underlying_hists = val

    @property
    def Histogram(self): return self.cummulative_hist
    @Histogram.setter
    def Histogram(self, val): self.cummulative_hist = val

    @property
    def Stack(self): return self._stack
    @Stack.setter
    def Stack(self, bool val): self._stack = val

    @property
    def Normalize(self): return self._norm

    @Normalize.setter
    def Normalize(self, bool val): self._norm = val



cdef class TH2F(BasePlotting):

    def __init__(self, **kwargs):
        self.fig.histogram = True
        cdef str key
        for key, val in kwargs.items():
            setattr(self, key, val)

    cpdef __histapply__(self):
        hep.hist2dplot(self.cummulative_hist)

    cpdef __makelabelaxis__(self):
        cdef list axes = [
                bh.axis.StrCategory(list(self.xLabels)),
                bh.axis.StrCategory(list(self.yLabels))
        ]
        cdef list data = [
                sum(list(self.xLabels.values()), []),
                sum(list(self.yLabels.values()), [])
        ]
        self.cummulative_hist = bh.Histogram(*axes)
        self.cummulative_hist.fill(*data)

    cpdef __fix_xrange__(self):
        arr = np.array(self.xData)
        min_, max_ = self.xMin, self.xMax
        if max_ is None: self.xMax = arr.max()
        if min_ is None: self.xMin = arr.min()
        if self.xStep is not None and self.xBins is None:
            x = 0
            while x+self.xMin < self.xMax: x += self.xStep
            self.xBins = int(x/self.xStep)+1
            self.xMax = x + self.xStep
        elif self.xBins is None: self.xBins = int((self.xMax - self.xMin))

        cdef dict com = {}
        com["bins"] = self.xBins
        com["start"] = self.xMin
        com["stop"] = self.xMax
        com["underflow"] = self.xUnderFlow
        com["overflow"] = self.xOverFlow
        return bh.axis.Regular(**com)

    cpdef __fix_yrange__(self):
        arr = np.array(self.yData)
        min_, max_ = self.yMin, self.yMax
        if max_ is None: self.yMax = arr.max()
        if min_ is None: self.yMin = arr.min()
        if self.yStep is not None and self.yBins is None:
            x = 0
            while x+self.yMin < self.yMax: x += self.yStep
            self.yBins = int(x/self.yStep)+1
            self.yMax = x + self.yStep
        elif self.yBins is None: self.yBins = int((self.yMax - self.yMin))

        cdef dict com = {}
        com["bins"] = self.yBins
        com["start"] = self.yMin
        com["stop"] = self.yMax
        com["underflow"] = self.yUnderFlow
        com["overflow"] = self.yOverFlow
        return bh.axis.Regular(**com)

    def __precompile__(self):
        if self.fig.label_data: self.__makelabelaxis__()
        else:
            x = self.__fix_xrange__()
            y = self.__fix_yrange__()
            self.cummulative_hist = bh.Histogram(x, y)
            self.cummulative_hist.fill(self.xData, self.yData)

    def __compile__(self):
        self.__histapply__()

    def __postcompile__(self):
        self._ax.tick_params(axis = "x", which = "minor", bottom = False)
        self._ax.tick_params(axis = "y", which = "minor", bottom = False)
        if self.xLogarithmic: self.matpl.xscale("log")
        if self.yLogarithmic: self.matpl.yscale("log")

    @property
    def yBins(self):
        if not self.y.bins: return None
        else: return self.y.bins
    @yBins.setter
    def yBins(self, val): self.y.bins = val

    @property
    def xUnderFlow(self): return self.x.underflow
    @xUnderFlow.setter
    def xUnderFlow(self, val): self.x.underflow = val

    @property
    def yUnderFlow(self): return self.y.underflow
    @yUnderFlow.setter
    def yUnderFlow(self, val): self.y.underflow = val

    @property
    def xOverFlow(self): return self.x.overflow
    @xOverFlow.setter
    def xOverFlow(self, val): self.x.overflow = val

    @property
    def yOverFlow(self): return self.y.overflow
    @yOverFlow.setter
    def yOverFlow(self, val): self.y.overflow = val



cdef class TLine(BasePlotting):

    def __init__(self, **kwargs):
        self.fig.line = True
        cdef str key
        for key, val in kwargs.items():
            setattr(self, key, val)

    cpdef __fixrange__(self):
        if self.xData is not None: arr = np.array(self.xData)
        min_, max_ = self.xMin, self.xMax
        if max_ is None: self.xMax = arr.max()
        if min_ is None: self.xMin = arr.min()

        if self.yData is not None: arr = np.array(self.yData)
        min_, max_ = self.yMin, self.yMax
        if max_ is None: self.yMax = arr.max()
        if min_ is None: self.yMin = arr.min()

    cpdef __lineapply__(self):
        cdef dict coms = {}
        coms["linestyle"] = "-"
        coms["color"] = self.Color
        coms["marker"] = self.Marker
        coms["linewidth"] = self.LineWidth
        coms["label"] = self.Title
        if self.xData is not None and not len(self.xData): pass
        elif self.yDataUp is not None and self.yDataDown is not None:
            coms["yerr"] = [self.yDataDown, self.yDataUp]
            coms["capsize"] = 3
            self.matpl.errorbar(self.xData, self.yData, **coms)
        else: self.matpl.plot(self.xData, self.yData, **coms)

    def __precompile__(self):
        cdef TLine dist
        for dist in self.underlying_hists: dist.__fixrange__()

    def __compile__(self):
        cdef TLine dist
        cdef int i

        if not len(self.underlying_hists): pass
        else:
            self.Colors = len(self.underlying_hists)+1
            self.Color = self.Colors[-1]
        for i in range(len(self.underlying_hists)):
            dist = self.underlying_hists[i]
            dist.Color = self.Colors[i]
            dist.__compile__()
        if self.xData is None: pass
        else: self.__lineapply__()

    def __postcompile__(self):
        self.__style__()
        self.matpl.legend(loc=self.LegendLoc)
        if self.xMin is None and self.xMax is None: pass
        elif self.xMin is not None: self.matpl.xlim(self.xMin)
        else: self.matpl.xlim(self.xMin, self.xMax)

        if self.yMin is None and self.yMax is None: pass
        elif self.yMin is not None: self.matpl.ylim(self.yMin)
        else: self.matpl.ylim(self.yMin, self.yMax)

        if self.xLogarithmic: self.matpl.xscale("log")
        if self.yLogarithmic: self.matpl.yscale("log")

        self._ax.tick_params(axis = "x", which = "minor", bottom = False)

    @property
    def yDataUp(self):
        try: return self.data_axis["y-data-up"]
        except KeyError: return None

    @yDataUp.setter
    def yDataUp(self, val): self.add_data("y-data-up", val)

    @property
    def yDataDown(self):
        try: return self.data_axis["y-data-down"]
        except KeyError: return None

    @yDataDown.setter
    def yDataDown(self, val): self.add_data("y-data-down", val)

    @property
    def Lines(self): return self.underlying_hists
    @Lines.setter
    def Lines(self, list val): self.underlying_hists = val
