#include "nusol_tools.h"

torch::Tensor Tooling::ToTensor(std::vector<std::vector<double>> inpt)
{
    const torch::TensorOptions op = torch::TensorOptions().dtype(torch::kFloat64); 
    std::vector<torch::Tensor> tmp = {}; 
    for (unsigned int i(0); i < inpt.size(); ++i)
    {
        unsigned int len = inpt[i].size(); 
        torch::Tensor v = torch::from_blob(inpt[i].data(), {len}, op).clone().view({-1, len}); 
        tmp.push_back(v); 
    }
    return torch::cat(tmp, 0); 
}
