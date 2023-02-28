#ifndef H_PHYSICS_TENSORS
#define H_PHYSICS_TENSORS

#include <torch/extension.h>
#include <iostream>

namespace PhysicsTensors
{
	static torch::TensorOptions Options(torch::Tensor ten)
	{
		return torch::TensorOptions().device(ten.device()).dtype(ten.dtype()); 
	}
        static torch::Tensor Slicer(torch::Tensor Vector, int sdim, int edim)
        {
        	return Vector.index({torch::indexing::Slice(), torch::indexing::Slice(sdim, edim)});
        }

	static torch::Tensor ToPx(torch::Tensor pt, torch::Tensor phi){ return pt*torch::cos(phi); }
	static torch::Tensor ToPy(torch::Tensor pt, torch::Tensor phi){ return pt*torch::sin(phi); }
	static torch::Tensor ToPz(torch::Tensor pt, torch::Tensor eta){ return pt*torch::sinh(eta); }


	torch::Tensor ToPxPyPzE(torch::Tensor Polar); 
	torch::Tensor ToPxPyPz(torch::Tensor Polar); 

	torch::Tensor Rx(torch::Tensor angle);
	torch::Tensor Ry(torch::Tensor angle);
	torch::Tensor Rz(torch::Tensor angle);

	torch::Tensor ToThetaCartesian(torch::Tensor Cartesian); 
	torch::Tensor ToThetaPolar(torch::Tensor Polar); 
	
	torch::Tensor Mass2Polar(torch::Tensor Polar); 
	torch::Tensor MassPolar(torch::Tensor Polar); 

	torch::Tensor Mass2Cartesian(torch::Tensor Cartesian);
	torch::Tensor MassCartesian(torch::Tensor Cartesian); 

	torch::Tensor P2Cartesian(torch::Tensor Cartesian);
	torch::Tensor PCartesian(torch::Tensor Cartesian);

	torch::Tensor P2Polar(torch::Tensor Polar); 
	torch::Tensor PPolar(torch::Tensor Polar); 
	
	torch::Tensor BetaPolar(torch::Tensor Polar); 
	torch::Tensor BetaCartesian(torch::Tensor Cartesian);

	torch::Tensor Beta2Polar(torch::Tensor Polar); 
	torch::Tensor Beta2Cartesian(torch::Tensor Cartesian);

	torch::Tensor CosThetaCartesian(torch::Tensor CV1, torch::Tensor CV2);
	torch::Tensor SinThetaCartesian(torch::Tensor CV1, torch::Tensor CV2);
}
#endif

