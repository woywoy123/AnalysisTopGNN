#ifndef H_TRANSFORM_TENSORS_CARTESIAN
#define H_TRANSFORM_TENSORS_CARTESIAN
#include <torch/torch.h>

namespace Transform
{
    namespace Tensors
    {
	    torch::Tensor Px(torch::Tensor pt, torch::Tensor phi); 
	    torch::Tensor Py(torch::Tensor pt, torch::Tensor phi); 
	    torch::Tensor Pz(torch::Tensor pt, torch::Tensor eta); 
	    torch::Tensor PxPyPz(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi);
        torch::Tensor PxPyPzE(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor E); 

	    torch::Tensor Px(torch::Tensor pmu); 
	    torch::Tensor Py(torch::Tensor pmu); 
	    torch::Tensor Pz(torch::Tensor pmu); 
	    torch::Tensor PxPyPz(torch::Tensor pmu);
        torch::Tensor PxPyPzE(torch::Tensor pmu); 
    }
}

#endif
