Transformation
______________

An extension module which aims to simplify the transformation between Polar and Cartesian coordinates within the ATLAS detector. 
In the context of Neural Networks, this is particularly useful, since all functions within the module are written in both native C++ and CUDA, resulting in faster training and inference performance.
Some of the module member functions have also been ported to natively support Python types such as floats and integers.


Transformation for Combined Tensors
===================================

The term **Combined** refers to input tensors, where the entire four-vector of the particle is specified, or just enough information for the module to infer the values.
For instance, rather than using the individual particle four-vector components as input arguments, one could pass the entire vector as a single tensor, thus reducing code cluttering. 

.. py:function:: pyc.Transform.Px(torch.tensor pmu) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.Py(torch.tensor pmu) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.Pz(torch.tensor pmu) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.PxPyPz(torch.tensor pmu) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.PxPyPzE(torch.tensor pmu) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.Pt(torch.tensor pmc) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.Eta(torch.tensor pmc) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.Phi(torch.tensor pmc) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.PtEtaPhi(torch.tensor pmc) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.PtEtaPhiE(torch.tensor pmc) -> torch.tensor
    :no-index:

Transformation for Separated Tensors
====================================

The term **Separated** refers to input tensors representing the individual particle's four momenta compents.

.. py:function:: pyc.Transform.Px(torch.tensor pt, torch.tensor phi) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.Py(torch.tensor pt, torch.tensor phi) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.Pz(torch.tensor pt, torch.tensor eta) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.PxPyPz(torch.tensor pt, torch.tensor eta, torch.tensor phi) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.PxPyPzE(torch.tensor pt, torch.tensor eta, torch.tensor phi, torch.tensor e) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.Pt(torch.tensor px, torch.tensor py) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.Eta(torch.tensor px, torch.tensor py, torch.tensor pz) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.Phi(torch.tensor px, torch.tensor py) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.PtEtaPhi(torch.tensor px, torch.tensor py, torch.tensor pz) -> torch.tensor
    :no-index:

.. py:function:: pyc.Transform.PtEtaPhiE(torch.tensor px, torch.tensor py, torch.tensor pz, torch.tensor e) -> torch.tensor
    :no-index:

Transformation for Combined Floats
==================================

.. py:function:: pyc.Transform.Px(list[list[pt, eta, phi, e]]) -> list[float]
    :no-index:

.. py:function:: pyc.Transform.Py(list[list[pt, eta, phi, e]]) -> list[float]
    :no-index:

.. py:function:: pyc.Transform.Pz(list[list[pt, eta, phi, e]]) -> list[float]
    :no-index:

.. py:function:: pyc.Transform.PxPyPz(list[list[pt, eta, phi, e]]) -> list[list[float]]
    :no-index:

.. py:function:: pyc.Transform.PxPyPzE(list[list[pt, eta, phi, e]]) -> list[list[float]]
    :no-index:

.. py:function:: pyc.Transform.Pt(list[list[px, py, pz, e]]) -> list[float]
    :no-index:

.. py:function:: pyc.Transform.Eta(tlist[list[px, py, pz, e]] -> list[float]
    :no-index:

.. py:function:: pyc.Transform.Phi(list[list[px, py, pz, e]]) -> list[float]
    :no-index:

.. py:function:: pyc.Transform.PtEtaPhi(list[list[px, py, pz, e]]) -> list[list[float]]
    :no-index:

.. py:function:: pyc.Transform.PtEtaPhiE(list[list[px, py, pz, e]]) -> list[list[float]]
    :no-index:

Transformation for Separated Floats
===================================

.. py:function:: pyc.Transform.Px(float pt, float phi) -> float
    :no-index:

.. py:function:: pyc.Transform.Py(float pt, float phi) -> float
    :no-index:

.. py:function:: pyc.Transform.Pz(float pt, float eta) -> float
    :no-index:

.. py:function:: pyc.Transform.PxPyPz(float pt, float eta, float phi) -> list[float]
    :no-index:

.. py:function:: pyc.Transform.PxPyPzE(float pt, float eta, float phi, float e) -> list[float]
    :no-index:

.. py:function:: pyc.Transform.Pt(float px, float py) -> float
    :no-index:

.. py:function:: pyc.Transform.Eta(float px, float py, float pz) -> float
    :no-index:

.. py:function:: pyc.Transform.Phi(float px, float py) -> float
    :no-index:

.. py:function:: pyc.Transform.PtEtaPhi(float px, float py, float pz) -> list[float]
    :no-index:

.. py:function:: pyc.Transform.PtEtaPhiE(float px, float py, float pz, float e) -> list[float]
    :no-index:










