Torch Extension Modules (pyc) C++ Interfaces
********************************************

This section of the documentation provides a complete mapping of the C++/CUDA headers, which can be linked to other external packages.

Transformation Module
_____________________

.. code:: C++ 

   // headers for the CPU only version
   #include <transform/cartesian-tensors/cartesian.h>
   #include <transform/polar-tensors/polar.h>

   // headers for the CUDA versions
   #include <transform/cartesian-cuda/cartesian.h>
   #include <transform/polar-cuda/polar.h>


.. cpp:function:: torch::Tensor pyc::transform::separate::Pt(torch::Tensor px, torch::Tensor pz); 
.. cpp:function:: torch::Tensor pyc::transform::separate::Eta(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 

.. cpp:function:: torch::Tensor pyc::transform::separate::Phi(torch::Tensor px, torch::Tensor py); 
.. cpp:function:: torch::Tensor pyc::transform::separate::PtEtaPhi(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
.. cpp:function:: torch::Tensor pyc::transform::separate::PtEtaPhiE(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);

.. cpp:function:: torch::Tensor pyc::transform::separate::Px(torch::Tensor pt, torch::Tensor phi); 
.. cpp:function:: torch::Tensor pyc::transform::separate::Py(torch::Tensor pt, torch::Tensor phi); 
.. cpp:function:: torch::Tensor pyc::transform::separate::Pz(torch::Tensor pt, torch::Tensor eta); 

.. cpp:function:: torch::Tensor pyc::transform::separate::PxPyPz(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi); 
.. cpp:function:: torch::Tensor pyc::transform::separate::PxPyPzE(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e); 

.. cpp:function:: torch::Tensor pyc::transform::combined::Pt(torch::Tensor pmc); 
.. cpp:function:: torch::Tensor pyc::transform::combined::Eta(torch::Tensor pmc);
.. cpp:function:: torch::Tensor pyc::transform::combined::Phi(torch::Tensor pmc);
 
.. cpp:function:: torch::Tensor pyc::transform::combined::PtEtaPhi(torch::Tensor pmc); 
.. cpp:function:: torch::Tensor pyc::transform::combined::PtEtaPhiE(torch::Tensor pmc);

.. cpp:function:: torch::Tensor pyc::transform::combined::Px(torch::Tensor pmu); 
.. cpp:function:: torch::Tensor pyc::transform::combined::Py(torch::Tensor pmu); 
.. cpp:function:: torch::Tensor pyc::transform::combined::Pz(torch::Tensor pmu); 

.. cpp:function:: torch::Tensor pyc::transform::combined::PxPyPz(torch::Tensor pmu); 
.. cpp:function:: torch::Tensor pyc::transform::combined::PxPyPzE(torch::Tensor pmu);

Physics Module
______________

.. code:: C++

   // headers for the CPU only version 
   #include <physics/physics-tensor/physics.h>
   #include <physics/physics-tensor/polar.h>
   #include <physics/physics-tensor/cartesian.h>

   // headers for the CUDA versions
   #include <physics/physics-cuda/physics.h>
   #include <physics/physics-cuda/cartesian.h>
   #include <physics/physics-cuda/polar.h>

.. cpp:function:: torch::Tensor pyc::physics::cartesian::separate::P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
.. cpp:function:: torch::Tensor pyc::physics::cartesian::separate::P(torch::Tensor px, torch::Tensor py, torch::Tensor pz);

.. cpp:function:: torch::Tensor pyc::physics::cartesian::separate::Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);
.. cpp:function:: torch::Tensor pyc::physics::cartesian::separate::Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);

.. cpp:function:: torch::Tensor pyc::physics::cartesian::separate::M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);
.. cpp:function:: torch::Tensor pyc::physics::cartesian::separate::M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);

.. cpp:function:: torch::Tensor pyc::physics::cartesian::separate::Mt2(torch::Tensor pz, torch::Tensor e);
.. cpp:function:: torch::Tensor pyc::physics::cartesian::separate::Mt(torch::Tensor pz, torch::Tensor e);

.. cpp:function:: torch::Tensor pyc::physics::cartesian::separate::Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
.. cpp:function:: torch::Tensor pyc::physics::cartesian::separate::DeltaR(torch::Tensor px1, torch::Tensor px2, torch::Tensor py1, torch::Tensor py2, torch::Tensor pz1, torch::Tensor pz2);

.. cpp:function:: torch::Tensor pyc::physics::cartesian::combined::P2(torch::Tensor pmc); 
.. cpp:function:: torch::Tensor pyc::physics::cartesian::combined::P(torch::Tensor pmc); 

.. cpp:function:: torch::Tensor pyc::physics::cartesian::combined::Beta2(torch::Tensor pmc); 
.. cpp:function:: torch::Tensor pyc::physics::cartesian::combined::Beta(torch::Tensor pmc); 

.. cpp:function:: torch::Tensor pyc::physics::cartesian::combined::M2(torch::Tensor pmc);
.. cpp:function:: torch::Tensor pyc::physics::cartesian::combined::M(torch::Tensor pmc);

.. cpp:function:: torch::Tensor pyc::physics::cartesian::combined::Mt2(torch::Tensor pmc);
.. cpp:function:: torch::Tensor pyc::physics::cartesian::combined::Mt(torch::Tensor pmc);

.. cpp:function:: torch::Tensor pyc::physics::cartesian::combined::Theta(torch::Tensor pmc); 
.. cpp:function:: torch::Tensor pyc::physics::cartesian::combined::DeltaR(torch::Tensor pmc1, torch::Tensor pmc2); 

.. cpp:function:: torch::Tensor pyc::physics::polar::separate::P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
.. cpp:function:: torch::Tensor pyc::physics::polar::separate::P(torch::Tensor px, torch::Tensor py, torch::Tensor pz);

.. cpp:function:: torch::Tensor pyc::physics::polar::separate::Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);
.. cpp:function:: torch::Tensor pyc::physics::polar::separate::Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);

.. cpp:function:: torch::Tensor pyc::physics::polar::separate::M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);
.. cpp:function:: torch::Tensor pyc::physics::polar::separate::M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);

.. cpp:function:: torch::Tensor pyc::physics::polar::separate::Mt2(torch::Tensor pz, torch::Tensor e);
.. cpp:function:: torch::Tensor pyc::physics::polar::separate::Mt(torch::Tensor pz, torch::Tensor e);

.. cpp:function:: torch::Tensor pyc::physics::polar::separate::Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
.. cpp:function:: torch::Tensor pyc::physics::polar::separate::DeltaR(torch::Tensor px1, torch::Tensor px2, torch::Tensor py1, torch::Tensor py2, torch::Tensor pz1, torch::Tensor pz2);

.. cpp:function:: torch::Tensor pyc::physics::polar::combined::P2(torch::Tensor pmc); 
.. cpp:function:: torch::Tensor pyc::physics::polar::combined::P(torch::Tensor pmc); 

.. cpp:function:: torch::Tensor pyc::physics::polar::combined::Beta2(torch::Tensor pmc); 
.. cpp:function:: torch::Tensor pyc::physics::polar::combined::Beta(torch::Tensor pmc); 

.. cpp:function:: torch::Tensor pyc::physics::polar::combined::M2(torch::Tensor pmc);
.. cpp:function:: torch::Tensor pyc::physics::polar::combined::M(torch::Tensor pmc);

.. cpp:function:: torch::Tensor pyc::physics::polar::combined::Mt2(torch::Tensor pmc);
.. cpp:function:: torch::Tensor pyc::physics::polar::combined::Mt(torch::Tensor pmc);

.. cpp:function:: torch::Tensor pyc::physics::polar::combined::Theta(torch::Tensor pmc); 
.. cpp:function:: torch::Tensor pyc::physics::polar::combined::DeltaR(torch::Tensor pmc1, torch::Tensor pmc2); 


Operator Module
_______________

.. code:: C++

   // headers for the CPU only version 
   #include <operators/operators-tensor/operators.h>

   // headers for the CUDA versions
   #include <operators/operators-cuda/cartesian.h>

