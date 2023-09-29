#ifndef H_NUSOL_FLOATS
#define H_NUSOL_FLOATS
#include <torch/torch.h>
#include <nusol/nusol-tensor/nusol_tools.h>
#include <nusol/nusol-tensor/nusol.h>

namespace NuSol
{
    namespace Floats
    {
        namespace Polar 
        {
            std::map<std::string, torch::Tensor> Nu(
                    std::vector<std::vector<double>> pmu_b, std::vector<std::vector<double>> pmu_mu,
                    std::vector<std::vector<double>> met_phi, 
                    std::vector<std::vector<double>> masses,
                    std::vector<std::vector<double>> sigma, const double null); 

            std::map<std::string, torch::Tensor> NuNu(
                    std::vector<std::vector<double>> pmu_b1, std::vector<std::vector<double>> pmu_b2, 
                    std::vector<std::vector<double>> pmu_mu1, std::vector<std::vector<double>> pmu_mu2,
                    std::vector<std::vector<double>> met_phi, 
                    std::vector<std::vector<double>> masses, const double null);
        }
        namespace Cartesian
        {
            std::map<std::string, torch::Tensor> Nu(
                    std::vector<std::vector<double>> pmc_b, std::vector<std::vector<double>> pmc_mu,
                    std::vector<std::vector<double>> met_xy, 
                    std::vector<std::vector<double>> masses,
                    std::vector<std::vector<double>> sigma, const double null); 
            
            std::map<std::string, torch::Tensor> NuNu(
                    std::vector<std::vector<double>> pmc_b1, std::vector<std::vector<double>> pmc_b2, 
                    std::vector<std::vector<double>> pmc_mu1, std::vector<std::vector<double>> pmc_mu2,
                    std::vector<std::vector<double>> met_xy, 
                    std::vector<std::vector<double>> masses, const double null); 
        }
    }
}

#endif
