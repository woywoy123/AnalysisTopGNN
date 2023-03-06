#ifndef H_PHYSICS_CUDA
#define H_PHYSICS_CUDA

#include <torch/extension.h>
#include <utility>
torch::Tensor _P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
torch::Tensor _P(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 

torch::Tensor _Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
torch::Tensor _Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 

torch::Tensor _M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
torch::Tensor _M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 

torch::Tensor _Mt2(torch::Tensor pz, torch::Tensor e); 
torch::Tensor _Mt(torch::Tensor pz, torch::Tensor e); 

torch::Tensor _Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz);
torch::Tensor _DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2); 


#define CHECK_CUDA(x) TORCH_CHECK(x.device().is_cuda(), "#x must be on CUDA")
#define CHECK_CONTIGUOUS(x) TORCH_CHECK(x.is_contiguous(), "#x must be contiguous")
#define CHECK_INPUT(x) CHECK_CUDA(x); CHECK_CONTIGUOUS(x)

namespace PhysicsCUDA
{
	const std::vector<torch::Tensor> _format(std::vector<torch::Tensor> imp)
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


	const torch::Tensor P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
	{
		std::vector<torch::Tensor> _o = _format({px, py, pz});
		return _P2(_o[0], _o[1], _o[2]);
	}

	const torch::Tensor P(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
	{		
		std::vector<torch::Tensor> _o = _format({px, py, pz});
		return _P(_o[0], _o[1], _o[2]);
	}

	const torch::Tensor Beta2(
			torch::Tensor px, torch::Tensor py, 
			torch::Tensor pz, torch::Tensor e)
	{
		std::vector<torch::Tensor> _o = _format({px, py, pz, e}); 
		return _Beta2(_o[0], _o[1], _o[2], _o[3]);
	}

	const torch::Tensor Beta(
			torch::Tensor px, torch::Tensor py, 
			torch::Tensor pz, torch::Tensor e)
	{
		std::vector<torch::Tensor> _o = _format({px, py, pz, e});
		return _Beta(_o[0], _o[1], _o[2], _o[3]);
	}

	const torch::Tensor M2(
			torch::Tensor px, torch::Tensor py, 
			torch::Tensor pz, torch::Tensor e)
	{		
		std::vector<torch::Tensor> _o = _format({px, py, pz, e});
		return _M2(_o[0], _o[1], _o[2], _o[3]);
	}


	const torch::Tensor M(
			torch::Tensor px, torch::Tensor py, 
			torch::Tensor pz, torch::Tensor e)
	{
		std::vector<torch::Tensor> _o = _format({px, py, pz, e});
		return _M(_o[0], _o[1], _o[2], _o[3]);
	}

	const torch::Tensor Mt2(torch::Tensor pz, torch::Tensor e)
	{
		std::vector<torch::Tensor> _o = _format({pz, e});
		return _Mt2(_o[0], _o[1]);
	}


	const torch::Tensor Mt(torch::Tensor pz, torch::Tensor e)
	{
		std::vector<torch::Tensor> _o = _format({pz, e});
		return _Mt(_o[0], _o[1]);
	}

	const torch::Tensor Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
	{
		std::vector<torch::Tensor> _o = _format({px, py, pz});
		return _Theta(_o[0], _o[1], _o[2]);
	}

	const torch::Tensor DeltaR(
			torch::Tensor eta1, torch::Tensor eta2,
			torch::Tensor phi1, torch::Tensor phi2)
	{
		std::vector<torch::Tensor> _o = _format({eta1, eta2, phi1, phi2});
		return _DeltaR(_o[0], _o[1], _o[2], _o[3]);
	}
}
#endif
