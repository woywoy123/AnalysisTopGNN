#ifndef H_SINGLENU_FLOATS
#define H_SINGLENU_FLOATS

#include <torch/extension.h>
#include <iostream>
#include "../../Physics/Floats/Headers/PhysicsFloats.h"
#include "../../Physics/Tensors/Headers/PhysicsTensors.h"
#include "../../NuSolutions/Headers/NuSolTensors.h"

namespace SingleNu
{
	namespace Tensors
	{
		torch::Tensor Sigma2(
				torch::Tensor sxx, torch::Tensor sxy, 
				torch::Tensor syx, torch::Tensor syy);
		torch::Tensor V0(torch::Tensor metx, torch::Tensor mety);

		std::vector<torch::Tensor> Init(
			torch::Tensor _b, torch::Tensor _mu, 
			torch::Tensor massTop, torch::Tensor massW, torch::Tensor massNu,
			torch::Tensor met, torch::Tensor phi, 
			torch::Tensor Sxx, torch::Tensor Sxy, torch::Tensor Syx, torch::Tensor Syy); 
	
		static torch::Tensor V0Polar(torch::Tensor met, torch::Tensor phi)
		{
			return V0(
				PhysicsTensors::ToPx(met, phi), 
				PhysicsTensors::ToPy(met, phi)); 
		}

		static torch::Tensor Rotation(
				torch::Tensor b_, torch::Tensor mu_)
		{
			return NuSolutionTensors::Rotation(b_, mu_); 
		}

		static torch::Tensor H(
				torch::Tensor b_, torch::Tensor mu_, 
				torch::Tensor massTop, torch::Tensor massW, 
				torch::Tensor massNu)
		{
			return NuSolutionTensors::H(b_, mu_, massTop, massW, massNu); 
		}
	}

	namespace Floats
	{
		static torch::Tensor Sigma2(
				double sxx, double sxy, 
				double syx, double syy, std::string device)
		{	
			return SingleNu::Tensors::Sigma2(
					PhysicsFloats::ToTensor(sxx, device), 
					PhysicsFloats::ToTensor(sxy, device),
					PhysicsFloats::ToTensor(syx, device),
					PhysicsFloats::ToTensor(syy, device)); 
		}

		static torch::Tensor V0(
				double metx, double mety, std::string device)
		{
			return SingleNu::Tensors::V0(
					PhysicsFloats::ToTensor(metx, device), 
					PhysicsFloats::ToTensor(mety, device)); 
		}

		static torch::Tensor Rotation(
				double b_pt, double b_eta, double b_phi,
				double mu_pt, double mu_eta, double mu_phi, std::string device)
		{
			return NuSolutionTensors::Rotation(
					PhysicsFloats::ToTensor(b_pt, b_eta, b_phi, device), 
					PhysicsFloats::ToTensor(mu_pt, mu_eta, mu_phi, device));
		}
		
		static torch::Tensor H(
				double b_pt, double b_eta, double b_phi, double b_e, 
				double mu_pt, double mu_eta, double mu_phi, double mu_e, 
				double massTop, double massW, double massNu, std::string device)
		{
			
			return NuSolutionTensors::H(
					PhysicsFloats::ToTensor(b_pt, b_eta, b_phi, b_e, device), 
					PhysicsFloats::ToTensor(mu_pt, mu_eta, mu_phi, mu_e, device), 
					PhysicsFloats::ToTensor(massTop, device), 
					PhysicsFloats::ToTensor(massW, device), 
					PhysicsFloats::ToTensor(massNu, device));
		}


	}
}


#endif 
