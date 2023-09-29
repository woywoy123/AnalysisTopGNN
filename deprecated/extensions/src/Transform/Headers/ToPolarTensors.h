#ifndef H_TRANSFORM_TOPOLAR_T
#define H_TRANSFORM_TOPOLAR_T

#include<torch/extension.h>

namespace TransformTensors
{
	torch::Tensor PT(torch::Tensor px, torch::Tensor py); 
	torch::Tensor Phi(torch::Tensor px, torch::Tensor py);
	torch::Tensor Eta(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
	torch::Tensor _Eta(torch::Tensor pt, torch::Tensor pz); 
	torch::Tensor PtEtaPhi(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
}

#endif
