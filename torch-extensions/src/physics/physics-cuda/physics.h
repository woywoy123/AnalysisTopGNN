#ifndef H_PHYSICS_CUDA
#define H_PHYSICS_CUDA
#include <torch/torch.h>

torch::Tensor _P2(torch::Tensor pmc);
torch::Tensor _P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
torch::Tensor _P(torch::Tensor pmc); 
torch::Tensor _P(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 

torch::Tensor _Beta2(torch::Tensor pmc); 
torch::Tensor _Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
torch::Tensor _Beta(torch::Tensor pmc); 
torch::Tensor _Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 

torch::Tensor _M2(torch::Tensor pmc); 
torch::Tensor _M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
torch::Tensor _M(torch::Tensor pmc); 
torch::Tensor _M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 

torch::Tensor _Mt2(torch::Tensor pmc); 
torch::Tensor _Mt2(torch::Tensor pz, torch::Tensor e); 
torch::Tensor _Mt(torch::Tensor pmc); 
torch::Tensor _Mt(torch::Tensor pz, torch::Tensor e); 

torch::Tensor _Theta(torch::Tensor pmc); 
torch::Tensor _Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 

torch::Tensor _DeltaR(torch::Tensor pmu1, torch::Tensor pmu2); 
torch::Tensor _DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2); 


namespace Physics
{
    namespace CUDA
    {
        inline torch::Tensor P2(torch::Tensor pmc)
        { 
            return _P2(pmc); 
        }
        
        inline torch::Tensor P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
        { 
            return _P2(px, py, pz); 
        }

        inline torch::Tensor P(torch::Tensor pmc)
        { 
            return _P(pmc); 
        }

        inline torch::Tensor P(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
        { 
            return _P(px, py, pz); 
        }

        inline torch::Tensor Beta2(torch::Tensor pmc)
        { 
            return _Beta2(pmc); 
        }

        inline torch::Tensor Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
        { 
            return _Beta2(px, py, pz, e); 
        }
        
        inline torch::Tensor Beta(torch::Tensor pmc)
        { 
            return _Beta(pmc); 
        }

        inline torch::Tensor Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
        { 
            return _Beta(px, py, pz, e); 
        }

        inline torch::Tensor M2(torch::Tensor pmc)
        { 
            return _M2(pmc); 
        }

        inline torch::Tensor M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
        { 
            return _M2(px, py, pz, e); 
        }
        
        inline torch::Tensor M(torch::Tensor pmc)
        { 
            return _M(pmc); 
        }

        inline torch::Tensor M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
        { 
            return _M(px, py, pz, e); 
        }

        inline torch::Tensor Mt2(torch::Tensor pmc)
        { 
            return _Mt2(pmc); 
        }

        inline torch::Tensor Mt2(torch::Tensor pz, torch::Tensor e)
        { 
            return _Mt2(pz, e); 
        }
        
        inline torch::Tensor Mt(torch::Tensor pmc)
        { 
            return _Mt(pmc); 
        }

        inline torch::Tensor Mt(torch::Tensor pz, torch::Tensor e)
        { 
            return _Mt(pz, e); 
        }

        inline torch::Tensor Theta(torch::Tensor pmc)
        { 
            return _Theta(pmc); 
        }

        inline torch::Tensor Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
        { 
            return _Theta(px, py, pz); 
        }

        inline torch::Tensor DeltaR(torch::Tensor pmu1, torch::Tensor pmu2)
        { 
            return _DeltaR(pmu1, pmu2); 
        }

        inline torch::Tensor DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2)
        { 
            return _DeltaR(eta1, eta2, phi1, phi2); 
        }
    }
}
#endif
