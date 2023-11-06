.. role:: python(code)
   :language: python 

Advanced Usage of SelectionTemplate
***********************************

As previously outlined in :ref:`selection-start`, the **SelectionTemplate** is an inheritable module of the Analysis-G framework, and provides the user to generate customized analysis strategies for extracting information out of ROOT samples. 
This module differs from the **EventTemplate** in several key aspects, one of which being that the output of the selection class can be written as ROOT n-tuples and subsequently passed into some additional fitting tool for example, ``TRexFitter`` or ``PyHF``. 
Additionally, the class does not require the recompilation of events, and is therefore much faster and customizable for running analyses.


.. py:class:: SelectionTemplate

    .. py:function:: Selection(event) -> bool, str
    
        Returns by default **True** but can be overridden to add custom selection criteria.
        If the function is overridden, there are several return options which can be used to indicate the status of the selection. 
        In the simplest case, returning a boolean value indicates whether the given event should be accepted or rejected.
        For more complex cases, returning a string might be more useful, these are outlined below:
    
        * :python:`::Passed`:
          Appending this to the return string will indicate the event has passed selection and should be processed further.
        * :python:`::Rejected`:
          This indicates the event did not pass the given selection and should therefore be skipped.
        * :python:`::Error`:
          Indicates the event has failed and should be skipped. 
          This can be particularly useful, when implementing something like a try and except block to ensure the selection doesnt crash even if a particular object is missing some attribute.
        * :python:`::Ambiguous`: 
          This will be **automatically appended** to the string if none of the above keywords were found, with the event still passing the selection.
    
    .. py:function:: Strategy(event) -> bool, str, other
    
        A function which allows the analyst to extract additional information from events and implement additional complex clustering algorithms.
        The output of this function can be arbitrary, if however a string or boolean is returned, then a similar logic applies to what is outlined under **Selection**. 
        The only special case, which differs from the Selection prescription is when the string contains **"->"**, then a new key is added to the CutFlow variable without any of the **"::"** syntax.
        For any other data types, a container is filled, which can be retrieved from the variable ``Residual``. 
    
    .. py:function:: Px(met, phi) -> float
    
        A function which converts polar coordinates to Cartesian x-component.
    
    .. py:function:: Py(met, phi) -> float
    
        A function which converts polar coordinates to Cartesian y-component.
    
    .. py:function:: NuNu(quark1, quark2, lep1, lep2, event, mT = 172.5*1000, mW = 80.379*1000, mN = 0, zero = 1e-12,gev = False) -> list[[Neutrino, Neutrino]]
    
        Invokes the **DoubleNeutrino** reconstruction algorithm with the given quark and lepton pairs for this event. 
        This function returns either an empty list, or a list of neutrino objects with possible solution vectors.
        The **Neutrino** object will contain an attribute called **chi2**, which indicates the distance between the analytical ellipses.
    
    .. py:function:: Nu(quark, lep, event, S = [100, 0, 0, 100], mT = 172.5*1000, mW = 80.379*1000, mN = 0, zero = 1e-12, gev = False) -> list[Neutrino]
    
        Invokes the **SingleNeutrino** reconstruction algorithm with the given quark and lepton pair for this event. 
        This function returns either an empty list, or a list of neutrino objects with possible solution vectors.
        The variable **S** is the uncertainty on the MET of the event. 
        The **Neutrino** object will contain an attribute called **chi2**, which indicates the distance between the analytical ellipses.
    
    .. py:function:: MakeNu(s_, chi2 = None, gev = False) -> Neutrino
    
        A function which generates a new neutrino particle object with a given set of Cartesian 3-momentum vector (**s_**).
    
    .. py:function:: is_self(inpt) -> bool
    
        A function which indicates whether the input is of **SelectionTemplate** type.
    
    .. py:function:: clone() -> SelectionTemplate
        
        A function which clones the current object, but without its attributes.
     
    .. py:function:: __scrapecode__()
    
        A function which returns a dictionary which actually is a data type called **code_t**.
        This dictionary contains information about the code object and how it is preserved. 
        For more details, see the :ref:`code-types` documentation.
     
    :ivar Union[None, dict, list] __params__: 
    
        A variable which can be called prior to instanting the selection runtime. 
        The purpose of this variable is to assign parameters to the selection object, which increases object modularity.
        The parameter does not require to have any special values, as long as it is defined. 
        For example the below options are ok; 
    
        - :python:`self.__params__ = None`
        - :python:`self.__params__ = {...}`
        - :python:`self.__params__ = [...]`
 
    :ivar dict CutFlow:
    
        Returns a dictionary containing statistics involving events (not)-passing the **Selection** function.
        If during the **Strategy** a string is returned containing **"->"**, a new key is added to the dictionary and a counter is automatically instantiated and the event is counted as having passed.
    
    :ivar str ROOT: Returns the current ROOT filename of the given event being processed.
    :ivar float AverageTime: Returns the average time required to process a bunch of events.
    :ivar float StdevTime: Returns the standard deviation of the time required to process a bunch of events.
    :ivar float Luminosity: The total luminosity of a bunch of events passing the selection function. 
    :ivar int nPassedEvents: The total number of events passing the selection and strategy
    :ivar int TotalEvents: Number of events processed (can be called within the selection run-time or post run-time).
    :ivar bool AllowFailure:
    
        A boolean attribute which allows events to fail and continue the selection run-time. 
        Any failures will be recorded in the **CutFlow** dictionary and can be further investigated after processing has finished.
   
    :ivar str hash: Returns the current event hash. 
    :ivar int index: Returns the event index being current processed. 
    :ivar str Tag: A attribute which allows for event tagging.
    :ivar str Tree: 

        Returns the tree of the current event being processed. 
        This allows the user to derive complex selection methods which can be used to trigger on different event tree types.
        See :ref:`complex-events` for an in-depth example.
   
    :ivar bool cached: Returns a boolean value indicating whether this selection has been cached and stored in the HDF5 file.
    :ivar bool selection: A boolean return value indicating if the current object is of SelectionTemplate type.
    :ivar str SelectionName: Returns a string indicating the name of the object.
    :ivar list Residual: If the Strategy function returns anything other than a string, then the returned value will be placed in this list for further inspection.
    :ivar list AllWeights: All collected event weights of (not)-passing events. 
    :ivar list SelectionWeights: Weights of all events passing both the **Selection** and **Strategy** function calls.



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
            self.__params__ = {"test" : None}

        def Selection(self, event):
            if len(event.<SomeParticles>) == 0: return False # Reject the event 
            return True # Accept this event and continue to the Strategy function.

        def Strategy(self, event):
            # Recall the ROOT file from which this event is from 
            print(self.ROOT)

            # Get the event hash (useful for debugging)
            print(self.hash)

            for i in event.<SomeParticles>:
                # <.... Do some cool Analysis ....>

                # Prematurely escape the function
                if i.accept: return "Accepted -> Particles"

                # Add stuff to the attributes:
                self.SomeParticleStuff["lep"].append(i.Mass)

                if i.is_lep: self.SomeCounter["lep"] += 1


    # change the params attribute and make this parameter persistent
    # for the entire processing chain
    x = SimpleSelection()
    x.__params__["test"] = "out"

    #....


