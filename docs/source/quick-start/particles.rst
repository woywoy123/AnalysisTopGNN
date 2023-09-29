Advanced Usage of ParticleTemplate
**********************************

Introduction
____________

As was briefly touched on in :ref:`particle-start`, the **ParticleTemplate** class is used to define Python particle objects, which can be used to mimic the particle contents of events within ROOT files.
Similar to the **EventTemplate** class, the **ParticleTemplate** leverages C++ in the back-end, but uses Cython as an interface to retain the modularity of Python. 

Primitive Attributes/Functions
______________________________

.. _pdgids: https://pdg.lbl.gov/2007/reviews/montecarlorpp.pdf

- ``Type``:
    A setter and getter function which expects a string and returns a string of the particle Type specified. 
    This parameter is optional but can be useful when wanting to create a generic particle object. 
    This will be shown in a later example.

- ``index``:
    A setter and getter function which expects a string, float, or integer. 
    If a string is assigned to the particle, then during compilation time, the associated ROOT leaf string will be used to assign the respective index.
    If a float/integer is provided, then default internal integer (``-1``) is overwritten with the assigned value. 
    If the parameter is not assigned at all, then the index will be assigned based on generation index. 

- ``hash``:
    A function which has a setter and getter implementation. 
    Once the setter has been called, an 18 character long string will be internally generated, which cannot be modified.
    The hash is computed from the particle's four vector, and is used for magic functions.

- ``px``:
    A setter and getter function which can be manually set by a string, float, or automatically by supply the particle with ``pt`` and ``phi``. 

- ``py``: 
    A setter and getter function which can be manually set by a string, float, or automatically by supply the particle with ``pt`` and ``phi``. 

- ``pz``:
    A setter and getter function which can be manually set by a string, float, or automatically by supply the particle with ``pt`` and ``eta``. 

- ``e`` (energy):
    A setter and getter function which can be manually set by a string, float, or automatically by supply the particle with ``pt``, ``eta``, ``phi`` or ``px``, ``py``, ``pz``. 

- ``pt``:
    A setter and getter function which can be manually set by a string, float, or automatically by supply the particle with ``px`` and ``py``. 

- ``eta``: 
    A setter and getter function which can be manually set by a string, float, or automatically by supply the particle with ``px``, ``py`` and ``pz`` or ``pz``, ``pt``. 

- ``phi``:
    A setter and getter function which can be manually set by a string, float, or automatically by supply the particle with ``px`` and ``py``. 

- ``Mass``:
    A setter and getter function which can be manually set by a string, float, or automatically by supply the particle with ``pt``, ``eta``, ``phi``, ``e`` or ``px``, ``py``, ``pz``, ``e``. 

- ``pdgid``:
    A setter and getter function which returns the ``pdgid`` of the particle. This can be manually set for each particle definition, see `pdgids`_.

- ``charge``:
    A setter and getter function used to assign a particle some charge. 

- ``symbol``:
    A setter and getter function used to assign a particle a symbolic string representation. 
    Some symbols are already implemented for associated ``pdgid``. 
    The complete mapping is as follows; 

    - quarks: 1 : d, 2 : u, 3 : s, 4 : c, 5 : b, 6 : b
    - leptons: 11 : e, 12 : :math:`\nu_e`, 13 : :math:`\mu`, 14 : :math:`\nu_{\mu}`, 15 : :math:`\tau`, 16 : :math:`\nu_{\tau}`

- ``lepdef``:
    A setter and getter function which expects a list of integers representing the **pdgid** considered leptons, by default this list is [11, 13, 15].

- ``nudef``:
    A setter and getter function which expects a list of integers representing the **pdgid** considered neutrinos, by default this list is [12, 14, 16].

- ``is_lep``:
    Returns a boolean whether the given particle has a **pdgid** considered to be leptonic.

- ``is_nu``:
    Returns a boolean whether the given particle has a **pdgid** considered to be a neutrino.

- ``is_b``:
    Returns a boolean whether the given particle has a **pdgid** is a b-quark.

- ``is_add``:
    Returns a boolean whether the given particle has a **pdgid** anything other than being a b-quark or leptonic.

- ``LeptonicDecay``:
    Returns a boolean whether the given particle has children which have a leptonic **pdgid**.

- ``DeltaR(ParticleTemplate)``:
    Computes the :math:`\Delta R` between two particles. Expects a particle to be inherited from from `ParticleTemplate`. 
    If two particles have a :math:`\varphi_1 = 2\pi - 0.1\pi` and :math:`0.1\pi`, respectively, then angles are normalized to obtain the lowest relative angle.

- ``clone``:
    Return a clone of the particle object type (not its properties).

- ``Parent``:
    A list used to manually add a parent particle to this particle. Returns an empty list by default.

- ``Children``:
    A list used to manually add a children particles to this particle (decay products). Returns an empty list by default.

Magic Functions
_______________
Magic functions in Python are indicated by functions which have the naming scheme ``__<name>__`` and serve as so called "Syntax Sugar". 
An example of this would be ``"ab" = "a" + "b"``, where in the back-end, Python has directly invoked the ``__add__(self, val)`` function. 
Or another example would be ``if "a" in ["a", "b"]``, here again, Python has invoked a combination of ``__hash__`` and ``__eq___`` magic functions. 
Analysis-G exploits Python's "Syntax" sugar to simplify much of the particle and event syntax as possible. 
To keep this section as straightforward as possible, any event implementation which inherits the ``EventTemplate`` class has the following Syntax sugar

.. code-block:: python 

    p1 = SomeParticle()
    p2 = SomeParticle2()
    p3 = SomeParticle3()

    # Summation 
    p = sum([p for p in [p1, p1, p1, p2, p3]])
    p = sum([p1, p1, p1, p2, p3)
    p = p1 + p2 + p3

    # Prints the particle's attributes including its children.
    print(p)

    # Equivalence 
    same = p1 == p2
    diff = p1 != p2
    contains = i in SomeParticleList

    # Can use set without altering the kinematics of the particles
    p1, p2 = set([p1, p2, p1, p2])


Particle Templating (Use-Case of Type)
______________________________________

If the ROOT files contain particle leaves of similar structure, such as "particle1_pt", "particle2_pt", "particle3"_pt, ..., then it would be tedious to rewrite each particle attribute multiple times. 
The framework allows the user to generate an abstraction of an abstraction as shown below:

.. code-block:: python 

    def GenericParticle(ParticleTemplate):

        def __init__(self):
            self.pt = self.Type + "_pt"
            self.eta = self.Type + "_eta"
            self.phi = self.Type + "_phi"
            self.e = self.Type + "_e"

    def Particle1(GenericParticle):

        def __init__(self):
            self.Type = "particle1"
            GenericParticle.__init__(self)

    def Particle2(GenericParticle):

        def __init__(self):
            self.Type = "particle2"
            GenericParticle.__init__(self)

    def Particle2(GenericParticle):

        def __init__(self):
            self.Type = "particle2"
            GenericParticle.__init__(self)

As can be easily seen, this reduces the amount of redundant code having to be written drastically and allows for recursive abstracting.
