#ifndef H_PHYSICS_CUDA_POLAR
#define H_PHYSICS_CUDA_POLAR

#include <physics/physics-cuda/physics.h>
#include <transform/cartesian-cuda/cartesian.h>

namespace Physics
{
    namespace CUDA
    {
        namespace Polar
        {
            const torch::Tensor P2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
            {
                torch::Tensor pmc = Transform::CUDA::PxPyPz(pt, eta, phi); 
                return Physics::CUDA::P2(pmc); 
            } 

            const torch::Tensor P2(torch::Tensor Pmu)
            {
                torch::Tensor pmc = Transform::CUDA::PxPyPzE(Pmu); 
                return Physics::CUDA::P2(pmc);
            }

            const torch::Tensor P(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
            {
                 torch::Tensor pmc = Transform::CUDA::PxPyPz(pt, eta, phi); 
                 return Physics::CUDA::P(pmc); 
            }

            const torch::Tensor P(torch::Tensor Pmu)
            {
                torch::Tensor pmc = Transform::CUDA::PxPyPzE(Pmu); 
                return Physics::CUDA::P(pmc);
            }

            const torch::Tensor Beta2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
            { 
                torch::Tensor pmc = Transform::CUDA::PxPyPzE(pt, eta, phi, e); 
                return Physics::CUDA::Beta2(pmc); 
            }

            const torch::Tensor Beta2(torch::Tensor pmu)
            {
                torch::Tensor pmc = Transform::CUDA::PxPyPzE(pmu); 
                return Physics::CUDA::Beta2(pmc); 
            }

            const torch::Tensor Beta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
            { 
                torch::Tensor pmc = Transform::CUDA::PxPyPzE(pt, eta, phi, e); 
                return Physics::CUDA::Beta(pmc); 
            }

            const torch::Tensor Beta(torch::Tensor pmu)
            {
                torch::Tensor pmc = Transform::CUDA::PxPyPzE(pmu); 
                return Physics::CUDA::Beta(pmc); 
            }

            const torch::Tensor M2(torch::Tensor pmu)
            { 
                torch::Tensor pmc = Transform::CUDA::PxPyPzE(pmu); 
                return Physics::CUDA::M2(pmc); 
            }

            const torch::Tensor M2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
            { 
                torch::Tensor pmc = Transform::CUDA::PxPyPzE(pt, eta, phi, e); 
                return Physics::CUDA::M2(pmc); 
            }
            
            const torch::Tensor M(torch::Tensor pmu)
            { 
                torch::Tensor pmc = Transform::CUDA::PxPyPzE(pmu); 
                return Physics::CUDA::M(pmc); 
            }
            
            const torch::Tensor M(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
            { 
                torch::Tensor pmc = Transform::CUDA::PxPyPzE(pt, eta, phi, e); 
                return Physics::CUDA::M(pmc); 
            }

            const torch::Tensor Mt2(torch::Tensor pmu)
            { 
                torch::Tensor pmc = Transform::CUDA::PxPyPzE(pmu); 
                return Physics::CUDA::Mt2(pmc);
            }

            const torch::Tensor Mt2(torch::Tensor pt, torch::Tensor eta, torch::Tensor e)
            { 
                torch::Tensor pz = Transform::CUDA::Pz(pt, eta); 
                return Physics::CUDA::Mt2(pz, e); 
            }
            
            const torch::Tensor Mt(torch::Tensor pmu)
            { 
                torch::Tensor pmc = Transform::CUDA::PxPyPzE(pmu); 
                return Physics::CUDA::Mt(pmc); 
            }

            const torch::Tensor Mt(torch::Tensor pt, torch::Tensor eta, torch::Tensor e)
            { 
                torch::Tensor pz = Transform::CUDA::Pz(pt, eta); 
                return Physics::CUDA::Mt(pz, e); 
            }

            const torch::Tensor Theta(torch::Tensor pmu)
            {
                torch::Tensor pmc = Transform::CUDA::PxPyPzE(pmu); 
                return Physics::CUDA::Theta(pmc); 
            }

            const torch::Tensor Theta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
            {
                torch::Tensor pmc = Transform::CUDA::PxPyPz(
                        torch::cat({
                             pt.view({-1, 1}), 
                            eta.view({-1, 1}), 
                            phi.view({-1, 1})}, -1)); 
                return Physics::CUDA::Theta(pmc); 
            }

            const torch::Tensor DeltaR(torch::Tensor pmu1, torch::Tensor pmu2)
            {
                return Physics::CUDA::DeltaR(pmu1, pmu2); 
            }

            const torch::Tensor DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2)
            {
                return Physics::CUDA::DeltaR(eta1, eta2, phi1, phi2); 
            }
        }
    }
}

#endif
