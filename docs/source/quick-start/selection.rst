Advanced Usage of SelectionTemplate
***********************************

Introduction
____________
As previously outlined in :ref:`selection-start`, the **SelectionTemplate** is an inheritable module of the Analysis-G framework, and provides the user to generate customized analysis strategies for extracting information out of ROOT samples. 
This module differs from the **EventTemplate** in several key aspects, one of which being that the output of the selection class can be written as ROOT n-tuples and subsequently passed into some additional fitting tool for example, ``TRexFitter`` or ``PyHF``. 
Additionally, the class does not require the recompilation of events, and is therefore much faster and customizable for running analyses.

Primitive Attributes
____________________

- ``ROOTName``:
  Returns the current ROOT filename of the given event being processed.

- ``hash``:
  Returns the current event hash. 

- ``Tree``:
  Returns the tree of the current event being processed. 
  This allows the user to derive complex selection methods which can be used to trigger on different event tree types.
  See :ref:`complex-events` for an in-depth example.

- ``AverageTime``:
  Returns the average time required to process a bunch of events.

- ``StdevTime``:
  Returns the standard deviation of the time required to process a bunch of events.

- ``Luminosity``: 
  The total luminosity of a bunch of events passing the selection function. 

- ``NEvents``:
  Number of events processed (can be called within the selection run-time or post run-time).

- ``CutFlow``:
  Returns a dictionary containing statistics involving events (not)-passing the **Selection** function.
  If during the **Strategy** a string is returned containing "``->``", a new key is added to this dictionary and a counter is automatically instantiated.

- ``AllWeights``:
  All collected event weights of (not)-passing events. 

- ``SelWeights``:
  Event weights collected which passing the **Selection** function.

- ``Errors``:
  A dictionary which records event failures. 
  This could be the result of accessing undefined attributes or code crashing due to missing try and except code blocks. 

- ``AllowFailure``:
  A boolean attribute which allows events to fail and continue the selection run-time. 
  Any failures will be recorded in the **Errors** dictionary and can be further investigated after processing has finished.

- ``Residual``:
  If the Strategy function returns anything other than a string, then the returned value will be placed in this list for further inspection.

- ``index``:
  Returns the event index being current processed. 

- ``__params__``:
  A variable which can be called prior to instanting the selection runtime. 
  This allows for higher degree of modularity, can is a free variable which can be sourced from.
  The parameter does not require to have any special values, as long as it is defined. 
  For example the below options are ok; 

  - ``self.__params__ = None``
  - ``self.__params__ = {.....}``
  - ``self.__params__ = [.....]``

Primitive Functions
___________________

- ``Selection(event)``: 
  Returns by default **True** but can be overridden to add custom selection criteria.

- ``Strategy(event)``:
  A function which allows the analyst to extract additional information from events and implement additional complex clustering algorithms.

- ``Px(met, phi)``: 
  A function which converts polar coordinates to Cartesian x-component.

- ``Py(met, phi)``:
  A function which converts polar coordinates to Cartesian y-component.

- ``MakeNu(list[px, py, pz])``:
  A function which generates a new neutrino particle object with a given set of Cartesian 3-momentum vector.

- ``NuNu(quark1, quark2, lep1, lep2, event, mT = 172.5, mW = 80.379, mN = 0, zero = 1e-12)``:
    Invokes the **DoubleNeutrino** reconstruction algorithm with the given quark and lepton pairs for this event. 
    This function returns either an empty list, or a list of neutrino objects with possible solution vectors.

- ``Nu(quark, lep, event, S = [100, 0, 0, 100], mT = 172.5, mW = 80.379, mN = 0, zero = 1e-12)``:
    Invokes the **SingleNeutrino** reconstruction algorithm with the given quark and lepton pair for this event. 
    This function returns either an empty list, or a list of neutrino objects with possible solution vectors.
    The variable **S** is the uncertainty on the MET of the event. 

Magic Functions
_______________

.. code-block:: python 

    Ana = Analysis()

    Sel = SimpleSelection()

    # Use the Analysis class to run this on a single thread
    Sel(Ana)

    # Adding Selections 
    selected = []
    for event in Ana:
        Sel = SimpleSelection()
        selected.append(Sel(event))
    total = sum(selected)

    Sel1 = SimpleSelection()
    Sel2 = SimpleSelection2()

    # Equivalence 
    Sel1 == total # Returns True if the Selection implementations are the same
    Sel1 != Sel2  # Returns False since Sel1 and Sel2 are different implementations

Semi-Advanced Selection Example
_______________________________

.. code-block:: python

    class SimpleSelection(SelectionTemplate):
        def __init__(self):
            SelectionTemplate.__init__(self)

            # Add some attributes you want to capture in this selection 
            # This can be a nested list/dictionary or a mixture of both
            self.SomeParticleStuff = {"lep" : [], "had" : []} 
            self.SomeCounter = {"lep" : 0, "had" : 0}

        def Selection(self, event):
            if len(event.<SomeParticles>) == 0: return False # Reject the event 
            return True # Accept this event and continue to the Strategy function.

        def Strategy(self, event):
            # Recall the ROOT file from which this event is from 
            print(self.ROOTName)

            # Get the event hash (useful for debugging)
            print(self.hash)

            for i in event.<SomeParticles>:
                # <.... Do some cool Analysis ....>

                # Prematurely escape the function
                if i.accept: return "Accepted -> Particles"

                # Add stuff to the attributes:
                self.SomeParticleStuff["lep"].append(i.Mass)

                if i.is_lep: self.SomeCounter["lep"] += 1

