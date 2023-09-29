#include <torch/extension.h>

#ifndef H_OPERATORS_TENSORS
#define H_OPERATORS_TENSORS

namespace OperatorsTensors
{
	torch::Tensor Dot(torch::Tensor v1, torch::Tensor v2); 
	torch::Tensor CosTheta(torch::Tensor v1, torch::Tensor v2);
	torch::Tensor SinTheta(torch::Tensor v1, torch::Tensor v2); 
	torch::Tensor _SinTheta(torch::Tensor cos);

	// Rotation Matrix 
	torch::Tensor Rx(torch::Tensor angle); 
	torch::Tensor Ry(torch::Tensor angle);
	torch::Tensor Rz(torch::Tensor angle);

}
#endif

#ifndef H_CONSTANTS_TENSORS
#define H_CONSTANTS_TENSORS

namespace Constants
{
	torch::Tensor Pi_2(torch::Tensor v); 
}

#endif
