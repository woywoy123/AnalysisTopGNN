#ifndef H_PHYSICS_TENSOR_POLAR
#define H_PHYSICS_TENSOR_POLAR

#include "physics.h"
#include <transform/cartesian-tensors/cartesian.h>

namespace Physics
{
    namespace Tensors
    {
        namespace Polar
        {
            torch::Tensor P2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi);
            torch::Tensor P2(torch::Tensor Pmu);
            torch::Tensor P(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi);
            torch::Tensor P(torch::Tensor Pmu);
            torch::Tensor Beta2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e);
            torch::Tensor Beta2(torch::Tensor pmu);
            torch::Tensor Beta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e);
            torch::Tensor Beta(torch::Tensor pmu);
            torch::Tensor M2(torch::Tensor pmu);
            torch::Tensor M2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e);
            torch::Tensor M(torch::Tensor pmu);
            torch::Tensor M(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e);
            torch::Tensor Mt2(torch::Tensor pmu);
            torch::Tensor Mt2(torch::Tensor pt, torch::Tensor eta, torch::Tensor e);
            torch::Tensor Mt(torch::Tensor pmu);
            torch::Tensor Mt(torch::Tensor pt, torch::Tensor eta, torch::Tensor e);
            torch::Tensor Theta(torch::Tensor pmu);
            torch::Tensor Theta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi);
            torch::Tensor DeltaR(torch::Tensor pmu1, torch::Tensor pmu2);
            torch::Tensor DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2);
        }
    }
}
#endif
