#include <torch/extension.h>
#include <iostream>
#include <vector>

using namespace torch::indexing;

float Px(float pt, float phi){ return pt*std::cos(phi); }
float Py(float pt, float phi){ return pt*std::sin(phi); }
float Pz(float pt, float eta){ return pt*std::sinh(eta); }

torch::Tensor ToPxPyPzE(float pt, float eta, float phi, float e, std::string device)
{
  torch::TensorOptions options = torch::TensorOptions().dtype(torch::kFloat64); 
  if (device == "cuda"){ options = options.device(torch::kCUDA); }
  return torch::tensor({Px(pt, phi), Py(pt, phi), Pz(pt, eta), e}, options);
}

torch::Tensor ListToPxPyPzE(std::vector<std::vector<float>> P_mu_List, std::string device)
{
  torch::TensorOptions options = torch::TensorOptions().dtype(torch::kFloat64); 
  if (device == "cuda"){ options = options.device(torch::kCUDA); }

  std::vector<torch::Tensor> Output; 
  for (unsigned int i(0); i < P_mu_List.size(); i++)
  {
    Output.push_back(ToPxPyPzE(P_mu_List[i][0], P_mu_List[i][1], P_mu_List[i][2], P_mu_List[i][3], device)); 
  }
  return torch::stack(Output).to(options);
}

torch::Tensor TensorToPxPyPzE(torch::Tensor v)
{

  v = v.view({-1, 4});
  
  torch::Tensor pt = v.index({Slice(), Slice(0, 1, 1)}); 
  torch::Tensor eta = v.index({Slice(), Slice(1, 2, 2)}); 
  torch::Tensor phi = v.index({Slice(), Slice(2, 3, 3)}); 
  torch::Tensor e = v.index({Slice(), Slice(3, 4, 4)}); 

  torch::Tensor px = pt*torch::cos(phi); 
  torch::Tensor py = pt*torch::sin(phi); 
  torch::Tensor pz = pt*torch::sinh(eta); 

  return torch::cat({px, py, pz, e}, 1); 
}

torch::Tensor MassFromPxPyPzE(torch::Tensor v)
{
  v = v.pow(2);  
  v = v.view({-1, 4});
  
  torch::Tensor px = v.index({Slice(), Slice(0, 1, 1)}); 
  torch::Tensor py = v.index({Slice(), Slice(1, 2, 2)}); 
  torch::Tensor pz = v.index({Slice(), Slice(2, 3, 3)}); 
  torch::Tensor e = v.index({Slice(), Slice(3, 4, 4)}); 
  
  torch::Tensor s2 = e - px - py - pz;
  return torch::sqrt(s2.abs()); 
}

torch::Tensor MassFromPtEtaPhiE(torch::Tensor v)
{
  v = TensorToPxPyPzE(v); 
  torch::Tensor px = v.index({Slice(), Slice(0, 1, 1)}); 
  torch::Tensor py = v.index({Slice(), Slice(1, 2, 2)}); 
  torch::Tensor pz = v.index({Slice(), Slice(2, 3, 3)}); 
  torch::Tensor e  = v.index({Slice(), Slice(3, 4, 4)}); 
  torch::Tensor s2 = e.pow(2) - px.pow(2) - py.pow(2) - pz.pow(2);
  return torch::sqrt(s2.abs()); 
}

torch::Tensor TensorToPtEtaPhiE(torch::Tensor v)
{

  v = v.view({-1, 4});
  
  torch::Tensor px = v.index({Slice(), Slice(0, 1, 1)}); 
  torch::Tensor py = v.index({Slice(), Slice(1, 2, 2)}); 
  torch::Tensor pz = v.index({Slice(), Slice(2, 3, 3)}); 
  torch::Tensor e = v.index({Slice(), Slice(3, 4, 4)}); 
  
  torch::Tensor pt = torch::sqrt(torch::pow(px,2) + torch::pow(py, 2)); 
  torch::Tensor phi = torch::atan2(py, px); 
  torch::Tensor eta = torch::arcsinh(pz/pt);
  return torch::cat({pt, eta, phi, e}, 1); 
}

torch::Tensor TensorDeltaR(torch::Tensor v1, torch::Tensor v2)
{
  torch::Tensor eta1 = v1.index({Slice(), Slice(1, 2, 2)}); 
  torch::Tensor phi1 = v1.index({Slice(), Slice(2, 3, 3)}); 

  torch::Tensor eta2 = v2.index({Slice(), Slice(1, 2, 2)}); 
  torch::Tensor phi2 = v2.index({Slice(), Slice(2, 3, 3)}); 

  return torch::sqrt((eta1-eta2).pow(2) + (phi1 - phi2).pow(2)); 
}



PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
  m.def("ToPxPyPzE", &ToPxPyPzE, "Convert Rapidity to Cartesian"); 
  m.def("ListToPxPyPzE", &ListToPxPyPzE, "Convert Rapidity to Cartesian");
  m.def("MassFromPxPyPzE", &MassFromPxPyPzE, "Calculate Invariant Mass");
  m.def("MassFromPtEtaPhiE", &MassFromPtEtaPhiE, "Calculate Invariant Mass");
  m.def("TensorToPxPyPzE", &TensorToPxPyPzE, "Convert Rapidity Tensor to Cartesian");
  m.def("TensorToPtEtaPhiE", &TensorToPtEtaPhiE, "Convert Cartesian to Rapidity"); 
  m.def("TensorDeltaR", &TensorDeltaR, "Calculate the DeltaR between objects");
  m.def("ToPx", &Px, "Convert to Cartesian");
  m.def("ToPy", &Py, "Convert to Cartesian");
  m.def("ToPz", &Pz, "Convert to Cartesian");
}
