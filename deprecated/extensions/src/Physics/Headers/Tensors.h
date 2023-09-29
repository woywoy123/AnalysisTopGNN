#ifndef H_PHYSICS_TENSORS
#define H_PHYSICS_TENSORS

#include <torch/extension.h>

namespace PhysicsTensors
{
	torch::Tensor P2(torch::Tensor px, torch::Tensor py, torch:: Tensor pz); 
	torch::Tensor P(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
	
	torch::Tensor Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
	torch::Tensor Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
	
	torch::Tensor M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
	torch::Tensor M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 

	torch::Tensor Mt2(torch::Tensor pz, torch::Tensor e); 
	torch::Tensor Mt(torch::Tensor pz, torch::Tensor e); 

	torch::Tensor Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz);
	torch::Tensor Theta_(torch::Tensor P_, torch::Tensor pz);

	torch::Tensor DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2); 
}
#endif



