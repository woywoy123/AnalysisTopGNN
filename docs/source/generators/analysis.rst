The Analysis Generator
**********************
The Analysis class is a module of the framework and serves as the main interface, which unifies all modules found within the framework. 
It is composed of several generator modules and binds for instance the event, graph and selection generation into a single and convenient interface.
This class can also be used to generate and automate **Condor**/**DAGMAN** scripting, further simplifying a given analysis pipeline. 

This class has a large number of parameters, so it is advised to study this part of the documentation carefully, such that it's tools can be used as effectively as possible. 

Generating Events from EventTemplates:
______________________________________

The first step is to initialize the ``Analysis`` instance and providing it with a sample path/directory. 
This should look something like the code shown below: 

.. code-block:: python 
    
    from AnalysisG import Analysis

    Ana = Analysis()

    # Scan the entire "Some/Path/To/ROOT/" path for .root files
    Ana.InputSample("SomeName", "Some/Path/To/ROOT/")

    # Or point at a single ROOT file in "Some/Path/To/ROOT/"
    Ana.InputSample("SomeName", "Some/Path/To/ROOT/One.root") 

    # Or use some dictionary for multiple paths to scan
    scans = {
        "Some/Path/To/ROOT1" : ["*"],
        "Some/Path/To/ROOT2" : ["One.root", "Two.root", "Three.root"]
    }
    Ana.InputSample("SomeName", scans)


The purpose of ``SomeName`` is to assign certain samples a name. 
This could be useful if say, there are mulitple ROOT files which have previously been sourced/compiled, but the aim is to run only a specific sample type. 
For instance, if the framework was used to generate events from :math:`t\bar{t}` and :math:`t\bar{t}t\bar{t}`, and you wanted to only load :math:`t\bar{t}`, then you could specify the sample name and only :math:`t\bar{t}` would be loaded.

The next step would be to point the framework to the event implementation (see :ref:`event-start` for an introduction). 
Continuing on from the above code, this would be done as such: 

.. code-block:: python 

   from PathToCustomEvent.Event import CustomEvent

   Ana.Event = CustomEvent # <--- link the Event
   Ana.EventCache = True

From the above, the command ``EventCache`` informs the framework to save the Python representation ``CustomEvent`` into HDF5 files. 
This significantly reduces computational time, since the framework would not need to always re-read the ROOT files and convert them into ``CustomEvent``.
To start the process, simply call ``Ana.Launch`` and the instance will do some preliminary checks. 
At some point in the run-time, an error might occur informing you about not having a **VOMS** session, this is totally benign and can be safely ignored, and will be discussed later. 

At this point, one might notice that the framework is running rather slowly, this is likely because the number of threads or chunks have not been optimially configured.
These two parameters are key attributes that alter the Run-Time behaviour of the framework. 
As the name suggests, ``Threads`` refers to the number of ``CPU Threads``, and is set to 6 by default. 
The ``chunk`` or ``chnk`` parameter is a variable which forces the framework to allocate ``chnk`` number of events per CPU thread.
For instance, if 1000 events are being processed, one could distribute 100 events across 10 CPU threads, thus increasing parallelism. 
There is one subtle drawback with a high number of jobs per thread, and this is exessive RAM usage and transfer speeds between the parent and children threads. 
By default the ``chnk`` parameter is set to 100, but can be safely changed. 


Magic Functions
_______________

.. code-block:: python 

    # Iteration
    [i for i in Analysis]

    # Length operator
    len(Analysis)

    # Summation operator 
    Analysis3 = Analysis1 + Analysis2
    AnalysisSum = [Analysis1, Analysis2, Analysis3]

    # These will be equal since the events and ROOT files 
    # will be merged into a summed Analysis.
    # This means that if Analysis1 and Analysis2 have different events/ROOT Files
    # then the sum of these two will give Analysis3, but summing Analysis1 and 2 
    # again wont result in double counting.
    len(AnalysisSum) == len(Analysis3)


Minimalistic Example
____________________

.. code-block:: python

    from AnalysisG import Analysis
    from SomeEventImplementation import CustomEvent

    Ana = Analysis()
    Ana.ProjectName = "Example"
    Ana.InputSample(<name of sample>, "/some/sample/directory")
    Ana.Event = CustomEvent
    Ana.EventCache = True
    Ana.Launch()
 
    for event in Ana:
        print(event)

   
Run-Time Attributes
___________________

- ``Verbose``: 
    An integer which increases the verbosity of the framework, with 3 being the highest and 0 the lowest.

- ``Threads``: 
    The number of CPU threads to use for running the framework.
    If the number of threads is set to 1, then the framework will not print a progress bar. 

- ``chnk``: 
    An integer which regulates the number of entries to process for each given core. 
    This is particularly relevant when constructing events, as to avoid memory issues. 
    As an example, if Threads is set to 2 and **chnk** is set to 10, then 10 events will be processed per core. 

- ``ProjectName``: 
    Specifies the output folder of the analysis. If the folder is non-existent, a folder will be created.

- ``OutputDirectory``: 
    Specifies the output directory of the analysis. This is useful if the output needs to be placed outside of the working directory.

Event Generation Attributes
___________________________

- ``Event``: 
    Specifies the event implementation to use for constructing the Event objects from ROOT Files.

- ``EventStart``: 
    The event to start from given a set of ROOT samples. Useful for debugging specific events.

- ``EventStop``: 
    The number of events to generate. 

- ``EventCache``: 
    Specifies whether to generate a cache after constructing **Event** objects. 
    If this is enabled without specifying a **ProjectName**, a folder called **UNTITLED** is generated.

Graph Generation Attributes
___________________________

- ``EventGraph``:
    Specifies the event graph implementation to use for constructing graphs.

- ``SelfLoop``:
    Given an event graph implementation, add edges to particle nodes which connect to themselves.

- ``FullyConnect``:
    Given an event graph implementation, create a fully connected graph.

- ``DataCache``:
    Specifies whether to generate a cache after constructing graph objects. 
    If this is enabled without having an event cache, the **Event** attribute needs to be set. 

- ``TestFeature``: 
    A parameter mostly concerning graph generation. 
    It checks whether the supplied features are compatible with the **Event** python object. 
    If any of the features fail, an alert is issued. 

Optimizer Attributes
____________________

- ``TrainingPercentage``:
    Assign some percentage to training and reserve the remaining for testing.

- ``kFolds``:
    Number of folds to use for training 

- ``kFold``:
    Explicitly use this kFold during training. 
    This can be quite useful when doing parallel traning, since each kFold is trained completely independently. 

- ``BatchSize``:
    How many Event Graphs to group into a single graph.

- ``Model``:
    The model to be trained, more on this later.

- ``DebugMode``:
    Expects a boolean, if this is set to **True**, a complete print out of the training is displayed. 

- ``ContinueTraining``:
    Whether to continue the training from the last known checkpoint (after each epoch).

- ``Optimizer``:
    Expects a string of the specific optimizer to use.
    Current choices are; **SGD** - Stochastic Gradient Descent and **ADAM**.

- ``OptimizerParams``: 
    A dictionary containing the specific input parameters for the chosen **Optimizer**.

- ``Scheduler``:
    Expects a string of the specific scheduler to use. 
    Current choices are
    - **ExponentialLR** 
    - **CyclicLR**

- ``SchedulerParams``: 
    A dictionary containing the specific input parameters for the chosen **Scheduler**.

- ``Device``: 
    The device used to run ``PyTorch`` training on. This also applies to where to store graphs during compilation.

Run-Time Functions:
___________________
 
- ``InputSample(Name, SampleDirectory)``:
    This function is used to specify the directory or sample to use for the analysis. 
    The **Name** parameter expects a string, which assigns a name to **SampleDirectory** and is used for book-keeping. 
    **SampleDirectory** can be either a string, pointing to a ROOT file or a nested dictionary with keys indicating the path and values being a string or list of ROOT files. 

- ``AddSelection(Name, inpt)``:
    The **Name** parameter specifies the name of the selection criteria, for instance, **MySelection**. 
    The **inpt** specifies the **Selection** implementation to use, more on this later. 

- ``MergeSelection(Name)``:
    This function allows for post selection output to be merged into a single pickle file. 
    During the execution of the **Selection** implementation, multiple threads are spawned, which individually save the output of each event selection, meaning a lot of files being written and making it less ideal for inspecting the data.
    Merging combines all the internal data into one single file and deletes files being merged. 
 
- ``DumpSettings``:
    Returns a directory of the settings used to configure the **Analysis** object. 

- ``ImportSettings(inpt)``:
    Expects a dictionary of parameters used to configure the object.

- ``Quantize(inpt, size)``:
    Expects a dictionary with lists of ROOT files, that need to be split into smaller lists (defined by size).
    For instance, given a size of 2, a list of 100 ROOT files will be split into 50 lists with length 2.

- ``Launch``:
    Launches the Analysis with the specified parameters.


Default Values of Analysis
__________________________

Run-Time Values (All Stages)
============================

- ``Verbose``: 3
- ``Threads``: 6
- ``chnk``: 100
- ``OutputDirectory``: "./"
- ``ProjectName`` : "UNTITLED"
- ``PurgeCache``: False (Warning! This will delete all your cache.)

Event Generation Values
=======================

- ``EventStart``: -1
- ``EventStop``: None 
- ``Event``: None 
- ``EventCache``: False

Event Graph Generation Values
=============================

- ``EventGraph``: None 
- ``SelfLoop``: True 
- ``FullyConnect``: True

Machine Learning/Optimizer Values
=================================

- ``kFolds``: False
- ``kFold``: None 
- ``Epochs``: 10
- ``Epoch``: None 
- ``RunName``: "RUN"
- ``DebugMode``: False
- ``TrainingSample``: "Sample"
- ``Model``: None 
- ``ContinueTraining``: False
- ``SortByNodes``: False
- ``BatchSize``: 1
- ``EnableReconstruction``: False
- ``Optimizer``: None
- ``OptimizerParams``: {}
- ``Scheduler``: None
- ``SchedulerParams``: {}

Sample Generator / Random Sampler Values
========================================

- ``TrainingSize``: False
- ``Shuffle`` : True 

Feature Analysis Values
=======================

- ``nEvents``: 10
- ``TestFeatures``: False
