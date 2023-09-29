#ifndef H_TRANSFORM_TENSORS_POLAR
#define H_TRANSFORM_TENSORS_POLAR
#include <torch/torch.h>

namespace Transform
{
    namespace Tensors
    {
        torch::Tensor Pt(torch::Tensor px, torch::Tensor py); 
        torch::Tensor Phi(torch::Tensor px, torch::Tensor py);
        torch::Tensor Eta(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
        torch::Tensor PtEta(torch::Tensor pt, torch::Tensor pz); 
        torch::Tensor PtEtaPhi(torch::Tensor px, torch::Tensor py, torch::Tensor pz);
        torch::Tensor PtEtaPhiE(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);

        torch::Tensor Pt(torch::Tensor pmc); 
        torch::Tensor Phi(torch::Tensor pmc);
        torch::Tensor Eta(torch::Tensor pmc); 
        torch::Tensor PtEta(torch::Tensor pmc); 
        torch::Tensor PtEtaPhi(torch::Tensor pmc);
        torch::Tensor PtEtaPhiE(torch::Tensor pmc);
    }
}

#endif
