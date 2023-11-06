The GraphGenerator
******************

A core module of the Analysis-G framework.
The purpose of this module is to convert **EventTemplate** objects into **PyTorch Geometric** compatible Graph Data objects.
This class features a set of input methods, used to populate a particle graph with customized features.
Furthermore, the parent class of this module is the **SampleTracer**, thus contains the same tunable parameters.

The module can be used, similar to the **EventGenerator**, as a standalone module or integrated into a larger package.
A simple example is shown below:

.. code-block:: python

    from AnalysisG.Generators import GraphGenerator, EventGenerator

    gr = GraphGenerator()


