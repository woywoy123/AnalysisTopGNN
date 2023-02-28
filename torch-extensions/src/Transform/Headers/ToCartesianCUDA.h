#ifndef H_TRANSFORM_TOCARTESIAN_C
#define H_TRANSFORM_TOCARTESIAN_C

#include <torch/extension.h>
torch::Tensor _Px(torch::Tensor _pt, torch::Tensor _phi); 
torch::Tensor _Py(torch::Tensor _pt, torch::Tensor _phi);
torch::Tensor _Pz(torch::Tensor _pt, torch::Tensor _eta);
torch::Tensor _PxPyPz(torch::Tensor _pt, torch::Tensor _eta, torch::Tensor _phi);

#define CHECK_CUDA(x) TORCH_CHECK(x.device().is_cuda(), "#x must be on CUDA")
#define CHECK_CONTIGUOUS(x) TORCH_CHECK(x.is_contiguous(), "#x must be contiguous")
#define CHECK_INPUT(x) CHECK_CUDA(x); CHECK_CONTIGUOUS(x)

namespace TransformCUDA
{
	const std::vector<torch::Tensor> _Ccheck(std::vector<torch::Tensor> imp)
	{
		std::vector<torch::Tensor> out; 
		for (torch::Tensor x : imp)
		{ 
			x = x.view({-1, 1}).contiguous(); 
			CHECK_INPUT(x); 
			out.push_back(x); 
		}
		return out; 
	}

	const torch::Tensor Px(torch::Tensor pt, torch::Tensor phi)
	{
		std::vector<torch::Tensor> _o = _Ccheck({pt, phi}); 
		return _Px(_o[0], _o[1]); 
	}

	const torch::Tensor Py(torch::Tensor pt, torch::Tensor phi)
	{
		std::vector<torch::Tensor> _o = _Ccheck({pt, phi}); 
		return _Py(_o[0], _o[1]); 
	}

	const torch::Tensor Pz(torch::Tensor pt, torch::Tensor eta)
	{
		std::vector<torch::Tensor> _o = _Ccheck({pt, eta}); 
		return _Pz(_o[0], _o[1]); 
	}

	const torch::Tensor PxPyPz(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
	{
		std::vector<torch::Tensor> _o = _Ccheck({pt, eta, phi}); 
		return _PxPyPz(_o[0], _o[1], _o[2]); 
	}
}

#endif 
