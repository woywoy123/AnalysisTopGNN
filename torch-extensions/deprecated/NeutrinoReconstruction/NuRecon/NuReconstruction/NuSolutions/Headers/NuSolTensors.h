#ifndef H_NUSOL_TENSORS
#define H_NUSOL_TENSORS

#include <torch/extension.h>
#include <iostream>
#include "../../Physics/Tensors/Headers/PhysicsTensors.h"

namespace NuSolutionTensors
{
	// Some calculations... Wont be moved into main production.
	torch::Tensor x0Polar(torch::Tensor PolarL, torch::Tensor MassH, torch::Tensor MassL); 
	torch::Tensor x0Cartesian(torch::Tensor CartesianL, torch::Tensor MassH, torch::Tensor MassL);
	
	torch::Tensor SxCartesian(torch::Tensor _b, torch::Tensor _mu, 
			torch::Tensor mW, torch::Tensor mNu); 
	torch::Tensor SyCartesian(torch::Tensor _b, torch::Tensor _mu, 
			torch::Tensor mTop, torch::Tensor mW, torch::Tensor Sx); 
	torch::Tensor SxSyCartesian(torch::Tensor _b, torch::Tensor _mu, 
			torch::Tensor mTop, torch::Tensor mW, torch::Tensor mNu);

	torch::Tensor Eps2Cartesian(torch::Tensor mW, torch::Tensor mNu, torch::Tensor mu);
	torch::Tensor Eps2Polar(torch::Tensor mW, torch::Tensor mNu, torch::Tensor mu);

	torch::Tensor wCartesian(torch::Tensor _b, torch::Tensor _mu, int factor); 
	torch::Tensor wPolar(torch::Tensor _b, torch::Tensor _mu, int factor); 

	torch::Tensor Omega2Cartesian(torch::Tensor _b, torch::Tensor _mu); 
	torch::Tensor Omega2Polar(torch::Tensor _b, torch::Tensor _mu);

	
	// Base Functions which are to be added as main. 
	torch::Tensor AnalyticalSolutionsCartesian(torch::Tensor _b, torch::Tensor _mu, 
			torch::Tensor massTop, torch::Tensor massW, torch::Tensor massNu);
	torch::Tensor Rotation(torch::Tensor _b, torch::Tensor _mu);
	torch::Tensor H_Algo(torch::Tensor _b, torch::Tensor _mu, torch::Tensor Sol_); 
	torch::Tensor Derivative(torch::Tensor X);
	torch::Tensor UnitCircle(torch::Tensor Op); 
	torch::Tensor Intersections(torch::Tensor A, torch::Tensor B, float cutoff); 

	static torch::Tensor cofactor(torch::Tensor A, std::vector<int> selr, std::vector<int> selc)
	{
		A = A.index({torch::indexing::Slice(), torch::tensor(selr), torch::indexing::Slice()}); 
		A = A.index({torch::indexing::Slice(), torch::indexing::Slice(), torch::tensor(selc)}); 
		return torch::det(A); 
	}
	
	// Transformational functions.
	static torch::Tensor AnalyticalSolutionsPolar(
			torch::Tensor _b, torch::Tensor _mu,
			torch::Tensor massTop, torch::Tensor massW, torch::Tensor massNu)
	{
		return NuSolutionTensors::AnalyticalSolutionsCartesian(
				PhysicsTensors::ToPxPyPzE(_b), 
				PhysicsTensors::ToPxPyPzE(_mu), 
				massTop, massW, massNu); 
	}

	static torch::Tensor H(
			torch::Tensor _b, torch::Tensor _mu, 
			torch::Tensor massTop, torch::Tensor massW, torch::Tensor massNu)
	{
		torch::Tensor Sol_ = NuSolutionTensors::AnalyticalSolutionsPolar(
				_b, _mu, massTop, massW, massNu); 
		return NuSolutionTensors::H_Algo(_b, _mu, Sol_);
	}
}


#endif 
