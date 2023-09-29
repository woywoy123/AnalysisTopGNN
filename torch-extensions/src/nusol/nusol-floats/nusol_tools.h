#ifndef H_NUSOL_TOOLS_FLOATS
#define H_NUSOL_TOOLS_FLOATS
#include <torch/torch.h>

namespace Tooling
{
    torch::Tensor ToTensor(std::vector<std::vector<double>> inpt); 
}

#endif
