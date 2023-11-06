Physics
_______

An extension module which optimizes common physics operators.
The input tensors can be either polar or cartesian, however one needs to specify the source coordinate type explicitly using the **Cartesian** or **Polar** submodules.
Similar to what was previously discussed, the inputs can be either combined or separate, depending on preference.

Physics for Combined Tensors (Cartesian)
========================================

.. py:function::  pyc.Physics.Cartesian.P2(torch.tensor pmc) -> torch.tensor 
    :no-index:
 
.. py:function::  pyc.Physics.Cartesian.P(torch.tensor pmc) -> torch.tensor 
    :no-index:
 
.. py:function::  pyc.Physics.Cartesian.Beta2(torch.tensor pmc) -> torch.tensor 
    :no-index:
 
.. py:function::  pyc.Physics.Cartesian.Beta(torch.tensor pmc) -> torch.tensor 
    :no-index:
 
.. py:function::  pyc.Physics.Cartesian.M2(torch.tensor pmc) -> torch.tensor 
    :no-index:

.. py:function::  pyc.Physics.Cartesian.M(torch.tensor pmc) -> torch.tensor 
    :no-index:

.. py:function::  pyc.Physics.Cartesian.Mt2(torch.tensor pmc) -> torch.tensor 
    :no-index:

.. py:function::  pyc.Physics.Cartesian.Mt(torch.tensor pmc) -> torch.tensor 
    :no-index:

.. py:function::  pyc.Physics.Cartesian.Theta(torch.tensor pmc) -> torch.tensor 
    :no-index:
 
.. py:function::  pyc.Physics.Cartesian.DeltaR(torch.tensor pmc1, torch.tensor pmc2) -> torch.tensor 
    :no-index:
 

Physics for Separated Tensors (Cartesian)
=========================================

.. py:function::  pyc.Physics.Cartesian.P2(torch.tensor px, torch.tensor py, torch.tensor pz) -> torch.tensor 
    :no-index:
 
.. py:function::  pyc.Physics.Cartesian.P (torch.tensor px, torch.tensor py, torch.tensor pz) -> torch.tensor 
    :no-index:

.. py:function::  pyc.Physics.Cartesian.Beta2(torch.tensor px, torch.tensor py, torch.tensor pz, torch.tensor e) -> torch.tensor 
    :no-index:

.. py:function::  pyc.Physics.Cartesian.Beta (torch.tensor px, torch.tensor py, torch.tensor pz, torch.tensor e) -> torch.tensor 
    :no-index:

.. py:function::  pyc.Physics.Cartesian.M2(torch.tensor px, torch.tensor py, torch.tensor pz, torch.tensor e) -> torch.tensor 
    :no-index:

.. py:function::  pyc.Physics.Cartesian.M (torch.tensor px, torch.tensor py, torch.tensor pz, torch.tensor e) -> torch.tensor 
    :no-index:

.. py:function::  pyc.Physics.Cartesian.Mt2(torch.tensor pz, torch.tensor e) -> torch.tensor 
    :no-index:

.. py:function::  pyc.Physics.Cartesian.Mt (torch.tensor pz, torch.tensor e) -> torch.tensor 
    :no-index:

.. py:function::  pyc.Physics.Cartesian.Theta(torch.tensor px, torch.tensor py, torch.tensor pz) -> torch.tensor 
    :no-index:
 
.. py:function::  pyc.Physics.Cartesian.DeltaR(torch.tensor px1, torch.tensor px2, torch.tensor py1, torch.tensor py2, torch.tensor pz1, torch.tensor pz2) -> torch.tensor 
    :no-index:

Physics for Combined Tensors (Polar)
====================================

.. py:function:: pyc.Physics.Polar.P2(torch.tensor pmu) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.P(torch.tensor pmu) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.Beta2(torch.tensor pmu) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.Beta(torch.tensor pmu) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.M2(torch.tensor pmu) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.M(torch.tensor pmu) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.Mt2(torch.tensor pmu) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.Mt(torch.tensor pmu) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.Theta(torch.tensor pmu) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.DeltaR(torch.tensor pmu1, torch.tensor pmu2) -> torch.tensor 
    :no-index:
 
Physics for Separated Tensors (Polar)
=====================================

.. py:function:: pyc.Physics.Polar.P2(torch.tensor pt, torch.tensor eta, torch.tensor phi) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.P(torch.tensor pt, torch.tensor eta, torch.tensor phi) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.Beta2(torch.tensor pt, torch.tensor eta, torch.tensor phi, torch.tensor e) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.Beta(torch.tensor pt, torch.tensor eta, torch.tensor phi, torch.tensor e) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.M2(torch.tensor pt, torch.tensor eta, torch.tensor phi, torch.tensor e) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.M(torch.tensor pt, torch.tensor eta, torch.tensor phi, torch.tensor e) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.Mt2(torch.tensor pt, torch.tensor eta, torch.tensor e) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.Mt(torch.tensor pt, torch.tensor eta, torch.tensor e) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.Theta(torch.tensor pt, torch.tensor eta, torch.tensor phi) -> torch.tensor 
    :no-index:
 
.. py:function:: pyc.Physics.Polar.DeltaR(torch.tensor eta1, torch.tensor eta2, torch.tensor phi1, torch.tensor phi2) -> torch.tensor 
    :no-index:
 
                

