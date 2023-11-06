The Optimizer Composite Class
*****************************

A composite class focused on training and evaluating a given model.
Given the complexity of the class, several backend modules are utilized to increase performance during training.
An overview of the modules and their purposes is further discussed in the subsequent sections.

OptimizerWrapper
================

A cythonized optimizer wrapper class used for tracking and saving the state of the optimizer when training a model.

.. py:class:: OptimizerWrapper(initial = None)

    :param dict initial: Expects a dictionary of keys being class attributes with associated standard values.

    .. py:function:: setoptimizer()

        Does a preliminary check of the input settings parameters when initializing a torch optimizer, e.g. optimizer name and params.

    .. py:function:: setscheduler()

        Does a preliminary check of the scheduler parameters.

    .. py:function:: save()

        Saves the current optimizer and scheduler state for the trained model at given epoch and k-fold.

    .. py:function:: load()

        Loads the optimizer at a given epoch and k-fold.

    .. py:function:: step()

        Steps the optimizer.

    .. py:function:: zero() 

        Zeros the gradient of the model's parameters.

    .. py:function:: stepsc()

        Steps the scheduler.

    :ivar optimizer optimizer: Returns the torch optimizer.
    :ivar scheduler scheduler: Returns the torch scheduler.
    :ivar model model: Returns the original model
    :ivar str Path: The path to store the checkpoint data.
    :ivar str RunName: Name of the training session (untitled by default)
    :ivar str Optimizer: The name of the optimizer to use (SGD, ADAM, ...)
    :ivar str Scheduler: The name of the scheduler to use (ExponentialLR, ...)
    :ivar dict OptimizerParams: Additional parameters to define the optimizer.
    :ivar dict SchedulerParams: Additional parameters to define the scheduler.
    :ivar int Epoch: The current epoch of the optimizer.
    :ivar bool Train: Set the optimizer to train mode.
    :ivar int KFold: K-Fold of the optimizer.


cOptimizer
==========

.. py:class:: cOptimizer

    .. py:function:: length(self) -> dict[str, int]:

    .. py:function:: GetHDF5Hashes(str path) -> bool:

    .. py:function:: UseAllHashes(dict inpt) -> None:

    .. py:function:: MakeBatch(sampletracer, vector[string] batch, int kfold, int index, int max_percent = 80) -> [torch_geometric.Data]:

    .. py:function:: UseTheseFolds(list inpt) -> None:

    .. py:function:: FetchTraining(int kfold, int batch_size) -> list[str]:

    .. py:function:: FetchValidation(int kfold, int batch_size) -> list[str]:

    .. py:function:: FetchEvaluation(int batch_size) -> list[str]:

    .. py:function:: AddkFold(int epoch, int kfold, dict inpt, dict out_map) -> None:

    .. py:function:: DumpEpochHDF5(int epoch, str path, list[int] kfolds) -> None:

    .. py:function:: RebuildEpochHDF5(int epoch, str path, int kfold) -> None:

    .. py:function:: BuildPlots(int epoch, str path):

    :ivar bool metric_plot: Whether to plot the learning, accuracy, etc. metrics.
    :ivar list[int] kFolds: The specific k-Folds to train on. Useful for multiprocessing.


RandomSamplers
==============

.. py:class:: RandomSamplers:

    .. py:function:: SaveSets(self, inpt, path) -> None 

        Dumps the hashes of the samples to HDF5 files.

    .. py:function:: RandomizeEvents(self, Events, nEvents = None) -> dict[str: None]

        Randomly selects hashes from the input events, or randomly selects nEvents from the input.

    .. py:function:: MakeTrainingSample(self, Sample, TrainingSize=50) -> dict[str, list[str]]

        Splits the input sample into training and testing by the specified 'TrainingSize' percentage.

    .. py:function:: MakekFolds(self, sample, folds, shuffle=True, asHashes=False) -> dict[str, dict[str, list[str]]]

    .. py:function:: MakeDataLoader(self, sample, SortByNodes=False, batch_size=1) -> list[torch_geometric.Data], dict[str, list[str]]


Optimizer
=========

.. py:class:: Optimizer(inpt)

    :inherited-members: SampleTracer, _Interface, RandomSampler

    :param Union[SampleTracer, None] inpt: Set to None by default, but expects an inherited instance of SampleTracer.
    
    .. py:method:: Start(sample):

        :param Union[SampleTracer, None] sample: Set to None by default, but expects an inherited instance of SampleTracer.

