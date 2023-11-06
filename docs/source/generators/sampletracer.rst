.. _sample-tracer:

The SampleTracer
****************

A core module which is being inherited by all generator classes. 
This class focuses on tracking sample generation including events, graphs and selections, and how they are cached in memory. 
The class can be used as a standalone package, but is primarily intended to be integrated into any abstract generator class that one might want to implement, this will be illustrated later.
Most of the functionalities, such as the magic functions are implemented within this class, making it a rather useful core module. 

Methods and Attributes
______________________

.. py:class:: Event

    A simple wrapper class used to batch cached objects into a single object. 
    Upon calling for a specific attribute, the class will scan available objects for the attribute.
    Unlike most sub-modules within the package, this class has limited functionalities in terms of magic functions.

    .. py:method:: release_event() -> EventTemplate

        A method which releases the event object from the sample tracer batch.

    .. py:method:: release_graph() -> GraphTemplate

        A method which releases the graph object from the sample tracer batch.

    .. py:method:: release_selection() -> SelectionTemplate
    
        A method which releases the selection object from the sample tracer batch.

    .. py:method:: event_cache_dir() -> dict 

        Returns a dictionary of the current caching directory of the given event name.

    .. py:method:: graph_cache_dir() -> dict 

        Returns a dictionary of the current caching directory of the given event name.


    .. py:method:: selection_cache_dir() -> dict 

        Returns a dictionary of the current caching directory of the given event name.

    .. py:method:: meta() -> MetaData

        Returns a **MetaData** object for the current event.

    .. py:method:: __eq__() -> bool

        Returns true if the events have the same hash.

    .. py:method:: __hash__() -> bool

        Allows for the use of **set** and **dict**, where the event can be interpreted as a key in a dictionary.

    .. py:method:: __getstate__() -> tuple[meta_t, batch_t]

        Allows the event to be pickled.

    .. py:method:: __setstate__(tuple[meta_t, batch_t])

        Rebuilds the Event from a **meta_t** and **batch_t** data type.

    :ivar str hash: Returns a the hash of the current event.



