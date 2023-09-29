Advanced Usage of EventTemplate
*******************************

Introduction
____________
As was briefly discussed in :ref:`event-start`, the **EventTemplate** class has many abstract features which will be discussed here.
Something worth noting is that this module has been implemented in C++ but exploits Cython to retain the modularity of Python.
The C++ back-end is used to speed up certain operations, which would be tedious or slow in nominal Python, this includes hashing, object comparison, sample tracing, etc.
The underlying source code can be found under the ``src/Templates/CXX/Templates.cxx`` and ``src/Templates/Headers/Templates.h``. 

Primitive Attributes
____________________

- ``clone``: 
    A function which creates a duplicate of the event object. 
    This **does not** clone the events attributes, but rather only creates an empty clone of the given event. 

- ``index``:
    A function which has both a setter and getter implementation. 
    It is used to assign an event some internal index, this can be either a leaf string from within a ROOT tree/branch, or directly set to an integer. 
 
- ``weight``:
    A function which has both a setter and getter implementation:
    It is used to assign the given event some event weight.
    This is particularly important when computing the integrated luminosity of samples and for computing the cross section. 
    It can be either assigned a leaf string from within a ROOT tree/branch, or directly set to a float.

- ``Tree``:
    The tree from which this event is derived from. This is not to be confused with the **Trees** variable.
    This attribute is a function which has both a setter and getter, and expects a string. 
    **Note:** This variable does not need to be set manually if the event is assigned **Trees**. 

- ``Trees``:
    A list of strings from which to source events from.
    If multiple **Trees** are specified, the given event implementation is cloned twice (one for each tree) and assigned their respective **Tree** value. 

- ``Branches``:
    A list of strings from which to source branch variables from. 
    This is relevant if the ROOT data structure has nested leaf values.

- ``Leaves``:
    A list of leaves to retrieve from the ROOT file for this event implementation.
    This includes leaves from particles being linked to the event.
    Generally this attribute shouldn't be defined, since it is used internally.

- ``Objects``:
    A dictionary of particle names and their associated objects. 
    This is used to link particles to events, these particles will be available within the event under the attribute name of the dictionary keys. 
    For instance if the dictionary contains ``{"name" : Particle()}``, then these particles can be retrieved via ``event.name``. 
    By default the particles living under the dictionary key-name will also be dictionaries, with keys being integer indices. 

- ``hash``:
    A function which has a setter and getter implementation. 
    Once the setter has been called, an 18 character long string will be internally generated, which cannot be modified.
    The hash is computed from ``input/<event index>/Tree``, and assigns each event a unique identity such that the tracer can retrieve the specified event.
    If the getter (``self.hash``) has been called prior to the setter (``self.hash = 'something'``), then an empty string is returned.

- ``Deprecated``:
    A getter and setter function which indicates whether the given event implementation has been deprecated. 
    This can be useful when writing multiple event definitions but wanting to keep the old version, but ensuring that the user is made aware that this event is invalid/outdated. 
    The input is a boolean and if set to ``True``, will issue a warning to the user. 

- ``CommitHash``:
    A getter and setter function which is used for book-keeping purposes. 
    If the user decides to modify the implementation, the git-hash can be recorded here for later referencing. 
    For example, if the event was used with a specific ``AnalysisTop`` ROOT sample, but this implementation has been modified, the git-hash of ``AnalysisTop`` could be used as reference. 
    This function expects a string of any length/content. 


Magic Functions
_______________
Magic functions in Python are indicated by functions which have the naming scheme ``__<name>__`` and serve as so called "Syntax Sugar". 
An example of this would be ``"ab" = "a" + "b"``, where in the back-end, Python has directly invoked the ``__add__(self, val)`` function. 
Or another example would be ``if "a" in ["a", "b"]``, here again, Python has invoked a combination of ``__hash__`` and ``__eq___`` magic functions. 
Analysis-G exploits Python's "Syntax" sugar to simplify much of the particle and event syntax as possible. 
To keep this section as straightforward as possible, any event implementation which inherits the ``EventTemplate`` class has the following Syntax sugar

