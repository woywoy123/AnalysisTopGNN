EventGenerator
**************
A core module of the Analysis-G framework, it is tasked to interpret the event implementations and map event and particle variables back into Python from a ROOT file. 
It is mostly used when all available event variables are needed and is therefore rather larger when using the cache. 
This module has been integrated into the ``Analysis`` wrapper and for most uses, the class wouldn't need to be called explicitly. 
For advanced users, it can be inherited into pre-existing frameworks and act as a back-end method to abstract much of the IO related with ``UpROOT``. 

To import the module, simply import it as shown below:

.. code-block:: python

    from AnalysisG.Generators import EventGenerator

    ev = EventGenerator()
  
The interface is very much identical to the ``Analysis`` wrapper and has the same magic functions, such as iteration, summation, etc.
To use it as an inheritable module, see the code below:

.. code-block:: python 

    from AnalysisG.Generators import EventGenerator

    class SomeFramework(EventGenerator):

        def __init__(self):
            EventGenerator.__init__(self)

Since the back-end of this module is based on the ``Tools`` and ``SampleTracer`` module, all their methods are also available, including the dumping of caches, ``PyAMI`` API calls and so forth.
