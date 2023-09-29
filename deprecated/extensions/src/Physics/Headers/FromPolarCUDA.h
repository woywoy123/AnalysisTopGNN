#ifndef H_PHYSICS_CUDA_P
#define H_PHYSICS_CUDA_P

#include <iostream>
#include "CUDA.h"
#include "../../Transform/Headers/ToCartesianCUDA.h"

namespace PhysicsPolarCUDA
{
	const std::vector<torch::Tensor> _Conv( torch::Tensor pt, torch::Tensor eta, torch::Tensor phi )
	{
		return {TransformCUDA::Px(pt, phi), TransformCUDA::Py(pt, phi), TransformCUDA::Pz(pt, eta)}; 
	}

	const torch::Tensor P2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
	{ 
		std::vector<torch::Tensor> Pmu = _Conv(pt, eta, phi); 
		return PhysicsCUDA::P2(Pmu[0], Pmu[1], Pmu[2]); 
	}

	const torch::Tensor P(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
	{ 
		std::vector<torch::Tensor> Pmu = _Conv(pt, eta, phi); 
		return PhysicsCUDA::P(Pmu[0], Pmu[1], Pmu[2]); 
	}
	
	const torch::Tensor Beta2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
	{ 
		std::vector<torch::Tensor> Pmu = _Conv(pt, eta, phi); 
		return PhysicsCUDA::Beta2(Pmu[0], Pmu[1], Pmu[2], e); 
	}

	const torch::Tensor Beta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
	{ 
		std::vector<torch::Tensor> Pmu = _Conv(pt, eta, phi); 
		return PhysicsCUDA::Beta(Pmu[0], Pmu[1], Pmu[2], e); 
	}

	const torch::Tensor M2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
	{ 
		std::vector<torch::Tensor> Pmu = _Conv(pt, eta, phi); 
		return PhysicsCUDA::M2(Pmu[0], Pmu[1], Pmu[2], e); 
	}

	const torch::Tensor M(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
	{ 
		std::vector<torch::Tensor> Pmu = _Conv(pt, eta, phi); 
		return PhysicsCUDA::M(Pmu[0], Pmu[1], Pmu[2], e); 
	}
	
	const torch::Tensor Mass(torch::Tensor Pmu)
	{ 
		std::vector<torch::Tensor> Pmc = _Conv(
				Pmu.index({torch::indexing::Slice(), 0}).view({-1, 1}), 
				Pmu.index({torch::indexing::Slice(), 1}).view({-1, 1}), 
				Pmu.index({torch::indexing::Slice(), 2}).view({-1, 1})); 
		return PhysicsCUDA::M(
				Pmc[0], Pmc[1], Pmc[2],
				Pmu.index({torch::indexing::Slice(), 3}).view({-1, 1}));  
	}

	const torch::Tensor Mt2(torch::Tensor pt, torch::Tensor eta, torch::Tensor e)
	{ 
		return PhysicsCUDA::Mt2(TransformCUDA::Pz(pt, eta), e); 
	}

	const torch::Tensor Mt(torch::Tensor pt, torch::Tensor eta, torch::Tensor e)
	{ 
		return PhysicsCUDA::Mt(TransformCUDA::Pz(pt, eta), e); 
	}

	const torch::Tensor Theta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
	{ 
		std::vector<torch::Tensor> Pmu = _Conv(pt, eta, phi); 
		return PhysicsCUDA::Theta(Pmu[0], Pmu[1], Pmu[2]); 
	}

	const torch::Tensor DeltaR(
			torch::Tensor eta1, torch::Tensor eta2, 
			torch::Tensor phi1, torch::Tensor phi2)
	{ 
		return PhysicsCUDA::DeltaR(eta1, eta2, phi1, phi2); 
	}
}
#endif 
