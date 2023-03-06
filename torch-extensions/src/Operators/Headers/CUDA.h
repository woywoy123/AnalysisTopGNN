#ifndef H_OPERATORS_CUDA
#define H_OPERATORS_CUDA

#include <torch/extension.h>

torch::Tensor _Dot(torch::Tensor v1, torch::Tensor v2);
torch::Tensor _CosTheta(torch::Tensor v1, torch::Tensor v2);
torch::Tensor _Rx(torch::Tensor angle); 
torch::Tensor _Ry(torch::Tensor angle); 
torch::Tensor _Rz(torch::Tensor angle); 
torch::Tensor _Mul(torch::Tensor v1, torch::Tensor v2); 
torch::Tensor _Cofactors(torch::Tensor v1); 
torch::Tensor _Determinant(torch::Tensor cofact, torch::Tensor Matrix);
torch::Tensor _Inverse(torch::Tensor cofact, torch::Tensor Dets);
torch::Tensor _inv(torch::Tensor Matrix); 
torch::Tensor _det(torch::Tensor Matrix); 

#define CHECK_CUDA(x) TORCH_CHECK(x.device().is_cuda(), "#x must be on CUDA")
#define CHECK_CONTIGUOUS(x) TORCH_CHECK(x.is_contiguous(), "#x must be contiguous")
#define CHECK_INPUT(x) CHECK_CUDA(x); CHECK_CONTIGUOUS(x)

namespace OperatorsCUDA
{
	const void _CheckTensors(std::vector<torch::Tensor> T){for (torch::Tensor x : T){CHECK_INPUT(x);}}
	const torch::Tensor TransferToCUDA(std::vector<double> inpt)
	{
		torch::TensorOptions op = torch::TensorOptions().dtype(torch::kFloat64); 
		torch::Tensor v = torch::from_blob(inpt.data(), {(int)inpt.size()}, op); 
		v = v.view({-1, 1}).clone(); 
		v = v.to(torch::kCUDA); 
		CHECK_INPUT(v); 
		return v; 
	}

	const torch::Tensor CosTheta(torch::Tensor v1, torch::Tensor v2)
	{
		_CheckTensors({v1, v2}); 
		return _CosTheta(v1, v2); 
	}

	const torch::Tensor _SinTheta(torch::Tensor cos)
	{
		return torch::sqrt(1 - _Dot(cos, cos)); 
	}

	const torch::Tensor SinTheta(torch::Tensor v1, torch::Tensor v2)
	{

		_CheckTensors({v1, v2}); 
		return _SinTheta(_CosTheta(v1, v2)); 
	}

	const torch::Tensor Rx(torch::Tensor angle)
	{
		CHECK_INPUT(angle);
		return _Rx(angle); 
	}

	const torch::Tensor Ry(torch::Tensor angle)
	{
		CHECK_INPUT(angle);
		return _Ry(angle); 
	}

	const torch::Tensor Rz(torch::Tensor angle)
	{
		CHECK_INPUT(angle);
		return _Rz(angle); 
	}

	const torch::Tensor Dot(torch::Tensor v1, torch::Tensor v2)
	{ 
		_CheckTensors({v1, v1}); 
		return _Dot(v1, v2).sum({-1}, true);
	}

	const torch::Tensor Mul(torch::Tensor v1, torch::Tensor v2)
	{ 
		_CheckTensors({v1, v2}); 
		return _Mul(v1, v2); 
	}

	const torch::Tensor Cofactors(torch::Tensor v1)
	{
		_CheckTensors({v1}); 
		return _Cofactors(v1); 
	}

	const torch::Tensor Determinant(torch::Tensor Cofactors, torch::Tensor Matrix)
	{ 
		_CheckTensors({Cofactors, Matrix}); 
		return _Determinant(Cofactors, Matrix); 
	}

	const torch::Tensor Inverse(torch::Tensor Cofactors, torch::Tensor dets)
	{
		_CheckTensors({Cofactors, dets}); 
		return _Inverse(Cofactors, dets);
	}

	const torch::Tensor Inv(torch::Tensor matrix)
	{
		CHECK_INPUT(matrix);
		return _inv(matrix);
	}

	const torch::Tensor Det(torch::Tensor Matrix)
	{
		CHECK_INPUT(Matrix);
		return _det(Matrix); 
	}


}

#endif 