.. code-block:: python 

    ev = MyEvent()
    ev2 = MyEvent2()
    ev3 = MyEvent3()

    hash(ev) # Invokes the __hash__ function  
    print(ev2 == ev1) # returns False 

    # returns True if and only if the following attributes are identical:
    # - the hashes are identical
    # - Tree
    # - index
    # - ROOT File
    # - Event Implementation
    print(ev == ev)

    # returns True 
    ev in [ev, ev2, ev2, ev3, ev......]


    events = set([ev, ev2, ev2, ev3, ev])

    # returns [ev, ev2, ev3] since they are unique 
    # this allows one to remove duplicates
    print(events)

Advanced Attributes/Functions
_____________________________

- ``__interpret__`` (getter)
    A special function which returns a dictionary of trees/branches/leaves to get from the ROOT file for each object type. 
    Essentially, this is the output of scanning the event implementation and its constituents. 

- ``__interpret__`` (setter)
    Expects a dictionary as input with keys indicating the attribute to assign to the event. 
    For example, ``{"met" : 1000}`` will be translated to ``event.met -> 1000``.

- ``__compiler___(dict value)``
    Compiles the event from the input dictionary, including the particles. 
    When calling the function, the ``__interpret__`` setter is called recursively to generate and populate underlying event objects, such as particles and the events. 
    The output will be a list of event(s), depending on the number of entries specified in **Trees**. 

- ``CompileEvent()``
    A function which has no input but allows the user to define any last minute links between particles. 
    This can be very useful when ROOT files contain truth information, such as particle linkage attributes or multiple Trees are specified. 
    In cases of multiple Trees, additional functions can be used to "route" the compilation to a specific function. 
    This will be shown in more detail in the code examples below.

Meaning of **In** and **Post** Compilation
__________________________________________
Since Python is not a compiled language, the context of compilation infers the stage where the framework generates and builds event/particle objects. 
During the building stage (**In**) certain operations are performed only once and cannot be rerun after. 
For example this could include the generation of event hashes, object scanning or ROOT entry retrieval. 
So to ensure smooth integration, some variables need to be specified within the ``__init__`` function of the event implementation. 
If additional operations are required to fully define the event, then use the ``CompileEvent`` method.
Post compilation implies operations which are defined outside of the build process. 


Example Attributes used In and Post Compilation
___________________________________________________

``clone`` **Can be used In/Post Compilation**

.. code-block:: python 

    ev = MyEvent()

    # Create a completely independent clone of the event object
    ev2 = ev.clone

``index`` **Can be used In/Post Compilation**

.. code-block:: python 

    ev = MyEvent()

    # Directly assign the event index
    ev.index = 100

    # Or assign a string variable (only valid In compilation)
    ev.index = "nominal/index"

``weight`` **Can be used In/Post Compilation**

.. code-block:: python 

    ev = MyEvent()

    # Directly assign the event weight
    ev.weight = 100

    # Or assign a string variable (only valid In compilation)
    ev.weight = "nominal/weight"

``Tree`` **Defined In/Post Compilation**

.. code-block:: python 

    ev = MyEvent()

    # Return event tree
    print(ev.Tree)

    # Redefine tree - This wont have any impact 
    ev.Tree = "some tree"

``Trees`` **Defined In Compilation**

.. code-block:: python 

    class MyEvent(EventTemplate):
        def __init__(self):
            EventTemplate.__init__(self)

            # used to retrieve leaf values under these trees
            self.Trees = ["nominal", "some_trees"]

``Branches`` **Defined In Compilation**

.. code-block:: python 

    class MyEvent(EventTemplate):
        def __init__(self):
            EventTemplate.__init__(self)

            # used to retrieve leaf values under these trees
            self.Trees = ["nominal", "some_trees"]

            # Scans additional branches within "nominal" and "some_trees"
            self.Branches = ["ParticleBranch1", "ParticleBranch2"]

            # The output of the __interpret__ will look like this 
            # {
            #   event: [
            #       "nominal/ParticleBranch1", 
            #       "nominal/ParticleBranch2",
            #       "some_tree/ParticleBranch1", 
            #       "some_tree/ParticleBranch2",
            #   ]
            # If the above combination is not found within the ROOT sample, then it will be skipped without warning.

