#ifndef H_TRANSFORM_TOPOLAR_C
#define H_TRANSFORM_TOPOLAR_C

#include <torch/extension.h>
torch::Tensor _Pt(torch::Tensor _px, torch::Tensor _py);  
torch::Tensor _Phi(torch::Tensor _px, torch::Tensor _py); 
torch::Tensor _Eta(torch::Tensor _px, torch::Tensor _py, torch::Tensor _pz);
torch::Tensor _PtEtaPhi(torch::Tensor _px, torch::Tensor _py, torch::Tensor _pz);

#define CHECK_CUDA(x) TORCH_CHECK(x.device().is_cuda(), "#x must be on CUDA")
#define CHECK_CONTIGUOUS(x) TORCH_CHECK(x.is_contiguous(), "#x must be contiguous")
#define CHECK_INPUT(x) CHECK_CUDA(x); CHECK_CONTIGUOUS(x)

namespace TransformCUDA
{
	const std::vector<torch::Tensor> _Pcheck(std::vector<torch::Tensor> imp)
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

	const torch::Tensor PT(torch::Tensor px, torch::Tensor py)
	{
		std::vector<torch::Tensor> _o = _Pcheck({px, py}); 
		return _Pt(_o[0], _o[1]); 
	}

	const torch::Tensor Phi(torch::Tensor px, torch::Tensor py)
	{
		std::vector<torch::Tensor> _o = _Pcheck({px, py}); 
		return _Phi(_o[0], _o[1]); 
	}

	const torch::Tensor Eta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
	{
		std::vector<torch::Tensor> _o = _Pcheck({px, py, pz}); 
		return _Eta(_o[0], _o[1], _o[2]);  
	}

	const torch::Tensor PtEtaPhi(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
	{
		std::vector<torch::Tensor> _o = _Pcheck({px, py, pz}); 
		return _PtEtaPhi(_o[0], _o[1], _o[2]); 
	}
}

#endif 
