#ifndef H_PHYSICS_CUDA_CARTESIAN
#define H_PHYSICS_CUDA_CARTESIAN

#include <physics/physics-cuda/physics.h>
#include <transform/polar-cuda/polar.h>

namespace Physics
{
    namespace CUDA 
    {
        namespace Cartesian 
        {
            const torch::Tensor P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
            { 
                return Physics::CUDA::P2(px, py, pz); 
            }

            const torch::Tensor P2(torch::Tensor pmc)
            {
                return Physics::CUDA::P2(pmc); 
            }

            const torch::Tensor P(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
            { 
                return Physics::CUDA::P(px, py, pz); 
            }

            const torch::Tensor P(torch::Tensor pmc)
            {
                return Physics::CUDA::P(pmc); 
            }

            const torch::Tensor Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
            { 
                return Physics::CUDA::Beta2(px, py, pz, e); 
            }

            const torch::Tensor Beta2(torch::Tensor pmc)
            {
                return Physics::CUDA::Beta2(pmc); 
            }

            const torch::Tensor Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
            { 
                return Physics::CUDA::Beta(px, py, pz, e); 
            }

            const torch::Tensor Beta(torch::Tensor pmc)
            {
                return Physics::CUDA::Beta(pmc); 
            }

            const torch::Tensor M2(torch::Tensor pmc)
            { 
                return Physics::CUDA::M2(pmc); 
            }

            const torch::Tensor M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
            { 
                return Physics::CUDA::M2(px, py, pz, e); 
            }
            
            const torch::Tensor M(torch::Tensor pmc)
            { 
                return Physics::CUDA::M(pmc); 
            }
            
            const torch::Tensor M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
            { 
                return Physics::CUDA::M(px, py, pz, e); 
            }

            const torch::Tensor Mt2(torch::Tensor pmc)
            { 
                return Physics::CUDA::Mt2(pmc);
            }

            const torch::Tensor Mt2(torch::Tensor pz, torch::Tensor e)
            { 
                return Physics::CUDA::Mt2(pz, e); 
            }
            
            const torch::Tensor Mt(torch::Tensor pmc)
            { 
                return Physics::CUDA::Mt(pmc); 
            }

            const torch::Tensor Mt(torch::Tensor pz, torch::Tensor e)
            { 
                return Physics::CUDA::Mt(pz, e); 
            }
        
            const torch::Tensor Theta(torch::Tensor pmc)
            {
                return Physics::CUDA::Theta(pmc); 
            }
            
            const torch::Tensor Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
            {
                return Physics::CUDA::Theta(px, py, pz); 
            }
 
            const torch::Tensor DeltaR(torch::Tensor pmc1, torch::Tensor pmc2)
            {
                const unsigned int len = pmc1.size(0);
                torch::Tensor pmu1 = Transform::CUDA::PtEtaPhiE(torch::cat({pmc1, pmc2}, 0)); 
                torch::Tensor pmu2 = pmu1.index({torch::indexing::Slice({len, len*2+1})}).view({-1, 4});
                pmu1 = pmu1.index({torch::indexing::Slice({0, len})}).view({-1, 4});
                return Physics::CUDA::DeltaR(pmu1, pmu2); 
            }
            
            const torch::Tensor DeltaR(
                    torch::Tensor px1, torch::Tensor px2, 
                    torch::Tensor py1, torch::Tensor py2, 
                    torch::Tensor pz1, torch::Tensor pz2)
            {
                const unsigned int len = px1.size(0);
                torch::Tensor pmu1 = Transform::CUDA::PtEtaPhi(
                        torch::cat({px1, px2}, 0), 
                        torch::cat({py1, py2}, 0), 
                        torch::cat({pz1, pz2}, 0)); 
                torch::Tensor pmu2 = pmu1.index({torch::indexing::Slice({len, len*2+1})}).view({-1, 3});
                pmu1 = pmu1.index({torch::indexing::Slice({0, len})}).view({-1, 3});
                return Physics::CUDA::DeltaR(pmu1, pmu2); 
            }
        }
    }
}

#endif
