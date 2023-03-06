#ifndef H_PHYSICS_CUDA_C
#define H_PHYSICS_CUDA_C

#include "CUDA.h"
#include "../../Transform/Headers/ToPolarCUDA.h"

namespace PhysicsCartesianCUDA
{
	const torch::Tensor P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
	{ 
		return PhysicsCUDA::P2(px, py, pz); 
	}

	const torch::Tensor P(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
	{ 
		return PhysicsCUDA::P(px, py, pz); 
	}
	
	const torch::Tensor Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
	{ 
		return PhysicsCUDA::Beta2(px, py, pz, e); 
	}

	const torch::Tensor Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
	{ 
		return PhysicsCUDA::Beta(px, py, pz, e); 
	}

	const torch::Tensor M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
	{ 
		return PhysicsCUDA::M2(px, py, pz, e); 
	}

	const torch::Tensor M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
	{ 
		return PhysicsCUDA::M(px, py, pz, e); 
	}

	const torch::Tensor Mass(torch::Tensor Pmu)
	{ 
		return PhysicsCUDA::M(
				Pmu.index({torch::indexing::Slice(), 0}).view({-1, 1}), 
				Pmu.index({torch::indexing::Slice(), 1}).view({-1, 1}), 
				Pmu.index({torch::indexing::Slice(), 2}).view({-1, 1}), 
				Pmu.index({torch::indexing::Slice(), 3}).view({-1, 1}));  
	}


	const torch::Tensor Mt2(torch::Tensor pz, torch::Tensor e)
	{ 
		return PhysicsCUDA::Mt2(pz, e); 
	}

	const torch::Tensor Mt(torch::Tensor pz, torch::Tensor e)
	{ 
		return PhysicsCUDA::Mt(pz, e); 
	}

	const torch::Tensor Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
	{ 
		return PhysicsCUDA::Theta(px, py, pz); 
	}

	const torch::Tensor DeltaR(
			torch::Tensor px1, torch::Tensor px2, 
			torch::Tensor py1, torch::Tensor py2, 
			torch::Tensor pz1, torch::Tensor pz2)
	{ 
		torch::Tensor eta1 = TransformCUDA::Eta(px1, py1, pz1); 
		torch::Tensor eta2 = TransformCUDA::Eta(px2, py2, pz2); 

		torch::Tensor phi1 = TransformCUDA::Phi(px1, py1); 
		torch::Tensor phi2 = TransformCUDA::Phi(px2, py2); 

		return PhysicsCUDA::DeltaR(eta1, eta2, phi1, phi2); 
	}
}
#endif 
