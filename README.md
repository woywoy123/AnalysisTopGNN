# A Graph Neural Network Framework for High Energy Particle Physics
[![AnalysisTopGNN-Building-Action](https://github.com/woywoy123/AnalysisTopGNN/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/woywoy123/AnalysisTopGNN/actions/workflows/python-app.yml)

## Introduction <a name="introduction"></a>
The aim of this package is to provide Particle Physicists with an intuitive interface to **Graph Neural Networks**, whilst remaining Analysis agnostic. 
Following a similar spirit to AnalysisTop, the physicist defines a custom event class and matches variables within ROOT files to objects that they are a representation of.
A simple example of this would be a particle, since these generally have some defining properties such as the four vector, mass, type, etc. 

From a technical point of view, the particle would be represented by some Python object, where attributes are matched to the ROOT leaf strings, such that framework can identify how variables are matched. 
A similar approach can be taken to construct event objects, where particle objects live within the event and are matched accordingly to any other particles e.g. particle truth matching. 
This hierarchical architecture allows for complex event definitions, first basic building blocks are defined and then matched according to some rule (see tutorial below).

To streamline the transition between ROOT and PyTorch Geometric (a Deep Learning framework for Graph Neural Networks), the framework utilizes event graph definitions.
These simply define which particles should be used to construct nodes on a PyTorch Geometric (PyG) Data object. Edge, Node and Graph features can be added separately as simple python functions (see tutorial below).
Post event graph construction, events are delegated to an optimization step, which trains a specified model with those graphs. 

To avoid having to deal with additional boiler plate book keeping code, the framework tracks the event to the originating ROOT file using MD5 hashing. 
The MD5 hash is constructed by concatenating the directory, ROOT filename and event number into a single string and computing the associated hash. 
This ensures each event can be easily traced back to its original ROOT file. 


## Supported Monte Carlo Generators <a name="Generators"></a>
The framework was originally designed for samples produced via AnalysisTop, however the architecture has been tested on MadGraph5+Delphes ROOT samples and requires no additional extensions.

## Getting Started <a name="GettingStarted"></a>
1. First clone this repository:
```
git clone https://github.com/woywoy123/AnalysisTopGNN.git
```
2. Nagivate to setup-scripts and choose whether to use Conda or PyVenv, and open the script. 
```bash 
cd ./AnalysisTopGNN/setup-scripts
```
3. Open the selected installer in your desired text editor and adjust the environment parameters according to your environment.
By default the following settings are assumed. 
```bash 
CUDA_PATH=/usr/local/cuda-11.8 # Defines the cuda path 
VERSION=cu118 # The version to use for cuda. If set to 'cpu', cuda will be disabled 
TORCH=1.13.0  # Version of torch to install
MAX_JOBS=12   # Number of threads to use for compilation
CC=gcc-11     # GCC compiler version, see https://stackoverflow.com/questions/6622454/cuda-incompatible-with-my-gcc-version
CXX=g++-11
```

## How Do I Make This Code Work With My Samples? <a name="CustomSamples"></a>

### There are three steps involved:
1. Define **Particles** in your ROOT samples as Python Classes, and assign the associated leaf string to each particle attribute.
2. Define the **Event** and include any particles that constitute the event. 
Trees and Branches specify from where the particles should pull the leaf strings. 
For instance, if ROOT samples contain multiple trees with identical data structures, specifying the tree would instruct the framework to construct particle objects from that tree. 
Similar to the particle class, event attributes can be added by matching the associated leaf string. 
If the event needs additional tweaking, e.g. particle matching, the **CompileEvent** method provides additional space to script the matching instructions. 
3. Define the **EventGraph**. Here the Physicist specifies the particles to use for the Event Graph nodes.

A few simple/complex examples can be found under; 
```bash 
src/EventTemplates/Particles/Particles.py
src/EventTemplates/Events/Event.py
src/EventTemplates/Events/EventGraphs.py
```

### Tutorial (A Step by Step Guide):
- First create a new analysis directory `AnalysisName` or simply navigate to `cd tutorial` within this repository.
- Create three empty files; `Particles.py`, `Event.py`, `EventGraph.py`, we will edit these one by one. 

#### Defining A Particle Class (`Particles.py`): <a name="CustomParticleClass"></a>
This section aims to illustrate a very simple example of how to create a custom particle, which the framework can use to construct the particle.
1. Open ``Particles.py`` and place the following line on the top
```python 
from AnalysisTopGNN.Templates import ParticleTemplate
```
2. Let our custom particle class inherit functions from the template class, a simple example should look something like this:
```python 
class CustomParticle(ParticleTemplate): # <--- Inherit functions from ParticleTemplate
	def __init__(self):
                # initialize internal variables, Children, Parent, index
		ParticleTemplate.__init__(self) 
                
		self.Type = "Particle" # <--- Optional
		self.pt = self.Type + ".PT"
                self.eta = "Particle.ETA" # <--- A name within the ROOT file's leaf
                #... <Some Other Desired Particle Properties> ...
```

In the above example, the framework is expecting the ROOT file to contain particle leaves for `Particle.PT` and `Particle.ETA`. 
However, after the object has been constructed, these attributes can be simply called via `<some particle>.pt` or `<some particle>.eta`.
If during the construction step, that is, when the framework scans ROOT files, notices missing leaf keys, a warning will be issued and corresponding attribute is skipped.

#### Attributes and Functions:
The **ParticleTemplate** class comes with numerous useful functions that can be overridden, if needed. 
A full list is given below:
- `px -> float`: 
Computes the `x` component of a Cartesian momentum vector (requires `pt` and `phi`).
- `py -> float`: 
Computes the `y` component of a Cartesian momentum vector (requires `pt` and `phi`).
- `pz -> float`: 
Computes the `z` component of a Cartesian momentum vector (requires `pt` and `eta`).
- `eta -> float`: 
Computes the pseudorapidity (requires `px`, `py` and `pz`).
- `phi -> float`: 
Computes the polar angle around the beam pipe (requires `px` and `py`).
- `pt -> float`: 
Computes the transverse momentum (requires `px` and `py`).
- `e -> float` : 
Computes the particle's energy from given kinematics. If `m` is given, the energy is computed using the Energy-Momentum relation.
- `Mass -> float`: 
Computes the particle's invariant mass (requires `px`, `py`, `pz` and `e`). The output will be in the same units as the four vectors.
- `DeltaR(particle) -> float`: 
Computes the DeltaR between two particles from `eta` and `phi`. 
- `is_lep -> boolean`: 
True if the pdgid is consistent with a lepton (requires `pdgid` as integer).
- `is_nu -> boolean`: 
True if the pdgid is consistent with a neutrino (requires `pdgid` as integer).
- `is_b -> boolean`: 
True if the pdgid is consistent with a b-quark (requires `pdgid` as integer).
- `is_add -> boolean`: 
True if the particle is neither a lepton, neutrino or b-quark (requires `pdgid` as integer).
- `LeptonicDecay -> boolean`: 
True if the particle's decay products are leptonic (requires `Children` to have particle objects with `pdgid`).
- `Children -> list`: 
A list which links decay products for the particle.
- `Parent -> list`: 

#### Magic Functions:
```python
# Summation 
p = sum([p for p in SomeParticleList])
p = sum(SomeParticleList)
p = p1 + p2 + ... + pn

# Prints the particle's attributes including its children.
print(p)

# Equivalence 
same = p1 == p2
diff = p1 != p2
contains = i in SomeParticleList	
```


#### How to define a Custom Event Class (`Event.py`): <a name="CustomEventClass"></a>
#### Basic Example:
1. Open `Event.py` and place the following lines at the top; 
```python
from AnalysisTopGNN.Templates import EventTemplate 
from Particles import CustomParticle # <--- The example particle class implemented above
```
2. Similar to the Particle class, let the custom event inherit methods from **EventTemplate**. 
A simple example should look something like this:
```python  
class CustomEvent(EventTemplate):
	def __init__(self):
		EventTemplate.__init__(self)
		
		self.Type = "Event"
		self.runNumber = self.Type + ".Number" # <--- Example event leaf variable

                # Specify the trees you want to use for each event.
                self.Tree = ["nominal", "..."] 

                # If there are any relevant branches add these as well.
		self.Branches = ["Particle"] 

                # Add particles/additional objects constituting the event
		self.Objects = {
			"ArbitraryParticleName" : CustomParticle()
				}
	
                # Event luminosity which is used for computing the 
                # integrated luminosity for a sum of events.
		self.Lumi = 0 

		# Define all the attributes above this function.
		self.DefineObjects()
	
	def CompileEvent(self): 
		# Particle names defined in self.Objects will appear 
                # in this code segment as self.<Some Random Name>. 
                # For example; 
		print(self.ArbitraryParticleName)
                # returns a dictionary of particles in the event.
                
                # Some function to convert a dictionary to a list
		self.ArbitraryParticleName = self.DictToList(self.ArbitraryParticleName)
		
		# ... <Some Compiler Logic - Particle Matching etc.>

```

#### The ``self.Objects`` attribute:

```python 
self.Objects = {
	"CustomParticleV1" : CustomParticleV1(), 
	"CustomParticleV2" : CustomParticleV2()
		}
```

During event generation, the framework expects the attribute **Objects** to be a dictionary.
This defines the particles needed to construct the event and serve as templates, which are duplicated as many times as there are entries in the ROOT file leaf.
For instance, if the ROOT leaf contains 3 `CustomParticle` at event index `i`, then the template will be duplicated 3 times and populated with the associated leaf values.

Keys within the dictionary will be added as attributes to the event object, for instance if `CustomParticleV1` and `CustomParticleV2` are keys in the dictionary, the event will have attributes `self.CustomParticleV1` and `self.CustomParticleV2`, respectively. 
The names given to the keys do not need to match the particle class names, for example if `CustomParticleV1` was replaced with `ParticleV1`, the particles within the `self.ParticleV1` attribute will still be `CustomParticleV1` objects.

#### The **CompileEvent** Method:
This method is used to define any particle relationships or perform pre-processing of the event.
It is not intended to be used for event selection or cuts, but rather a space to organize and link objects together.
For instance, if the given ROOT files contain some mapping between particles then, this section of the implementation allows the Physicist to match the particle's parents/children.

### Attributes and Functions:
The **EventTemplate** class comes with a few pre-set attributes, which can be modified as needed, these are given below:
- `Trees -> list`: 
A list of trees to use for constructing the event. If this list is left empty, then the framework defaults to `Branches`. 
- `Branches -> list`: 
A list of branches to scan through and construct objects from within the given `Tree`.
- `Lumi -> (default: 0) float`: 
The luminosity contribution of the event. 
- `_Deprecated -> boolean`: 
A book-keeping variable used to indicate whether the event implementation is old or outdated. 
- `_CommitHash -> str`: 
A book-keeping variable used to specify which commit of `AnalysisTop` was used to produce the ROOT sample.
This can be useful when needing to reference which commit this implementation is compatible with.
- `CompileEvent -> None`: 
An empty function, which can be overridden to include additional linking to particle objects. 


### How to define a Custom Event Graph Class (`EventGraphs.py`): <a name="CustomEventGraphClass"></a>
#### Basic Example:
1. Open `EventGraphs.py` and place the following line at the top; 
```python
from AnalysisTopGNN.Templates import EventGraphTemplate 
```
2. Similar to the Particle class, let the custom Event Graph class inherit methods from `EventGraphTemplate`.
3. A simple example should look something like this:
```python 
def CustomEventGraph(EventGraphTemplate):
	def __init__(self, Event):
		EventGraphTemplate.__init__(self)

                # Adds the event to the graph (needed for Graph Level Attributes).
		self.Event = Event 
                
                # Select particles relevant for the analysis. 
		self.Particles += <Event.SomeParticles> 
```

## The Analysis Class: 
This is the main interface of the package, it is used to configure the **Event/EventGraph** constructors, including **Graph Neural Network** training and many other things, which will be shown as an example.

### A Minimal Example:
To get started, create a new python file `<SomeName>.py` and open it.
At the top, add the following line: 
```python 
from AnalysisTopGNN import Analysis
from SomeEventImplementation import CustomEvent
```
Now instantiate the class and specify the analysis parameters.
A simple example could look like this; 
```python 
Ana = Analysis()
Ana.ProjectName = "Example"
Ana.InputSample(<name of sample>, "/some/sample/directory")
Ana.Event = CustomEvent
Ana.EventCache = True
Ana.Launch()

for event in Ana:
	print(event)
``` 

### Attributes and Functions:
#### Attributes
- `VerboseLevel`: 
An integer which increases the verbosity of the framework, with 3 being the highest and 0 the lowest.
- `Threads`: 
The number of CPU threads to use for running the framework. 
- `chnk`: 
An integer which regulates the number of entries to process for each given core. 
This is particularly relevant when constructing events, as to avoid memory issues. 
As an example, if Threads is set to 2 and `chnk` is set to 10, then 10 events will be processed per core. 
- `Tree`: 
The tree the analysis should process. If set to `None`, all trees will be considered.
- `EventStart`: 
The event to start from given a set of ROOT samples. Useful for debugging specific events.
- `EventStop`: 
The number of events to generate. 
- `ProjectName`: 
Specifies the output folder of the analysis. If the folder is non-existent, a folder will be created.
- `OutputDirectory`: 
Specifies the output directory of the analysis. This is useful if the output needs to be placed outside of the working directory.
- `Event`: 
Specifies the event implementation to use for constructing the Event objects from ROOT Files.
- `EventGraph`:
Specifies the event graph implementation to use for constructing graphs.
- `SelfLoop`:
Given an event graph implementation, add edges to particle nodes which connect to themselves.
- `FullyConnect`:
Given an event graph implementation, create a fully connected graph.
- `TrainingSampleName`: 
Generate and save a list of events, with the given name, which should be assigned the to training.
- `TrainingPercentage`:
Assign some percentage to training and reserve the remaining for testing.
- `SplitSampleByNode`:
Sort event graphs by the number of nodes. This might be required if the given model is not immune to varying number of nodes.
- `kFolds`:
Number of folds to use for training 
- `BatchSize`:
How many Event Graphs to group into a single graph.
- `Model`:
The model to be trained, more on this later.
- `DebugMode`:
Increases the verbosity during training. This can be set to; "loss", "accuracy", "compare" (compare prediction to truth) or a combination of these e.g. "loss-accuracy".
- `ContinueTraining`:
Whether to continue the training from the last known checkpoint (after each epoch).
- `Optimizer`:
Takes as input a nested dictionary, where the first key specifies the minimizer and the subsequent dictionary the parameters. 
Current choices are; `SGD` - Stochastic Gradient Descent and `ADAM`.
- `Scheduler`: 
Takes as input a nested dictionary, where the first key specifies the scheduler for modulating the learning rate. Options are; `ExponentialLR` and `CyclicLR`. 
- `Device`: 
The device used to run `PyTorch` training on. This also applies to where to store graphs during compilation.
- `EventCache`: 
Specifies whether to generate a cache after constructing `Event` objects. If this is enabled without specifying a `ProjectName`, a folder called `UNTITLED` is generated.
- `DataCache`:
specifies whether to generate a cache after constructing graph objects. If this is enabled without having an event cache, the `Event` attribute needs to be set. 
- `FeatureTest`: 
A parameter mostly concerning graph generation. It checks whether the supplied features are compatible with the `Event` python object. 
If any of the features fail, an alert is issued. 
- `DumpHDF5`: 
Specifies whether to save constructed events/graphs into HDF5 containers. 
For `Event` objects, this is rather slow but very fast for graphs
- `DumpPickle`: 
Specifies whether to save constructed events/graphs as pickle files.
This is a much faster alternative to HDF5, however it requires the original implementation of the Event to be supplied. 

#### Default Parameters:
| **Attribute**        | **Default Value** | **Expected Type** |                    **Examples** |
|:---------------------|:-----------------:|:-----------------:|:-------------------------------:|
| VerboseLevel         |                 3 |             `int` |                                 | 
| Threads              |                12 |             `int` |                                 |
| chnk                 |                12 |             `int` |                                 |
| Tree                 |              None |             `str` |                                 |
| EventStart           |                 0 |             `int` |                                 |
| EventStop            |              None |             `int` |                                 |
| ProjectName          |          UNTITLED |             `str` |                                 |
| OutputDirectory      |                ./ |             `str` |                                 |
| Event                |              None |       EventObject |                                 |
| EventGraph           |              None |  EventGraphObject |                                 |
| SelfLoop             |              True |            `bool` |                                 |
| FullyConnect         |              True |            `bool` |                                 |
| TrainingSampleName   |             False |             `str` |                                 |
| TrainingPercentage   |                80 |             `int` |                                 |
| SplitSampleByNode    |             False |            `bool` |                                 |
| kFolds               |                10 |             `int` |                                 |
| BatchSize            |                10 |             `int` |                                 |
| Model                |              None |          GNNModel |                                 |
| DebugMode            |             False |             `str` | `loss`, `accuracy`, `compare`   |
| ContinueTraining     |             False |            `bool` |                                 |
| RunName              |          UNTITLED |             `str` |                                 |
| Epochs               |                10 |             `int` |                                 |
| Optimizer            |              None |            `dict` |      `{"ADAM" : {"lr" : 0.001}` |
| Scheduler            |              None |            `dict` |                                 |
| Device               |               cpu |            `str`  |			`cuda`   |
| EventCache           |             False |            `bool` |                                 |
| DataCache            |             False |            `bool` |                                 |
| FeatureTest          |             False |            `bool` |                                 |
| DumpHDF5             |             False |            `bool` |                                 |
| DumpPickle           |             False |            `bool` |                                 |

#### Functions:
```python 
def InputSample(Name, SampleDirectory)
```
This function is used to specify the directory or sample to use for the analysis. 
The `Name` parameter expects a string, which assigns a name to `SampleDirectory` and is used for book-keeping. 
`SampleDirectory` can be either a string, which directory points to the ROOT file or a nested dictionary with keys representing the path and values being either a string or list of ROOT files. 
```python 
def AddSelection(Name, inpt)
``` 
The `Name` parameter specifies the name of the selection criteria, for instance, `MyAwesomeSelection`. 
The `inpt` specifies the `Selection` implementation to use, more on this later. 
```python 
def MergeSelection(Name)
```
This function allows for post selection output to be merged into a single pickle file. 
During the execution of the `Selection` implementation, multiple threads are spawned, which individually save the output of each event selection, meaning a lot of files being written and making it less ideal for inspecting the data.
Merging combines all the internal data into one single file and deletes files being merged. 

```python 
def Launch()
```
Launches the Analysis with the specified parameters.

```python 
def DumpSettings(): 
``` 
Returns a directory of the settings used to configure the `Analysis` object. 
```python 
def RestoreSettings(inpt):
```
Expects a dictionary of parameters used to configure the object.
```python 
def ExportAnalysisScript():
```
Returns a list of strings representing the configuration of the object.

#### Magic Functions:
```python 
# Iteration
[i for i in Analysis]

# Length operator
len(Analysis)

# Summation operator 
Analysis3 = Analysis1 + Analysis2
AnalysisSum = [Analysis1, Analysis2, ..., AnalysisN]
```

## AnalysisTopGNN.Plotting.TH1F/CombineTH1F/TH2F
A class dedicated to plotting histograms using the `mplhep` package as a backend to format figures.
This class adds some additional features to simplify writing simple plotting code, such as bin centering. 

### Attributes and Functions:
#### Attributes (Cosmetics): 
- **Title**: 
Title of the histogram to generate.
- **Style**:
The style to use for plotting the histogram, options are; `ATLAS`, `ROOT` or `None`
- **ATLASData**:
A boolean switch to distinguish between *Simulation* and *Data*.
- **ATLASYear**:
The year the data/simulation was collected from.
- **ATLASCom**:
The *Center of Mass* used for the data/simulation.
- **ATLASLumi**:
The luminosity to display on the `ATLAS` formated histograms. 
- **NEvents**:
Displays the number of events used to construct the histogram. 
- **Color**:
The color to assign the histogram.
- **FontSize**:
The front size to use for text on the plot.
- **LabelSize**:
Ajusts the label sizes on the plot.
- **TitleSize**:
Modify the title font size.
- **LegendSize**:
Modify the size of the legend being displayed on the plot.
This is predominantly relevant for combining `TH1F` histograms.
- **xScaling**:
A scaling multiplier in the x-direction of the plot.
This is useful when bin labels start to merge together.
- **yScaling**:
A scaling multiplier in the y-direction of the plot.
This is useful when bin labels start to merge together.

#### Attributes (IO):
- **Filename**: 
The name given to the output `.png` file.
- **OutputDirectory**: 
The directory in which to save the figure. 
If the directory tree is non-existent, it will automatically be created.
- **DPI**:
The resolution of the figure to save. 

#### Attributes (Axis):
- **xTitle**: 
Title to place on the x-Axis.
- **yTitle**: 
Title to place on the y-Axis.
- **xMin**: 
The minimum value to start the x-Axis with.
- **xMax**:
The maximum value to end the x-Axis with.
- **yMin**: 
The minimum value to start the y-Axis with.
- **yMax**:
The maximum value to end the y-Axis with.
- **xTickLabels**:
A list of string/values to place on the x-Axis for each bin. 
The labels will be placed in the same order as given in the list.
- **Logarithmic**:
Whether to scale the bin content logarithmically.
- **Histograms**:
Expects `TH1F` objects from which to construct the combined histogram.
- **Colors**:
Expects a list of string indicating the color each histogram should be assigned.
The `CombineTH1F` automatically adjusts the color if a color has been assigned to another histogram.
- **Alpha**:
The alpha by which the color should be scaled by. 
- **FillHist**:
Whether to fill the histograms with the color assigned or not.
- **Texture**:
The filling pattern of the histogram, options are; `/ , \\ , | , - , + , x, o, O, ., *, True, False`
- **Stack**:
Whether to combine the histograms as a stack plot.
- **Histogram**:
A single `TH1F` object to which other `Histograms` are plotted against. 
- **LaTeX**:
Whether to use the *LaTeX* engine of `MatplotLib`

#### Attributes (Bins):
- **xBins**:
The number of bins to construct the histogram with.
- **xBinCentering**:
Whether to center the bins of the histograms. 
This can be relevant for classification plots.
- **xStep**:
The step size of placing a label on the x-Axis, e.g. 0, 100, 200, ..., (n-1)x100.
- **yStep**:
The step size of placing a label on the y-Axis, e.g. 0, 100, 200, ..., (n-1)x100.

#### Attributes (Data):
- **xData**:
The data from which to construct the histogram. 
If this is to be used with `xTickLabels`, make sure the bin numbers are mapped to the input list.
For example; `xData = [0, 1, 2, 3, 4]  -> xTickLabels = ["b1", "b2", "b3", "b4", "b5"]`
- **xWeights**:
Weights to be used to scale the bin content. 
This is particularly useful for using `xTickLabels`.
- **Normalize**:
Whether to normalize the data. Options are; `%`, `True` or `False`.

#### Functions (IO):
```python 
def DumpDict(varname = None)
``` 
Dumps a dictionary representation of the settings.
```python 
def Precompiler()
``` 
A function which can be overridden and is used to perform preliminary data manipulation or histogram modifications.
```python 
def SaveFigure(Dir = None)
```
Whether to compile the given histogram object. 
`Dir` is a variable used to indicate the output directory. 

#### Functions (Cosmetics): 
```python 
def ApplyRandomColor(obj)
```
Selects a random color for the histograms.

```python 
def ApplyRandomTexture(obj)
```
Selects a random texture for the histograms.

# Incomplete Documentation (Work in Progress):
## Tools.General:
- GetSourceCode 
- GetObjectFromString 
- GetSourceFile
- MergeListsInDict 
- DictToList
- AddDictToDict
- AddListToDict
- MergeNestedList 

## Tools.IO:
- lsFiles
- ls
- IsFile 
- ListFilesInDir 
- pwd
- abs
- path
- filename 
- mkdir 
- rm 
- cd

## Tools.MultiThreading.Threading:
- Start
- _lists

## Submission.Condor:
- AddJob 
- LocalDryRun 
- DumpCondorJobs 

## Plotting:
- TemplateHistograms.TH1FStack
- TemplateLines.TLine 
- TemplateLines.CombineTLine 
- TemplateLines.TLineStack 

## IO:
- HDF5.Start
- HDF5.End
- HDF5.DumpObject
- HDF5.RebuildObject 
- HDF5.MultiThreadedDump
- HDF5.MultiThreadedReading 
- HDF5.MergeHDF5
- Pickle.PickleObject
- Pickle.UnpickleObject
- Pickle.MultiThreadedDump
- Pickle.MultiThreadedReading

## EventTemplates.Templates.Selection 
- Selection 
- Strategy
- MakeNu 
- NuNu
- Nu 
- Sort 

## Generators.Settings
- DumpSettings 
- ExportAnalysisScript 
- CheckSettings
- RestoreSettings
- AddCode 
- CopyInstance 
- GetCode 
