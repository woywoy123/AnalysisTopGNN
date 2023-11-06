Getting Started
===============

Using the Framework with ROOT Samples
_____________________________________
To make the framework compatible with your ROOT samples, create a new workspace directory. 

.. code-block:: console 

    mkdir Analysis
    mkdir Analysis/Objects

Within the **Objects** folder create the following files:

.. code-block:: console 

   touch Analysis/Objects/particles.py
   touch Analysis/Objects/event.py
   touch Analysis/Objects/graph.py
   touch Analysis/Objects/selection.py

The above directory structure does not necessarily need to be followed, but minimizes clutter and provides oversight over what the Analysis is composed of. 
Alternatively, the following bash command can be run, which will mimic the above structure and pre-populate the templates for you.

.. code-block:: console 

   make_analysis 

.. _particle-start:

Particle Definitions
____________________
To create the particles templates, open the **particles.py** file and import the framework's base **ParticleTemplate** class. 
This base class interprets attributes and introduces additional functionalities that will be discussed further in the advanced section.
For now, a simple example would look like the code below: 

.. code-block:: python
    
    from AnalysisG.Templates import ParticleTemplate

    # Inherit functions from ParticleTemplate
    class CustomParticle(ParticleTemplate):

        def __init__(self):
            # Initialize the object and inherit base properties 
            ParticleTemplate.__init__(self)

            # optional but useful for making templates
            self.Type = "Particle"

            # Define the four vector 
            self.pt = self.Type + ".pt"
            self.eta = self.Type + ".eta"
            self.phi = self.Type + ".phi"
            self.e = self.Type + ".energy"

            #.... <Some other desired attributes>

.. _event-start:

Event Definitions
_________________
To create an event implementation, simply open the **event.py** file and import the particles defined in the **particles.py** file. 
Similar to the **particle.py** case, the name of the file can be completely arbitrary. 
Similar to the particle template example, import the base class **EventTemplate** and add a few variable declarations, as shown below:

.. code-block:: python 

    from AnalysisG.Templates import EventTemplate
    from .particles import CustomParticle # import the particle

    class CustomEvent(EventTemplate):
        def __init__(self):
            EventTemplate.__init__(self)

            self.Type = "Event"
            self.runNumber = self.Type + ".Number" # <--- Example event leaf variable

            # Specify the trees you want to use for each event.
            self.Trees = ["nominal", "..."]

            # Depending where the particles should be read from, either specify the branch 
            # or leave the branch empty and the framework will revert to the tree 
            # If there are any relevant branches add these as well.
            self.Branches = ["..."]

            # Add particles/additional objects constituting the event
            self.Objects = {
                "ArbitraryParticleName" : CustomParticle()
            }

            # Event luminosity which is used for computing the 
            # integrated luminosity for a sum of events.
            self.weight = 1 # can be hard coded like this or assigned a string 

        def CompileEvent(self):
            # Particle names defined in self.Objects will appear 
            # in this code segment as self.<Some Random Name>.
            # For example; 
            for i in self.ArbitraryParticleName:
                print(self.ArbitraryParticleName[k].pt)

            # Convert particle dictionary to list of particles for the event.
            self.ArbitraryParticleName = list(self.ArbitraryParticleName.values())


            # ... <Some Compiler Logic - Particle Matching etc.>


Important Attributes of EventTemplate
_____________________________________
Unlike the **ParticleTemplate**, the **EventTemplate** contains much more logic and adjustable parameters.
Most important to note are the key attributes, **Objects**, **Trees/Tree** and **Branches**. 
The **Objects** attribute tells the framework to link these particles to the event, if this variable is not populated, the event will simply have no particles. 
The **Trees/Tree** and **Branches** variables are used to control which parts of the ROOT file, the framework should source the particles/event attributes from. 
Fortunately, if a tree or branch has not been found, a warning will be issued and the associated object attribute will be skipped. 

.. _graph-start:

Graph Definitions
_________________
Similar to the above examples, to create graph data structures simply open the **graph.py** file inherit the base **GraphTemplate** class as shown below:

