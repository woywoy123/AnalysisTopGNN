#ifndef H_NUSOL_TOOLS
#define H_NUSOL_TOOLS
#include <torch/torch.h>

namespace Tooling
{
    torch::TensorOptions MakeOp(torch::Tensor x); 
    std::map<std::string, torch::Tensor> GetMasses(torch::Tensor L, torch::Tensor masses); 
    torch::Tensor Pi_2(torch::Tensor x); 
    torch::Tensor x0(torch::Tensor pmc, torch::Tensor _pm2, torch::Tensor mH2, torch::Tensor mL2); 
    torch::Tensor Rotation(torch::Tensor pmc_b, torch::Tensor pmc_mu, torch::Tensor base); 
    torch::Tensor Sigma(torch::Tensor x, torch::Tensor sigma);
    torch::Tensor MET(torch::Tensor met_xy); 
    torch::Tensor Shape(torch::Tensor x, std::vector<int> diag); 
    torch::Tensor HorizontalVertical(torch::Tensor G); 
    torch::Tensor Parallel(torch::Tensor G, torch::Tensor CoF); 
    torch::Tensor Intersecting(torch::Tensor G, torch::Tensor g22, torch::Tensor CoF);
    torch::Tensor H_perp(torch::Tensor base); 
    torch::Tensor N(torch::Tensor hperp); 
    std::map<std::string, torch::Tensor> _convert(torch::Tensor met_phi);
    std::map<std::string, torch::Tensor> _convert(torch::Tensor pmu1, torch::Tensor pmu2);
    torch::Tensor _format(std::vector<torch::Tensor> v); 
}

#endif
