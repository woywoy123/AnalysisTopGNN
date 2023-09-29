#include "nusol.h" 
#include "nusol_tools.h"

std::map<std::string, torch::Tensor> NuSol::Floats::Polar::Nu(
        std::vector<std::vector<double>> pmu_b, std::vector<std::vector<double>> pmu_mu,
        std::vector<std::vector<double>> met_phi, std::vector<std::vector<double>> masses,
        std::vector<std::vector<double>> sigma, const double null)
{

    torch::Tensor pmu_b_ = Tooling::ToTensor(pmu_b); 
    torch::Tensor pmu_mu_ = Tooling::ToTensor(pmu_mu); 
    torch::Tensor met_phi_ = Tooling::ToTensor(met_phi).view({-1, 2}); 
    torch::Tensor masses_ = Tooling::ToTensor(masses).view({-1, 3}); 
    torch::Tensor sigma_ = Tooling::ToTensor(sigma).view({-1, 2, 2}); 
    return NuSol::Tensor::Polar::Nu(pmu_b_, pmu_mu_, met_phi_, masses_, sigma_, null);
}

std::map<std::string, torch::Tensor> NuSol::Floats::Cartesian::Nu(
        std::vector<std::vector<double>> pmc_b, std::vector<std::vector<double>> pmc_mu,
        std::vector<std::vector<double>> met_xy, std::vector<std::vector<double>> masses,
        std::vector<std::vector<double>> sigma, const double null)
{

    torch::Tensor pmc_b_ = Tooling::ToTensor(pmc_b); 
    torch::Tensor pmc_mu_ = Tooling::ToTensor(pmc_mu); 
    torch::Tensor met_xy_ = Tooling::ToTensor(met_xy).view({-1, 2}); 
    torch::Tensor masses_ = Tooling::ToTensor(masses).view({-1, 3}); 
    torch::Tensor sigma_ = Tooling::ToTensor(sigma).view({-1, 2, 2}); 
    return NuSol::Tensor::Cartesian::Nu(pmc_b_, pmc_mu_, met_xy_, masses_, sigma_, null);
}

std::map<std::string, torch::Tensor> NuSol::Floats::Polar::NuNu(
        std::vector<std::vector<double>> pmu_b1, std::vector<std::vector<double>> pmu_b2, 
        std::vector<std::vector<double>> pmu_mu1, std::vector<std::vector<double>> pmu_mu2,
        std::vector<std::vector<double>> met_phi, 
        std::vector<std::vector<double>> masses, const double null)
{

    torch::Tensor pmu_b1_ = Tooling::ToTensor(pmu_b1); 
    torch::Tensor pmu_b2_ = Tooling::ToTensor(pmu_b2); 

    torch::Tensor pmu_mu1_ = Tooling::ToTensor(pmu_mu1); 
    torch::Tensor pmu_mu2_ = Tooling::ToTensor(pmu_mu2); 

    torch::Tensor met_phi_ = Tooling::ToTensor(met_phi).view({-1, 2}); 
    torch::Tensor masses_ = Tooling::ToTensor(masses).view({-1, 3}); 
    return NuSol::Tensor::Polar::NuNu(pmu_b1_, pmu_b2_, pmu_mu1_, pmu_mu2_, met_phi_, masses_, null);
}

std::map<std::string, torch::Tensor> NuSol::Floats::Cartesian::NuNu(
        std::vector<std::vector<double>> pmc_b1, std::vector<std::vector<double>> pmc_b2, 
        std::vector<std::vector<double>> pmc_mu1, std::vector<std::vector<double>> pmc_mu2,
        std::vector<std::vector<double>> met_xy, 
        std::vector<std::vector<double>> masses, const double null)
{

    torch::Tensor pmc_b1_ = Tooling::ToTensor(pmc_b1); 
    torch::Tensor pmc_b2_ = Tooling::ToTensor(pmc_b2); 

    torch::Tensor pmc_mu1_ = Tooling::ToTensor(pmc_mu1); 
    torch::Tensor pmc_mu2_ = Tooling::ToTensor(pmc_mu2); 

    torch::Tensor met_xy_ = Tooling::ToTensor(met_xy).view({-1, 2}); 
    torch::Tensor masses_ = Tooling::ToTensor(masses).view({-1, 3}); 
    return NuSol::Tensor::Cartesian::NuNu(pmc_b1_, pmc_b2_, pmc_mu1_, pmc_mu2_, met_xy_, masses_, null);
}