.. code-block:: python 

    from AnalysisG.Templates import GraphTemplate

    class MyGraph(GraphTemplate):

        def __init__(self, Event = None):
            GraphTemplate.__init__(self)
            self.Event = Event
            self.Particles += self.Event.ArbitraryParticleName


Graph features are not declared within the object class, but rather when launching the framework, as illustrated below: 

.. code-block:: python 

    from AnalysisG import Analysis
    from Objects.event import MyEvent
    from Objects.graphs import MyGraph

    def some_edge(a, b): return a.px - b.px
    def some_node(a): return a.px
    def some_graph(ev): return ev.weight


    Ana = Analysis()
    Ana.Event = MyEvent
    Ana.Graph = MyGraph
    Ana.AddEdgeFeature(some_edge, "delta_px")
    Ana.AddNodeFeature(some_node, "px")
    Ana.AddGraphFeature(some_graph, "weight")
    Ana.AddNodeTruthFeature(some_truth, "attribute")
    Ana.Launch()


There is a lot going on in the above example, this can be summarized as follows: 

- The first lines are importing **MyEvent** and **MyGraph** 
- The second block defines the functions defining the attributes to add to the graph.
- The third block utilizes the **Analysis** module to unify all modules and provides an interface to launch the code. 

Inspection of the graph features may suggest the code would throw an attribute error, since the variables **.px** etc. were not defined.
By default, the **ParticleTemplate** module introduces several inbuilt attributes and functions, these include coordinate system transformations and many more.
These functionalities are discussed under the **Advanced section**.

To access the graph attributes, the graph compiler appends prefixes to the attribute names, corresponding to the graph variable. 
For instance, a node attribute, would have the format, ``N_px``, where ``N`` corresponds to **Node**. 
For truth attributes, the format would be ``N_T_<truth attribute>``, where ``T`` implies **Truth**.
In the example above, to access all of the attributes, this would look like shown below:

.. code-block:: python 

    for gr in Ana:
        gr.E_delta_px # - Edge (delta_px)
        gr.N_px       # - Node (px)
        gr.G_weight   # - Graph (weight)
        gr.N_T_attribute # - Node Truth (attribute)

One might wonder whether all the ``PyTorch Geometric`` functionality is available, and the answer is absolutely!
Underneath the **gr** object is a ``Graph`` object which is interfaced with ``PyTorch Geometric``!
As an example, see ``tutorial/ExampleGraphAnalysis.py``.

.. _selection-start:

Selection Definitions
_____________________
This module is optional but can be very useful for post-processing ROOT samples. 
Here events can be filtered according to some event selection criteria and subsequently passed to some clustering strategy. 
For example, if the aim is to generate mass distributions of a heavy scalar resonance, a strategy method can be defined and used to sum particles together and record the associated mass.
Or alternatively, if the input ROOT samples were generated with some framework, this module can be rather useful to verify whether the matching/tagging of particles is done correctly. 

To implement a selection, open the **selection.py** and inherit the **SelectionTemplate** as shown below: 

.. code-block:: python 

    from AnaylsisG.Templates import SelectionTemplate

    class MySelection(SelectionTemplate):

        def __init__(self):
            SelectionTemplate.__init__(self)
            # Public variables, will be saved
            self.ClusterMasses = {}
            self.ParticleMasses = []

            # Private variables will not be saved
            self._Hidden = {}

        def Selection(self, event):
            if len(event.ArbitraryParticleName) == 4:
                return True
            return False

        def Strategy(self, event):
            self.ClusterMasses += [sum(event.ArbitraryParticleName).Mass]
            for i in event.ArbitraryParticleName:
                self.ParticleMasses.append(i.Mass)

In the above example, the **Selection** method is used to pre-filter events, for example if the event doesn't contain exactly 4 particles, then the event is skipped due to it not meeting the event requirements. 
Only events passing the **Selection** method will be further passed to the **Strategy** method, where additional information can be extracted. 


