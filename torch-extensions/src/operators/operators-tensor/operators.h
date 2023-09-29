#ifndef H_OPERATORS_TENSOR
#define H_OPERATORS_TENSOR
#include <torch/torch.h>

namespace Operators
{
    namespace Tensors
    {
        torch::Tensor Dot(torch::Tensor v1, torch::Tensor v2); 
        torch::Tensor Mul(torch::Tensor v1, torch::Tensor v2); 
        torch::Tensor CosTheta(torch::Tensor v1, torch::Tensor v2); 
        torch::Tensor SinTheta(torch::Tensor v1, torch::Tensor v2); 
        torch::Tensor Rx(torch::Tensor angle); 
        torch::Tensor Ry(torch::Tensor angle); 
        torch::Tensor Rz(torch::Tensor angle); 
        torch::Tensor CoFactors(torch::Tensor matrix); 
        torch::Tensor Determinant(torch::Tensor matrix); 
        torch::Tensor Inverse(torch::Tensor matrix); 
    }
}
#endif

