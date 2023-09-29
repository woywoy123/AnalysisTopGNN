Plotting (TH1F, TH2F, CombineTH1F)
**********************************

A class dedicated to plotting histograms using the `mplhep` package as a backend to format figures.
This class adds some additional features to simplify writing simple plotting code, such as bin centering. 

Attributes (Cosmetics) 
______________________

- ``Title``: 
  Title of the histogram to generate.

- ``Style``:
  The style to use for plotting the histogram, options are; `ATLAS`, `ROOT` or `None`

- ``ATLASData``:
  A boolean switch to distinguish between *Simulation* and *Data*.

- ``ATLASYear``:
  The year the data/simulation was collected from.

- ``ATLASCom``:
  The *Center of Mass* used for the data/simulation.

- ``ATLASLumi``:
  The luminosity to display on the `ATLAS` formated histograms. 

- ``NEvents``:
  Displays the number of events used to construct the histogram. 

- ``Color``:
  The color to assign the histogram.

- ``FontSize``:
  The front size to use for text on the plot.

- ``LabelSize``:
  Ajusts the label sizes on the plot.

- ``TitleSize``:
  Modify the title font size.

- ``LegendSize``:
  Modify the size of the legend being displayed on the plot.
  This is predominantly relevant for combining `TH1F` histograms.

- ``xScaling``:
  A scaling multiplier in the x-direction of the plot.
  This is useful when bin labels start to merge together.

- ``yScaling``:
  A scaling multiplier in the y-direction of the plot.
  This is useful when bin labels start to merge together.

Attributes (IO)
_______________

- ``Filename``: 
  The name given to the output `.png` file.

- ``OutputDirectory``: 
  The directory in which to save the figure. 
  If the directory tree is non-existent, it will automatically be created.

- ``DPI``:
  The resolution of the figure to save. 

Attributes (Axis)
_________________

- ``xTitle``: 
  Title to place on the x-Axis.

- ``yTitle``: 
  Title to place on the y-Axis.

- ``xMin``: 
  The minimum value to start the x-Axis with.

- ``xMax``:
  The maximum value to end the x-Axis with.

- ``yMin``: 
  The minimum value to start the y-Axis with.

- ``yMax``:
  The maximum value to end the y-Axis with.

- ``xTickLabels``:
  A list of string/values to place on the x-Axis for each bin. 
  The labels will be placed in the same order as given in the list.

- ``Logarithmic``:
  Whether to scale the bin content logarithmically.

- ``Histograms``:
  Expects `TH1F` objects from which to construct the combined histogram.

- ``Colors``:
  Expects a list of string indicating the color each histogram should be assigned.
  The `CombineTH1F` automatically adjusts the color if a color has been assigned to another histogram.

- ``Alpha``:
  The alpha by which the color should be scaled by. 

- ``FillHist``:
  Whether to fill the histograms with the color assigned or not.

- ``Texture``:
  The filling pattern of the histogram, options are; 
    `/ , \\ , | , - , + , x, o, O, ., *, True, False`

- ``Stack``:
  Whether to combine the histograms as a stack plot.

- ``Histogram``:
  A single `TH1F` object to which other `Histograms` are plotted against. 

- ``LaTeX``:
  Whether to use the *LaTeX* engine of `MatplotLib`

Attributes (Bins)
_________________

- ``xBins``:
  The number of bins to construct the histogram with.

- ``xBinCentering``:
  Whether to center the bins of the histograms. 
  This can be relevant for classification plots.

- ``xStep``:
  The step size of placing a label on the x-Axis, e.g. 0, 100, 200, ..., (n-1)x100.

- ``yStep``:
  The step size of placing a label on the y-Axis, e.g. 0, 100, 200, ..., (n-1)x100.

Attributes (Data)
_________________

- ``xData``:
  The data from which to construct the histogram. 
  If this is to be used with `xTickLabels`, make sure the bin numbers are mapped to the input list.
    For example; `xData = [0, 1, 2, 3, 4]  -> xTickLabels = ["b1", "b2", "b3", "b4", "b5"]`

- ``xWeights``:
  Weights to be used to scale the bin content. 
  This is particularly useful for using `xTickLabels`.

- ``Normalize``:
  Whether to normalize the data. Options are; `%`, `True` or `False`.

- ``IncludeOverflow``:
  Whether to dedicate the last bin in the histogram for values beyond the specified maximum range.

Functions (IO)
______________
 
- ``DumpDict(varname = None)``:
  Dumps a dictionary representation of the settings.
 
- ``Precompiler()``:
  A function which can be overridden and is used to perform preliminary data manipulation or histogram modifications.
 
- ``SaveFigure(Dir = None)``:
  Whether to compile the given histogram object. 
  `Dir` is a variable used to indicate the output directory. 

Functions (Cosmetics)
_____________________

- ``ApplyRandomColor(obj)``:
  Selects a random color for the histograms.

- ``ApplyRandomTexture(obj)``:
  Selects a random texture for the histograms.

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

    from AnalysisG.Plotting import TH1F, CombineTH1F

    # Define the settings to apply to all histograms
    th = CombineTH1F()
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

    th = CombineTH1F(**tmp)
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

