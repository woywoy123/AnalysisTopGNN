Using TH1F, TH2F and TLine
**************************

A class dedicated to plotting histograms using the `mplhep` package as a backend to format figures.
This class adds some additional features to simplify writing simple plotting code, such as bin centering. 


.. py:class:: AnalysisG.Plotting.BasePlotting

    .. py:function:: __precompile__() -> None

        A function which can be overridden and is used to perform preliminary data manipulation or histogram modifications.

    .. py:function:: __compile__() -> None

    .. py:function:: __postcompile__() -> None

    .. py:attribute:: SaveFigure(dirc) -> None

        Whether to compile the given histogram object. 
        
        :params str dirc: The output directory of the plotting.


    :ivar str OutputDirectory: The directory in which to save the figure. If the directory tree is non-existent, it will automatically be created.
    :ivar str Filename: The name given to the output `.png` file.
    :ivar int DPI: The resolution of the figure to save. 
    :ivar int FontSize: The front size to use for text on the plot.
    :ivar int LabelSize: Ajusts the label sizes on the plot.
    :ivar bool LaTeX: Whether to use the *LaTeX* engine of `MatplotLib`
    :ivar int TitleSize: Modify the title font size.
    :ivar int LegendSize:
   
        Modify the size of the legend being displayed on the plot.
        This is predominantly relevant for combining `TH1F` histograms.

    :ivar int LegendLoc: Location of the legend within the plot.
    :ivar int NEvents: Displays the number of events used to construct the histogram. 
    :ivar float xScaling:

        A scaling multiplier in the x-direction of the plot.
        This is useful when bin labels start to merge together.
    
    :ivar float yScaling:

        A scaling multiplier in the y-direction of the plot.
        This is useful when bin labels start to merge together.
    
    :ivar float Alpha: The alpha by which the color should be scaled by. 
    :ivar float LineWidth: Line width of the histogram bin lines.
    :ivar bool HistFill: Whether to fill the histograms with the color assigned or not.
    :ivar str Color: The color to assign the histogram.
    :ivar list[str] Colors:

        Expects a list of string indicating the color each histogram should be assigned.
        If none is given then colors will be automatically assigned to each histogram.

    :ivar str Texture: The filling pattern of the histogram, options are; / , \\ , | , - , + , x, o, O, ., '*', True, False
    :ivar str Marker: Line Marker.
    :ivar list[str] Textures: 
    :ivar list[str] Markers:
    :ivar bool autoscale:
    :ivar bool xLogarithmic: Whether to scale the bin content logarithmically.
    :ivar bool yLogarithmic: Whether to scale the bin content logarithmically.
    :ivar str Title: Main title of the histogram.
    :ivar str xTitle: Title to place on the x-Axis.
    :ivar bool xBinCentering: Whether to center the bins of the histogram.
    :ivar int xBins: The number of bins to construct the histogram with.
    :ivar str yTitle: Title to place on the y-Axis.
    :ivar str Style: 

        The style to use for plotting the histogram, options are:
        - "ATLAS"
        - "ROOT"
        - "MPL"

    :ivar Union[float, int] xMin: The minimum value to start the x-Axis with.
    :ivar Union[float, int] xMax: The maximum value to end the x-Axis with.
    :ivar Union[float, int] yMin: The minimum value to start the y-Axis with.
    :ivar Union[float, int] yMax: The maximum value to end the y-Axis with.
    :ivar Union[float, int] xStep: The step size of placing a label on the x-Axis, e.g. 0, 100, 200, ..., (n-1)x100.
    :ivar Union[float, int] yStep: The step size of placing a label on the y-Axis, e.g. 0, 100, 200, ..., (n-1)x100.
    :ivar Union[list, dict] xData: The data to plot on the xAxis.
    :ivar Union[list, dict] yData: The data to plot on the yAxis.
    :ivar Union[list, dict] xLabels:

        A list of string/values to place on the x-Axis for each bin. 
        The labels will be placed in the same order as given in the list.

    :ivar Union[list, dict] yLabels:

        A list of string/values to place on the y-Axis for each bin. 
        The labels will be placed in the same order as given in the list.

    :ivar float ATLASLumi: The luminosity to display on the `ATLAS` formated histograms. 
    :ivar bool ATLASData: A boolean switch to distinguish between *Simulation* and *Data*.
    :ivar int ATLASYear: The year the data/simulation was collected from.
    :ivar float ATLASCom: The *Center of Mass* used for the data/simulation.


