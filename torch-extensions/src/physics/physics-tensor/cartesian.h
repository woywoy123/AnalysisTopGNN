#ifndef H_PHYSICS_TENSOR_CARTESIAN
#define H_PHYSICS_TENSOR_CARTESIAN

#include "physics.h"
#include <transform/polar-tensors/polar.h>

namespace Physics
{
    namespace Tensors
    {
        namespace Cartesian 
        {
            torch::Tensor P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
            torch::Tensor P2(torch::Tensor pmc); 
            torch::Tensor P(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
            torch::Tensor P(torch::Tensor pmc); 
            torch::Tensor Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
            torch::Tensor Beta2(torch::Tensor pmc); 
            torch::Tensor Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
            torch::Tensor Beta(torch::Tensor pmc); 
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
            torch::Tensor DeltaR(torch::Tensor pmc1, torch::Tensor pmc2); 
            torch::Tensor DeltaR(torch::Tensor px1, torch::Tensor px2, torch::Tensor py1, torch::Tensor py2, torch::Tensor pz1, torch::Tensor pz2); 
        }
    }
}

#endif