.. py:class:: SampleTracer

    .. py:method:: __getstate__() -> tracer_t

        Export this tracer including all samples (selections, graphs, events) and state (settings).

    .. py:method:: __setstate__(tracer_t inpt)

        Import tracer parameters including all samples (selections, graphs, events) and state (settings).

        :param tracer_t inpt: An exported tracer data type.

    .. py:method:: __getitem__(key Union[list, str]) -> bool or list

        Scan indexed content and return a list of matches or a boolean if nothing has been found.
        
        :params Union[list, str] key: Scan the given requested term (ROOT name, Event Hash, ...).

    .. py:method:: __contains__(str val) -> bool

        Check if query is in sample tracer.

        :params str val: The string to check against.

    .. py:method:: __len__() -> int

        Return length of the entire sample.

    .. py:method:: __add__(other) -> SampleTracer

        Add two SampleTracers to create an independent SampleTracer. 
        Content of both samples is compared and summed as a set. 

        :params SampleTracer other: The other SampleTracer inherited object to sum.

    .. py:method:: __radd__(other) -> SampleTracer

        Add two SampleTracers to create an independent SampleTracer. 
        Content of both samples is compared and summed as a set. 

        :params SampleTracer other: The other SampleTracer inherited object to sum.

    .. py:method:: __iadd__(SampleTracer other) -> SampleTracer

        Append the incoming tracer object to this tracer.

    .. py:method:: __iter__

        Iteratate over the Sample Tracer with given parameters, e.g. cache type etc.

    .. py:method:: __next__ -> Event

        The return of the iterator is an Event (Not to be confused with EventTemplate). 
        This **Event** is a batched version of **SelectionTemplate**/**GraphTemplate**/**EventTemplate** and **MetaData**


    .. py:method:: preiteration() -> bool
        
        A place holder for adding last minute behaviour changes to the iteration process.
        This can include loading specific caches or changing general behaviour, i.e. pre-fetching etc.
        By default this function returns **False** to indicate no errors occurred.
        If **True** is returned, the iterator will be nulled.

    .. py:method:: DumpTracer(retag: Union[str, None]) -> None

        Preserve the index map of the samples within the tracer.
        The output of this is a set of HDF5 files, which are written in the form of their Logical File Names or original sample name.

        :param str, None retag: Allows for tagging specific samples of the tracer to be tagged.

    .. py:method:: RestoreTracer(dict tracers = {}, sample_name: Union[None, str]) -> None

         Restore the index map of the samples within the tracer.

         :param dict tracers: Restore these HDF5 file directories
         :param None, str sample_name: Restore only tracer samples with a particular sample name tag.

    .. py:method:: DumpEvents() -> None
        
        Preserve the **EventTemplates** in HDF5 files.

    .. py:method:: DumpGraphs() -> None

        Preserve the **GraphTemplates** in HDF5 files.

    .. py:method:: DumpSelections() -> None

        Preserve the **SelectionTemplates** in HDF5 files.

    .. py:method:: RestoreEvents(list these_hashes = []) -> None

        Restore **EventTemplates** matching a particular set of hashes.

        :params list these_hashes: A list of hashes consistent with events indexed by the tracer.

    .. py:method:: RestoreGraphs(list these_hashes = []) -> None

        Restore **GraphTemplates** matching a particular set of hashes.

        :params list these_hashes: A list of hashes consistent with events indexed by the tracer.

    .. py:method:: RestoreSelections(list these_hashes = []) -> None

        Restore **SelectionTemplates** matching a particular set of hashes.

        :params list these_hashes: A list of hashes consistent with events indexed by the tracer.

    .. py:method:: FlushEvents(list these_hashes = []) -> None

        Delete **EventTemplates** matching a particular set of hashes from RAM

        :params list these_hashes: A list of hashes consistent with events indexed by the tracer.

    .. py:method:: FlushGraphs(list these_hashes = []) -> None

        Delete **GraphsTemplates** matching a particular set of hashes from RAM.

        :params list these_hashes: A list of hashes consistent with events indexed by the tracer.

    .. py:method:: FlushSelections(list these_hashes = []) -> None

        Delete **SelectionTemplates** matching a particular set of hashes from RAM.

        :params list these_hashes: A list of hashes consistent with events indexed by the tracer.

    .. py:method:: _makebar(inpt: Union[int], CustTitle: Union[None, str] = None) -> (None, tqdm)

        Creates a *tqdm* progress bar.

        :params int inpt: Length of the sample, i.e. the range of the bar.
        :params None, str CustTitle: Override the default progress prefix title (see **Caller**).

    .. py:method:: trace_code(obj) -> code_t

        Preserve an object which is independent of the current file implementation (see **Code**).

        :params obj: Any Python object

    .. py:method:: rebuild_code(val: Union[list, str, None]) -> list[Code]

        Rebuild a set of **Code** objects which mimic the originally traced code.

        :params list, str, None val: Rebuild these strings from the traced code of the SampleTracer.

    .. py:method:: ImportSettings(settings_t inpt) -> None

        Apply settings from the input to the current SampleTracer.

        :params settings_t inpt: A dictionary like object with specific keys. See the **Data Type and Dictionary Section**.

    .. py:method:: ExportSettings -> settings_t

        Export the current settings of the SampleTracer.

    .. py:method:: clone -> SampleTracer

        Returns a copy of the current object SampleTracer object.
        This will **NOT** clone the content of the source tracer.

    .. py:method:: is_self(inpt, obj = SampleTracer) -> bool

        Checks whether the input has a type consistent with the object type (also inherited objects are permitted).

        :params inpt: Any Python object
        :params obj: The target object type to check against, e.g. SampleTracer type.

    .. py:method:: makehashes() -> dict
        
        Returns a dictionary of current hashes not found in RAM.

    .. py:method:: makelist() -> list[Event]

        Returns a list of **Event** objects regardless if Templates are not loaded in memory.

    .. py:method:: AddEvent(event_inpt, meta_inpt = None) -> None

        An internal function used to add **EventTemplate** to the sample tracer.

        :params EventTemplate event_inpt: The **EventTemplate** object to add.
        :params MetaData meta_inpt: An optional parameter that decorates the template with meta-data.

    .. py:method:: AddGraph(graph_inpt, meta_inpt = None) -> None

        An internal function used to add **GraphTemplate** to the sample tracer.

        :params GraphTemplate event_inpt: The **GraphTemplate** object to add.
        :params MetaData meta_inpt: An optional parameter that decorates the template with meta-data.


    .. py:method:: AddSelections(selection_inpt, meta_inpt = None) -> None

        An internal function used to add **SelectionTemplate** to the sample tracer.

        :params SelectionTemplate event_inpt: The **SelectionTemplate** object to add.
        :params MetaData meta_inpt: An optional parameter that decorates the template with meta-data.

    .. py:method:: SetAttribute(fx, str name) -> bool

        :params callable fx: A function used to apply to the **GraphTemplate** (this is an internal function).
        :params str name: The name of the feature to add.

    :ivar str Tree: Returns current ROOT Tree being used.
    :ivar list[str] ShowTrees: Returns a list of ROOT Trees found within the index.
    :ivar Union[EventTemplate, Code] Event: Specifies the an **EventTemplate** inherited event implementation to use for building Event objects from ROOT Files.
    :ivar list[str] ShowEvents: Returns a list of **EventTemplate** implementations found within the index.
    :ivar bool GetEvent: Forcefully get or ignore **EventTemplate** types from the **Event** object. This is useful to avoid redundant sample fetching from RAM.
    :ivar bool EventCache: Specifies whether to generate a cache after constructing **Event** objects. If this is enabled without specifying a **ProjectName**, a folder called **UNTITLED** is generated.
    :ivar str EventName: The event name to fetch from cache.
    :ivar Union[GraphTemplate, Code] Graph: Specifies the event graph implementation to use for constructing graphs.
    :ivar list[str] ShowGraphs: Returns a list of **GraphTemplate** implementations found within the index.
    :ivar bool GetGraph: Forcefully get or ignore **GraphTemplate** types from the **Graph** object. This is useful to avoid redundant sample fetching from RAM.
    :ivar bool DataCache: Specifies whether to generate a cache after constructing graph objects. If this is enabled without having an event cache, the **Event** attribute needs to be set. 
    :ivar str GraphName: The graph name to fetch from cache.
    :ivar dict[str, SelectionTemplate or Code] Selections: 
    :ivar list[str] ShowSelections:
    :ivar bool GetSelection: Forcefully get or ignore **SelectionTemplate** types from the **Selection** object. This is useful to avoid redundant sample fetching from RAM.
    :ivar str SelectionName: The selection name to fetch from cache.
    :ivar str Optimizer: Expects a string of the specific optimizer to use. Current choices are; **SGD** - Stochastic Gradient Descent and **ADAM**.
    :ivar str Scheduler: Expects a string of the specific scheduler to use. Current choices are; **ExponentialLR**, **CyclicLR**. More can be added under the loss function class.
    :ivar Union[ModelWrapper, Code] Model: The target model to be trained. 
    :ivar dict OptimizerParams: A dictionary containing the specific input parameters for the chosen **Optimizer**.
    :ivar dict SchedulerParams: A dictionary containing the specific input parameters for the chosen **Scheduler**.
    :ivar dict ModelParams: A dictionary used for initializing the model. This is only relevant if the model has input requirements to be initialized.
    :ivar list[int] kFold: Explicitly use these kFolds during training. This can be quite useful when doing parallel traning, since each kFold is trained completely independently. The variable can be set to a single integer or list of integers
    :ivar int Epoch: The epoch to start from.
    :ivar Union[list[int], int] kFolds: Number of folds to use for training
    :ivar int Epochs: Number of epochs to train the model with.
    :ivar int BatchSize: How many Graphs to group into a single big graph (also known as batch training).
    :ivar bool GetAll: Used to forcefully get all event hashes in the tracer index.
    :ivar int nHashes: Shows the number of hashes that have been indexed.
    :ivar dict ShowLength: Shows information about the number of hashes associated with a particular tree/event/graph/selection implementation.
    :ivar Union[int, None] EventStart: The event to start from given a set of ROOT samples. Useful for debugging specific events.
    :ivar Union[int, None] EventStop: The number of events to generate. 
    :ivar bool EnablePyAMI: Try to scan the input samples meta data on PyAmi.
    :ivar dict Files: Files found under some specified directory.
    :ivar dict SampleMap: A map of the sample names and associated ROOT samples.
    :ivar str ProjectName: Specifies the output folder of the analysis. If the folder is non-existent, a folder will be created.
    :ivar str OutputDirectory: Specifies the output directory of the analysis. This is useful if the output needs to be placed outside of the working directory.
    :ivar str WorkingPath: Returns the current working path of the Analysis. Constructed as; **OutputDirectory/ProjectName**
    :ivar str RunName: The name given to the particular training session of the Graph Neural Network.
    :ivar str Caller: A string controlling the verbose information prefix.
    :ivar int Verbose: An integer which increases the verbosity of the framework, with 3 being the highest and 0 the lowest.
    :ivar bool DebugMode: Expects a boolean, if this is set to **True**, a complete print out of the training is displayed. 
    :ivar int Chunks: An integer which regulates the number of entries to process for each given core. This is particularly relevant when constructing events, as to avoid memory issues. As an example, if Threads is set to 2 and **Chunks** is set to 10, then 10 events will be processed per core. 
    :ivar int Threads: The number of CPU threads to use for running the framework. If the number of threads is set to 1, then the framework will not print a progress bar.
    :ivar str Device: The device used to run ``PyTorch`` training on. Options are ``cuda`` or ``cpu``.
    :ivar str TrainingName: Name of the training sample to be used. 
    :ivar bool SortByNodes: Sort the input graph sample by nodes. This is useful when the model is node agnostic, but requires recomputation of internal variables based on variable graph node sizes. For instance, when computing the combinatorial of a graph, it is faster to compute the combinations for n-nodes and batch n-sized graphs into a single sample set.
    :ivar bool ContinueTraining: Whether to continue the training from the last known checkpoint (after each epoch).
    :ivar dict KinematicMap: An attribute enabling the mass reconstruction during and post GNN training. The following syntax is used to select a given feature from the GNN; 

        .. code-block:: python 

            <ana>.KinematicMap = {"<the feature to reconstruct>" : "<coordinate system (polar/cartesian)> -> pT, eta, phi, e"}

    :ivar bool PlotLearningMetrics: Whether to output various metric plots whilst training. This can be enabled before training or re-run after training from the training cache.
    :ivar float MaxGPU: This sets the upper limit of the GPU memory allowed during training/validation/testing.
    :ivar float MaxRAM: Sets the upper limit of the RAM used by the framework. This is independent from the GPU memory and is predominantly used to monitor general memory usage. If the data index becomes greater than the specified limit, parts of the cache is purged from memory.

    


