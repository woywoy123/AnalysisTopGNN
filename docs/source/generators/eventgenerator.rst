The EventGenerator
******************

A core module of the Analysis-G framework, used to interpret event implementations and map ROOT trees/branches/leaves to particles and events.
Since the events are using all available information of the ROOT sample, the resulting objects can become rather sizable in terms of RAM usage. 
As such, the class is generally used with **EventCache**, as this prevents the reading and recomputation of the object.

This module has been integrated into the **Analysis** wrapper and for most uses, the class would not need to be called explicitly. 
For advanced users, it can be inherited into pre-existing frameworks and act as a back-end method to abstract much of the IO related with ``UpROOT``. 

To import the module, simply import it as shown below:

.. code-block:: python

    from AnalysisG.Generators import EventGenerator

    ev = EventGenerator()
  
The interface is identical to the **Analysis** wrapper and has the same magic functions, such as iteration, summation, etc.
To use it as an inheritable module, see the code below:

.. code-block:: python 

    from AnalysisG.Generators import EventGenerator

    class SomeFramework(EventGenerator):

        def __init__(self):
            EventGenerator.__init__(self)

Since the back-end of this module is based on the **Tools** and **SampleTracer** module, all their methods are also available.
