Advanced Usage of GraphTemplate
*******************************

Unlike the ``EventTemplate`` and ``SelectionTemplate`` classes, this template module is rather simplistic by construction, as such it will be a short section. 
Most of the content explained in the :ref:`graph-start` is already considered advanced, however, there are some hidden features that this class has, which was not discussed previously.

.. py:class:: GraphTemplate

    .. py:method:: __scrapecode__(fx, str key) -> Code

        A function which returns a dictionary which actually is a data type called **code_t**.
        This dictionary contains information about the code object and how it is preserved. 
        For more details, see the :ref:`code-types` documentation.

    .. py:method:: AddGraphFeature(fx, str name = "")

        :param function fx: Function used to compute the graph feature.

    .. py:method:: AddNodeFeature(fx, str name = "")

        :param function fx: Function used to compute the node feature.

    .. py:method:: AddEdgeFeature(fx, str name = "")

        :param function fx: Function used to compute the edge feature.

    .. py:method:: AddGraphTruthFeature(fx, str name = "")

        :param function fx: Function used to compute the graph feature.

    .. py:method:: AddNodeTruthFeature(fx, str name = "")

        :param function fx: Function used to compute the node feature.

    .. py:method:: AddEdgeTruthFeature(fx, str name = "")

        :param function fx: Function used to compute the edge feature.

    .. py:method:: AddPreSelection(fx, str name = "")

        :param function fx: Function used to accept or reject this graph

    .. py:method:: SetTopology(fx = None)

        :param function fx: Function used to impose a prior bias on the topology.

    .. py:method:: __buildthis__(str key, str co_hash, bool preselection, list this)

        A method which builds the given feature. 

    .. py:method:: Build()

        A method which builds the graph object.

    .. py:method:: ImportCode(dict inpt)

        A method which imports Code objects to the graph.

    .. py:method:: ParticleToIndex(ParticleTemplate val) -> int

        Returns the index of the given particle object within the computation graph.

    .. py:method:: is_self(inpt) -> bool

        Returns a boolean value on whether the input is of **GraphTemplate** type.

    .. py:method:: ImportMetaData(meta_t meta)

        Import the MetaData object dictionary.

    .. py:method:: Import(graph_t graph)

        Instantiate a graph object from a graph_t dictionary type.

    .. py:method:: clone() -> GraphTemplate

        A function which creates a duplicate of the graph object. 
        This **does not** clone the graph attributes, but rather only creates an empty clone of the given graph. 

    :ivar list Topology: Returns the current graph topology.
    :ivar graph_t Export: Export the graph object as a dictionary.
    :ivar EventTemplate Event: 

        A variable used to indicate the event to be the target for graph compilation.
        Requires an **EventTemplate** object or any object which has the appropriate attributes.
    
    :ivar list[ParticleTemplate] Particle: A list of particles to compute the topology/graph/node from.
    :ivar bool self_loops: Connect nodes to themselves, i.e. the edge-index tensor will have values with `i = j`.
    :ivar bool code_owner: A special attribute used to indicate whether the C++ backend should be owner of the code objects.
    :ivar dict[str, Code] code: Returns a dictionary with the Code objects used to construct the graph.
    :ivar int index: An index used to track which event the graph is being computed from. 
    :ivar dict Errors: Outputs a dictionary with errors encountered during graph construction.
    :ivar dict PreSelectionMetric: Outputs information about the **PreSelection** function's impact on graphs.
    :ivar bool Train: Assign the graph for training sample.
    :ivar bool Eval: Assign the graph to evaluation sample.
    :ivar bool Validation: Assign the graph to validation sample.
    :ivar bool EmptyGraph: Returns a **True** if the event has no particles/event passing the **PreSelection** or **Topology** functions.
    :ivar bool SkipGraph: Exclude the graph from training/validation/evaluation.
    :ivar str Tag: A variable used to tag the event with some string value. 
    :ivar bool cached: Indicates whether this graph has been cached and saved within a HDF5 file.
    :ivar str ROOT: Returns the ROOT filename from which the event was compiled from.
    :ivar str hash: 

        Once set, an 18 character long string will be internally generated, which cannot be modified.
        The hash is computed from ``input/<event index>/``, and assigns each event a unique identity such that the tracer can retrieve the specified event.
        If the getter (``self.hash``) has been called prior to the setter (``self.hash = 'something'``), then an empty string is returned.

    :ivar bool Graph: Returns a boolean to indicate this graph to be of GraphTemplate type.
    :ivar str GraphName: Returns the name of this graph type.
    :ivar str Tree: Returns the ROOT Tree from which the graph was generated from.


Missing EventTemplate Attribute Behavior
________________________________________

.. code-block:: python 

    from AnalysisG.Templates import GraphTemplate

    class MyGraph(GraphTemplate):

        def __init__(self, Event = None):
            self.Event = Event
            self.Particles += self.Event.ArbitraryParticleName

Consider the code-block above, one might wonder what would happen if the ``Event`` implementation is missing an attribute? 
Generally, this would result in the code crashing and throwing the ``AttributeError`` exception. 
The framework in constructed to account for such instances using a pseudo-event object, which is instantiated when the ``self.Event`` variable is set. 
When the object does not contain the attribute ``ArbitraryParticleName``, the pseudo-event will return an empty list, and thus populate an empty graph (although graph level features would still be included).
This means, the event or event-graph would still be available, but with no particle nodes or edges. 