.. py:class:: AnalysisG.Plotting.TH1F(AnalysisG.Plotting.BasePlotting):

    A simple histogram plotting class used to minimize redundant styling code.
    The class can be further adapted in a custom framework via class inheritance.

    .. py:function:: __histapply__() -> None

    .. py:function:: __makelabelaxis__() -> None

    .. py:function:: __fixrange__() -> None

    .. py:function:: __aggregate__() -> None

    .. py:function:: __precompile__() -> None

    .. py:function:: __inherit_compile__(TH1F inpt) -> None

        :param TH1F inpt: Inherit the state of the caller histogram and apply it to the input.

    .. py:function:: __compile__() -> None

    .. py:function:: __postcompile__() -> None

    :ivar TH1F Histogram: A single `TH1F` object used to plot against (useful for underlying distributions).
    :ivar list[TH1F] Histograms: Expects `TH1F` objects from which to construct the combined histogram.
    :ivar bool Stack: Whether to combine the histograms as a stack plot.


.. py:class:: AnalysisG.Plotting.TH2F(AnalysisG.Plotting.BasePlotting):

    .. py:function:: __fix_xrange__() -> None

    .. py:function:: __fix_yrange__() -> None

    :ivar int xBins: Number of bins to use on the x-Axis
    :ivar int yBins: Number of bins to use on the y-Axis
    :ivar bool xUnderFlow: Whether to reserve the last bin for data not captured on the x-Axis.
    :ivar bool xOverFlow: Whether to reserve the last bin for data not captured on the x-Axis.
    :ivar bool yUnderFlow: Whether to reserve the last bin for data not captured on the y-Axis.
    :ivar bool yOverFlow: Whether to reserve the last bin for data not captured on the y-Axis.


.. py:class:: AnalysisG.Plotting.TLine(AnalysisG.Plotting.BasePlotting):

    .. py:function:: __lineapply__() -> None

    :ivar list[float, int, ...] yDataUp: 
    :ivar list[float, int, ...] yDataDown: 


Example: A simple TH1F plot
___________________________

.. code-block:: python 

    from AnalysisG.Plotting import TH1F

    th = TH1F()
    th.xBins = 100
    th.xMax = 100
    th.xMin = 0
    th.xData = [i for i in range(100)]
    th.Title = "some title"
    th.xTitle = "x-Axis"
    th.yTitle = "y-Axis"
    th.Filename = "some-name"
    th.OutputDirectory = "./Some/Path/"
    th.SaveFigure()


Example: A TH1F plot with bin centering 
_______________________________________

.. code-block:: python 

    from AnalysisG.Plotting import TH1F

    th = TH1F()
    th.xMin = 0
    th.xStep = 20
    #th.xMax = 100 <- dont include a maximum
    th.xBins = 100 # <- rather define the number of bins
    th.xBinCentering = True
    th.xData = [i for i in range(100)]
    th.Title = "some title"
    th.xTitle = "x-Axis"
    th.yTitle = "y-Axis"
    th.Filename = "some-name"
    th.OutputDirectory = "./Some/Path/"
    th.SaveFigure()

Example: Combining two or more TH1F plots 
_________________________________________

.. code-block:: python 

    from AnalysisG.Plotting import TH1F

    # Define the settings to apply to all histograms
    th = TH1F()
    th.xMin = 0
    th.xStep = 20
    th.xMax = 100
    th.Title = "some title"
    th.xTitle = "x-Axis"
    th.yTitle = "y-Axis"
    th.Filename = "some-name"
    th.OutputDirectory = "./Some/Path/"

    # Iterate over your data
    for i in MyDataDictionary:

        # Create a new TH1F instance
        th_ = TH1F()
        th_.Title = i

        # Populate this instance with some data
        th_.xData = MyDataDictionary[i]

        # Append the instance to the Histograms attribute
        th.Histograms.append(th_)

    th.SaveFigure()


    # To make the above code shorter, we can create a dictionary
    # of commands e.g. 
    tmp = {"xMin" : 0, "xStep" : 20, ... , "Histograms" : []}

    # and then do the same loop over the data, but populate the Histograms 
    # key in the tmp dictionary 

    for i in MyDataDictionary:
        tmp2 = {"xData" : MyDataDictionary[i], "Title" : i}
        tmp["Histograms"].append(TH1F(**tmp2))

    th = TH1F(**tmp)
    th.SaveFigure()


Example: A Simple TH2F Plot
___________________________

.. code-block:: python 

    from AnalysisG.Plotting import TH2F

    th2 = TH2F()
    th2.Title = "Some distribution plot"
    th2.xTitle = "x-Title"
    th2.yTitle = "y-Title"

    th2.xMin = 0
    th2.yMin = 0

    th2.xMax = 100
    th2.yMax = 100

    th2.xBins = 100
    th2.yBins = 100

    th2.xData = [i for i in range(100)]
    th2.yData = [i for i in range(100)]
    th2.Filename = "Some_File"
    th2.OutputDirectory = "./some/path"
    th2.SaveFigure()

