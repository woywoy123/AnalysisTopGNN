#ifndef H_PHYSICS_TENSORS_C
#define H_PHYSICS_TENSORS_C

#include "Tensors.h"
#include "../../Transform/Headers/ToPolarTensors.h"

namespace PhysicsCartesianTensors
{
	const torch::Tensor P2(torch::Tensor px, torch::Tensor py, torch:: Tensor pz){return PhysicsTensors::P2(px, py, pz);}
	const torch::Tensor P(torch::Tensor px, torch::Tensor py, torch::Tensor pz){return PhysicsTensors::P(px, py, pz);}
	
	const torch::Tensor Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e){return PhysicsTensors::Beta2(px, py, pz, e);}
	const torch::Tensor Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e){return PhysicsTensors::Beta(px, py, pz, e);} 

	const torch::Tensor M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e){return PhysicsTensors::M2(px, py, pz, e);}
	const torch::Tensor M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e){return PhysicsTensors::M(px, py, pz, e);}
	const torch::Tensor Mass(torch::Tensor Pmu)
	{ 
		return PhysicsTensors::M(
				Pmu.index({torch::indexing::Slice(), 0}).view({-1, 1}), 
				Pmu.index({torch::indexing::Slice(), 1}).view({-1, 1}), 
				Pmu.index({torch::indexing::Slice(), 2}).view({-1, 1}), 
				Pmu.index({torch::indexing::Slice(), 3}).view({-1, 1}));  
	}

	const torch::Tensor Mt2(torch::Tensor pz, torch::Tensor e){return PhysicsTensors::Mt2(pz, e);}
	const torch::Tensor Mt(torch::Tensor pz, torch::Tensor e){return PhysicsTensors::Mt(pz, e);}
	
	const torch::Tensor Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz){return PhysicsTensors::Theta(px, py, pz);}
	const torch::Tensor DeltaR(
			torch::Tensor px1, torch::Tensor px2, 
			torch::Tensor py1, torch::Tensor py2,
			torch::Tensor pz1, torch::Tensor pz2)
	{
		torch::Tensor _eta1 = TransformTensors::Eta(px1, py1, pz1); 	
		torch::Tensor _eta2 = TransformTensors::Eta(px2, py2, pz2); 	

		torch::Tensor _phi1 = TransformTensors::Phi(px1, py1); 	
		torch::Tensor _phi2 = TransformTensors::Phi(px2, py2); 	
		
		return PhysicsTensors::DeltaR(_eta1, _eta2, _phi1, _phi2);
	}
}
#endif 
