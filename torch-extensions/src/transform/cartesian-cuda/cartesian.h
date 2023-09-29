#ifndef H_TRANSFORM_CUDA_CARTESIAN
#define H_TRANSFORM_CUDA_CARTESIAN

#include <torch/torch.h>
torch::Tensor _Px(torch::Tensor pt, torch::Tensor phi); 
torch::Tensor _Py(torch::Tensor pt, torch::Tensor phi); 
torch::Tensor _Pz(torch::Tensor pt, torch::Tensor eta); 
torch::Tensor _PxPyPz(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi); 
torch::Tensor _PxPyPzE(torch::Tensor Pmu); 

namespace Transform
{
    namespace CUDA
    {
        inline torch::Tensor Cclip(torch::Tensor inpt, int dim)
        { 
            return inpt.index({torch::indexing::Slice(), dim}); 
        }
        inline torch::Tensor Px(torch::Tensor pt, torch::Tensor phi)
        {
            return _Px(pt, phi);
        } 

        inline torch::Tensor Px(torch::Tensor pmu)
        {
            torch::Tensor pt = Transform::CUDA::Cclip(pmu, 0);
            torch::Tensor phi = Transform::CUDA::Cclip(pmu, 2);
            return _Px(pt, phi);  
        }

        inline torch::Tensor Py(torch::Tensor pt, torch::Tensor phi)
        {
            return _Py(pt, phi);
        } 

        inline torch::Tensor Py(torch::Tensor pmu)
        {
            torch::Tensor pt = Transform::CUDA::Cclip(pmu, 0); 
            torch::Tensor phi = Transform::CUDA::Cclip(pmu, 2); 
            return _Py(pt, phi);
        } 

        inline torch::Tensor Pz(torch::Tensor pt, torch::Tensor eta)
        {
            return _Pz(pt, eta);
        }

        inline torch::Tensor Pz(torch::Tensor pmu)
        {
            torch::Tensor pt = Transform::CUDA::Cclip(pmu, 0); 
            torch::Tensor eta = Transform::CUDA::Cclip(pmu, 1); 
            return _Pz(pt, eta);
        }

        inline torch::Tensor PxPyPz(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
        {
            return _PxPyPz(pt, eta, phi);
        }

        inline torch::Tensor PxPyPz(torch::Tensor pmu)
        {
            torch::Tensor pt = Transform::CUDA::Cclip(pmu, 0); 
            torch::Tensor eta = Transform::CUDA::Cclip(pmu, 1); 
            torch::Tensor phi = Transform::CUDA::Cclip(pmu, 2);  
            return _PxPyPz(pt, eta, phi);
        }

        inline torch::Tensor PxPyPzE(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
        {
            pt = pt.view({-1, 1}); 
            eta = eta.view({-1, 1}); 
            phi = phi.view({-1, 1}); 
            e = e.view({-1, 1}); 
            return _PxPyPzE(torch::cat({pt, eta, phi, e}, -1));
        } 

        inline torch::Tensor PxPyPzE(torch::Tensor Pmu)
        {
            return _PxPyPzE(Pmu);
        } 
    }
}

#endif
