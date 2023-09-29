#ifndef H_TRANSFORM_CUDA_POLAR
#define H_TRANSFORM_CUDA_POLAR

#include <torch/torch.h>
torch::Tensor _Pt(torch::Tensor px, torch::Tensor py); 
torch::Tensor _Eta(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
torch::Tensor _Phi(torch::Tensor px, torch::Tensor py); 
torch::Tensor _PtEtaPhi(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
torch::Tensor _PtEtaPhiE(torch::Tensor Pmc);

namespace Transform
{
    namespace CUDA
    {
        inline torch::Tensor Pclip(torch::Tensor inpt, int dim)
        { 
            return inpt.index({torch::indexing::Slice(), dim}); 
        }

        inline torch::Tensor Pt(torch::Tensor px, torch::Tensor py)
        {
            return _Pt(px, py);
        } 

        inline torch::Tensor Pt(torch::Tensor pmc)
        {
            torch::Tensor px = Transform::CUDA::Pclip(pmc, 0); 
            torch::Tensor py = Transform::CUDA::Pclip(pmc, 1); 
            return _Pt(px, py); 
        }

        inline torch::Tensor Eta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
        {
            return _Eta(px, py, pz);
        } 

        inline torch::Tensor Eta(torch::Tensor pmc)
        {
            torch::Tensor px = Transform::CUDA::Pclip(pmc, 0); 
            torch::Tensor py = Transform::CUDA::Pclip(pmc, 1); 
            torch::Tensor pz = Transform::CUDA::Pclip(pmc, 2);
            return _Eta(px, py, pz); 
        }

        inline torch::Tensor Phi(torch::Tensor px, torch::Tensor py)
        {
            return _Phi(px, py);
        } 
        
        inline torch::Tensor Phi(torch::Tensor pmc)
        {
            torch::Tensor px = Transform::CUDA::Pclip(pmc, 0); 
            torch::Tensor py = Transform::CUDA::Pclip(pmc, 1); 
            return _Phi(px, py); 
        }

        inline torch::Tensor PtEtaPhi(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
        {
            return _PtEtaPhi(px, py, pz);
        }
        
        inline torch::Tensor PtEtaPhi(torch::Tensor pmc)
        {
            torch::Tensor px = Transform::CUDA::Pclip(pmc, 0); 
            torch::Tensor py = Transform::CUDA::Pclip(pmc, 1); 
            torch::Tensor pz = Transform::CUDA::Pclip(pmc, 2); 
            return _PtEtaPhi(px, py, pz); 
        }

        inline torch::Tensor PtEtaPhiE(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
        {
            px = px.view({-1, 1}); 
            py = py.view({-1, 1}); 
            pz = pz.view({-1, 1}); 
            e  =  e.view({-1, 1}); 
            return _PtEtaPhiE(torch::cat({px, py, pz, e}, -1));
        }

        inline torch::Tensor PtEtaPhiE(torch::Tensor pmc)
        {
            return _PtEtaPhiE(pmc);
        }
    }
}

#endif
