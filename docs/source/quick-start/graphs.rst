Advanced Usage of GraphTemplate
*******************************

Introduction
____________
Unlike the ``EventTemplate`` and ``SelectionTemplate`` classes, this template module is rather simplistic by construction, as such it will be a short section. 
Most of the content explained in the :ref:`graph-start` is already considered advanced, however, there are some hidden features that this class has, which was not discussed previously.

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

For those interested, the pseudo-event implementation is shown below: 

.. code-block:: python 

    class NoneEvent:
        def __init__(self):
            pass

        def __getattr__(self, inpt):
            return []


Primitive Functions
___________________

- ``CreateParticleNodes``: 
    A function used to construct nodes from input particles 

- ``CreateEdges``:
    A function which produces the edge-index from the input particles. 
    Graphs can be either fully connected, including self-loops, or completely disconnected.

- ``ConvertToData``:
    Converts the graph-like structure into a ``PyTorch Geometric`` compatible graph object. 

- ``purge``
    Clean the graph object from no longer needed event objects. 
    This is mostly done to reduce memory consumption post graph construction.

- ``Set(Edge/Node/Graph)Attribute``:
    A function used to assign a dictionary with the appropriate functions and keys, which will be applied to the graph.

Primitive Attributes
____________________

- ``SelfLoop``:
    Connect nodes to themselves, i.e. the edge-index tensor will have values with :math:`i = j`.

- ``FullyConnect``:
    Connect all nodes with each other, this **does not** invoke ``SelfLoops`` and self-loops are not automatically added.

- ``EdgeAttr``:
    A dictionary holding the edge attribute functions, with their respective keys.

- ``NodeAttr``:
    A dictionary holding the node attribute functions, with their respective keys.

- ``GraphAttr``:
    A dictionary holding the graph attribute functions, with their respective keys.

- ``index``:
    By default set to ``-1``, but is used to index events.