.. cpp:function:: torch::Tensor pyc::operators::Dot(torch::Tensor v1, torch::Tensor v2); 
.. cpp:function:: torch::Tensor pyc::operators::Mul(torch::Tensor v1, torch::Tensor v2); 

.. cpp:function:: torch::Tensor pyc::operators::CosTheta(torch::Tensor v1, torch::Tensor v2); 
.. cpp:function:: torch::Tensor pyc::operators::SinTheta(torch::Tensor v1, torch::Tensor v2);

.. cpp:function:: torch::Tensor pyc::operators::Rx(torch::Tensor angle); 
.. cpp:function:: torch::Tensor pyc::operators::Ry(torch::Tensor angle); 
.. cpp:function:: torch::Tensor pyc::operators::Rz(torch::Tensor angle); 

.. cpp:function:: torch::Tensor pyc::operators::CoFactors(torch::Tensor matrix);
.. cpp:function:: torch::Tensor pyc::operators::Determinant(torch::Tensor matrix); 
.. cpp:function:: torch::Tensor pyc::operators::Inverse(torch::Tensor matrix); 
.. cpp:function:: torch::Tensor pyc::operators::Cross(torch::Tensor mat1, torch::Tensor mat2);


Double and Single Neutrino Reconstruction Module
________________________________________________

.. code:: C++

   // headers for the CPU only version 
   #include <nusol/nusol-tensor/nusol.h>

   // headers for the CUDA versions
   #include <nusol/nusol-cuda/nusol.h>

.. cpp:function:: torch::Tensor pyc::nusol::BaseMatrix(torch::Tensor pmc_b, torch::Tensor pmc_mu, torch::Tensor masses); 
.. cpp:function:: std::tuple<torch::Tensor, torch::Tensor> pyc::nusol::Intersection(torch::Tensor A, torch::Tensor B, const double null); 
.. cpp:function:: std::vector<torch::Tensor> pyc::nusol::Nu(torch::Tensor pmc_b, torch::Tensor pmc_mu, torch::Tensor met_xy, torch::Tensor masses, torch::Tensor sigma, const double null); 
.. cpp:function:: std::vector<torch::Tensor> pyc::nusol::NuNu(torch::Tensor pmc_b1, torch::Tensor pmc_b2, torch::Tensor pmc_l1, torch::Tensor pmc_l2, torch::Tensor met_xy, torch::Tensor masses, const double null); 

.. cpp:function:: std::vector<torch::Tensor> pyc::nusol::polar::combined::Nu(torch::Tensor pmu_b, torch::Tensor pmu_mu, torch::Tensor met_phi, torch::Tensor masses, torch::Tensor sigma, const double null);                              
.. cpp:function:: std::vector<torch::Tensor> pyc::nusol::polar::combined::NuNu(torch::Tensor pmu_b1 , torch::Tensor pmu_b2, torch::Tensor pmu_mu1, torch::Tensor pmu_mu2, torch::Tensor met_phi, torch::Tensor masses, const double null); 

.. cpp:function:: std::vector<torch::Tensor> pyc::nusol::polar::separate::Nu(torch::Tensor pt_b, torch::Tensor eta_b, torch::Tensor phi_b, torch::Tensor e_b, torch::Tensor pt_mu, torch::Tensor eta_mu, torch::Tensor phi_mu, torch::Tensor e_mu, torch::Tensor met, torch::Tensor phi, torch::Tensor masses, torch::Tensor sigma, const double null); 

.. cpp:function:: std::vector<torch::Tensor> pyc::nusol::polar::separate::NuNu(torch::Tensor pt_b1, torch::Tensor eta_b1, torch::Tensor phi_b1, torch::Tensor e_b1, torch::Tensor pt_b2, torch::Tensor eta_b2, torch::Tensor phi_b2, torch::Tensor e_b2, torch::Tensor pt_mu1, torch::Tensor eta_mu1, torch::Tensor phi_mu1, torch::Tensor e_mu1, torch::Tensor pt_mu2, torch::Tensor eta_mu2, torch::Tensor phi_mu2, torch::Tensor e_mu2, torch::Tensor met, torch::Tensor phi, torch::Tensor masses, const double null); 

