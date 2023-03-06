#ifndef H_TRANSFORM_TOCARTESIAN_T
#define H_TRANSFORM_TOCARTESIAN_T

#include <torch/extension.h>

namespace TransformTensors
{
	torch::Tensor Px(torch::Tensor pt, torch::Tensor phi); 
	torch::Tensor Py(torch::Tensor pt, torch::Tensor phi); 
	torch::Tensor Pz(torch::Tensor pt, torch::Tensor eta); 
	torch::Tensor PxPyPz(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi);
}

#endif 
