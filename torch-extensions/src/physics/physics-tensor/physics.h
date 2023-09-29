#ifndef H_PHYSICS_TENSOR
#define H_PHYSICS_TENSOR
#include <torch/torch.h>

namespace Physics
{
    namespace Tensors
    {
        torch::Tensor P2(torch::Tensor pmc); 
        torch::Tensor P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
        torch::Tensor P(torch::Tensor pmc); 
        torch::Tensor P(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
        torch::Tensor Beta2(torch::Tensor pmc); 
        torch::Tensor Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
        torch::Tensor Beta(torch::Tensor pmc); 
        torch::Tensor Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 

        torch::Tensor M2(torch::Tensor pmc); 
        torch::Tensor M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
        torch::Tensor M(torch::Tensor pmc); 
        torch::Tensor M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
        torch::Tensor Mt2(torch::Tensor pmc); 
        torch::Tensor Mt2(torch::Tensor pz, torch::Tensor e); 
        torch::Tensor Mt(torch::Tensor pmc); 
        torch::Tensor Mt(torch::Tensor pz, torch::Tensor e); 
        torch::Tensor Theta(torch::Tensor pmc); 
        torch::Tensor Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
        torch::Tensor DeltaR(torch::Tensor pmu1, torch::Tensor pmu2); 
        torch::Tensor DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2); 
    }
}
#endif