``Objects`` **Defined In Compilation**

.. code-block:: python 

    class MyEvent(EventTempate):
        def __init__(self):
            EventTemplate.__init__(self)

            self.Objects = {"name" : SomeParticle()}

        def CompileEvent(self):
            # Retrieve particles defined under self.Objects
            # Particles will be presented as dictionaries: 
            # {0 : Particle, 1 : Particle, 2 : Particle, N-1 : Particle}
            print(self.name)

``hash`` **Defined In Compilation**

.. code-block:: python 

    class MyEvent(EventTempate):
        def __init__(self):
            EventTemplate.__init__(self)

            self.Trees = ["nominal"]

        def CompileEvent(self):

            # The hash of the event is generated either with a specified self.index 
            # or defaults to the event index as the event is generated.
            print(self.hash)

Simple CompileEvent Example
___________________________

The above code is an example of how the **CompileEvent** method can used to link truth particles to some hypothetical detector particles, provided the variables ``truth_index`` and ``index`` are attributes of the ``DetectorParticle`` and ``TruthParticle``, and matched to leaf strings in ROOT files. 
Although the above is a simple example, the complexity can be increased and further generalized as shown in the next example.

.. code-block:: python 

    class MyEvent(EventTempate):
        def __init__(self):
            EventTemplate.__init__(self)

            self.Trees = ["nominal"]
            self.Objects = {
                "truth_particle" : TruthParticle(),
                "detector_particle" : DetectorParticle()
            }

        def CompileEvent(self):
            tempLink = {}
            for i in self.detector_particles.values():
                index = i.truth_index
                if index not in tempLink:
                    tempLink[index] = []
                tempLink[index].append(i)

            for i in truth_particle.values():
                index = i.index
                for k in tempLink[index]:
                    k.Parent.append(i)

.. _complex-events:

Complex CompileEvent Example
____________________________

The hypothetical problem being discussed here, is about how to generalize the above example and make the class ``MyEvent`` as reusable as possible, without resorting to multiple event definitions. 
This could happen if certain trees have different particle definitions, matching schemes, or particle object meaning. 
Naturally, a naive approach would be to define a new ``event.py`` for each tree and rerun those separately. 
However, there is a simpler approach as shown below:

.. code-block:: python 

    class MyEvent(EventTempate):
        def __init__(self):
            EventTemplate.__init__(self)

            self.Trees = ["nominal", "systematic"]
            self.Objects = {
                "truth_particle" : TruthParticle(),
                "systematic_particle" : SysParticle(),
                "detector_particle" : DetectorParticle(), 
            }

        def UseNominal(self):
            tempLink = {}
            for i in self.detector_particles.values():
                index = i.truth_index
                if index not in tempLink:
                    tempLink[index] = []
                tempLink[index].append(i)

            for i in truth_particle.values():
                index = i.index
                for k in tempLink[index]:
                    k.Parent.append(i)

        def UseSystematic(self):
            system = list(self.systematic_particles.values())
            detect = list(self.detector_particle.values())

            mini_deltaR = {}
            outliers = []
            for i in detect:
                for j in system:
                    # find deltaR between particles (inbuilt particle function)
                    delR = j.DeltaR(i)

                    # Separate outliers larger than 0.4
                    if delR > 0.4: outliers.append(j)
                    else mini_deltaR[delR] = [i, j]
            self.mini_deltaR = list(sorted(mini_deltaR).values())
            self.outliers = outliers

        def CompileEvent(self):

            # Use the self.Tree as a routing mechanism in compilation 

            # Link truth particles to detector particles
            if self.Tree == "nominal": self.UseNominal()

            # Find the lowest deltaR and create outliers larger than 0.4
            if self.Tree == "systematic": self.UseSystematic()

As seen in the example above, there is no need to rewrite an entire event implementation, but rather use internal variables to force the compiler to use a specific function based on the tree. 

Examples of Complex Implementations
___________________________________
See src/Events/Events/Event.py

