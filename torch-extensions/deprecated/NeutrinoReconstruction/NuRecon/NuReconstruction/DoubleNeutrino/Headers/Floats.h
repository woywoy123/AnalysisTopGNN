#ifndef H_SINGLENU_FLOATS
#define H_SINGLENU_FLOATS

#include <torch/extension.h>
#include <iostream>
#include "../../Physics/Floats/Headers/PhysicsFloats.h"
#include "../../Physics/Tensors/Headers/PhysicsTensors.h"
#include "../../NuSolutions/Headers/NuSolTensors.h"

namespace DoubleNu
{
	namespace Tensors
	{
		std::vector<torch::Tensor> Init(
			torch::Tensor _b1, torch::Tensor _b2,
			torch::Tensor _mu1, torch::Tensor _mu2,
			torch::Tensor massTop, torch::Tensor massW, torch::Tensor massNu,
			torch::Tensor met, torch::Tensor phi, float cutoff); 
		
		torch::Tensor N(torch::Tensor H); 
		torch::Tensor V0(torch::Tensor metx, torch::Tensor mety);
		torch::Tensor H_Perp(torch::Tensor H); 

		static torch::Tensor V0Polar(torch::Tensor met, torch::Tensor phi)
		{
			return V0(
				PhysicsTensors::ToPx(met, phi), 
				PhysicsTensors::ToPy(met, phi)); 
		}



	}
}


#endif 
