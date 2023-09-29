#ifndef H_PHYSICS_TENSORS_P
#define H_PHYSICS_TENSORS_P

#include <iostream>
#include "Tensors.h"
#include "../../Transform/Headers/ToCartesianTensors.h"

namespace PhysicsPolarTensors
{
	const std::vector<torch::Tensor> _Transform(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
	{
		return {TransformTensors::Px(pt, phi), TransformTensors::Py(pt, phi), TransformTensors::Pz(pt, eta)}; 
	}

	const torch::Tensor P2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
	{
		std::vector<torch::Tensor> Pmc = _Transform(pt, eta, phi); 	
		return PhysicsTensors::P2(Pmc[0], Pmc[1], Pmc[2]);
	}


	const torch::Tensor P(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
	{
		std::vector<torch::Tensor> Pmc = _Transform(pt, eta, phi); 	
		return PhysicsTensors::P(Pmc[0], Pmc[1], Pmc[2]);
	}
	
	const torch::Tensor Beta2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
	{
		std::vector<torch::Tensor> Pmc = _Transform(pt, eta, phi); 	
		return PhysicsTensors::Beta2(Pmc[0], Pmc[1], Pmc[2], e);
	}

	const torch::Tensor Beta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
	{
		std::vector<torch::Tensor> Pmc = _Transform(pt, eta, phi); 	
		return PhysicsTensors::Beta(Pmc[0], Pmc[1], Pmc[2], e);
	} 

	const torch::Tensor M2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
	{
		std::vector<torch::Tensor> Pmc = _Transform(pt, eta, phi);
		return PhysicsTensors::M2(Pmc[0], Pmc[1], Pmc[2], e);
	}
	
	const torch::Tensor M(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
	{
		std::vector<torch::Tensor> Pmc = _Transform(pt, eta, phi);
		return PhysicsTensors::M(Pmc[0], Pmc[1], Pmc[2], e);
	}

	const torch::Tensor Mass(torch::Tensor Pmu)
	{ 
		std::vector<torch::Tensor> Pmc = _Transform(
				Pmu.index({torch::indexing::Slice(), 0}).view({-1, 1}), 
				Pmu.index({torch::indexing::Slice(), 1}).view({-1, 1}), 
				Pmu.index({torch::indexing::Slice(), 2}).view({-1, 1})); 
		return PhysicsTensors::M(
				Pmc[0], Pmc[1], Pmc[2],
				Pmu.index({torch::indexing::Slice(), 3}).view({-1, 1}));  
	}

	const torch::Tensor Mt2(torch::Tensor pt, torch::Tensor eta, torch::Tensor e)
	{
		return PhysicsTensors::Mt2(TransformTensors::Pz(pt, eta), e);
	}
	
	const torch::Tensor Mt(torch::Tensor pt, torch::Tensor eta, torch::Tensor e)
	{
		return PhysicsTensors::Mt(TransformTensors::Pz(pt, eta), e);
	}
	
	const torch::Tensor Theta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
	{
		std::vector<torch::Tensor> Pmc = _Transform(pt, eta, phi);
		return PhysicsTensors::Theta(Pmc[0], Pmc[1], Pmc[2]);
	}

	const torch::Tensor DeltaR(
			torch::Tensor eta1, torch::Tensor eta2, 
			torch::Tensor phi1, torch::Tensor phi2)
	{
		return PhysicsTensors::DeltaR(eta1, eta2, phi1, phi2);
	}
}
#endif