.. cpp:function:: std::vector<torch::Tensor> pyc::nusol::cartesian::combined::Nu(torch::Tensor pmc_b, torch::Tensor pmc_mu, torch::Tensor met_xy, torch::Tensor masses, torch::Tensor sigma, const double null); 
.. cpp:function:: std::vector<torch::Tensor> pyc::nusol::cartesian::combined::NuNu(torch::Tensor pmc_b1, torch::Tensor pmc_b2, torch::Tensor pmc_mu1, torch::Tensor pmc_mu2,torch::Tensor met_xy, torch::Tensor masses, const double null); 

.. cpp:function:: std::vector<torch::Tensor> pyc::nusol::cartesian::separate::Nu(torch::Tensor px_b , torch::Tensor py_b , torch::Tensor pz_b , torch::Tensor e_b, torch::Tensor px_mu, torch::Tensor py_mu, torch::Tensor pz_mu, torch::Tensor e_mu, torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, torch::Tensor sigma, const double null); 

.. cpp:function:: std::vector<torch::Tensor> pyc::nusol::cartesian::separate::NuNu(torch::Tensor px_b1, torch::Tensor py_b1, torch::Tensor pz_b1, torch::Tensor e_b1, torch::Tensor px_b2, torch::Tensor py_b2, torch::Tensor pz_b2, torch::Tensor e_b2, torch::Tensor px_mu1, torch::Tensor py_mu1, torch::Tensor pz_m1, torch::Tensor e_mu1, torch::Tensor px_mu2, torch::Tensor py_mu2, torch::Tensor pz_mu2, torch::Tensor e_mu2, torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, const double null); 
                
.. cpp:function:: std::vector<std::vector<torch::Tensor>> pyc::graph::dress(std::map<std::string, std::vector<torch::Tensor>> inpt); 
.. cpp:function:: std::vector<std::vector<torch::Tensor>> pyc::graph::edge_aggregation(torch::Tensor edge_index, torch::Tensor prediction, torch::Tensor node_feature, const bool include_zero); 
.. cpp:function:: std::vector<std::vector<torch::Tensor>> pyc::graph::node_aggregation(torch::Tensor edge_index, torch::Tensor prediction, torch::Tensor node_feature, const bool include_zero); 

.. cpp:function:: std::vector<std::vector<torch::Tensor>> pyc::graph::polar::combined::edge_pmu(torch::Tensor edge_index, torch::Tensor prediction, torch::Tensor pmu, const bool include_zero); 
.. cpp:function:: std::vector<std::vector<torch::Tensor>> pyc::graph::polar::combined::node_pmu(torch::Tensor edge_index, torch::Tensor prediction, torch::Tensor pmu, const bool include_zero); 

.. cpp:function:: std::vector<std::vector<torch::Tensor>> pyc::graph::polar::separate::edge_pmu(torch::Tensor edge_index, torch::Tensor prediction, torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  const bool include_zero); 
.. cpp:function:: std::vector<std::vector<torch::Tensor>> pyc::graph::polar::separate::node_pmu(torch::Tensor edge_index, torch::Tensor prediction, torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  const bool include_zero);  
.. cpp:function:: std::vector<std::vector<torch::Tensor>> pyc::graph::cartesian::combined::edge_pmc(torch::Tensor edge_index, torch::Tensor prediction, torch::Tensor pmc, const bool include_zero); 
.. cpp:function:: std::vector<std::vector<torch::Tensor>> pyc::graph::cartesian::combined::node_pmc(torch::Tensor edge_index, torch::Tensor prediction, torch::Tensor pmc, const bool include_zero);  
.. cpp:function:: std::vector<std::vector<torch::Tensor>> pyc::graph::cartesian::separate::edge_pmc(torch::Tensor edge_index, torch::Tensor prediction, torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  const bool include_zero); 
.. cpp:function:: std::vector<std::vector<torch::Tensor>> pyc::graph::cartesian::separate::node_pmc(torch::Tensor edge_index, torch::Tensor prediction, torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  const bool include_zero);  
