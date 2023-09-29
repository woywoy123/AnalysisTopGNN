#ifndef H_NUSOL_TENSOR
#define H_NUSOL_TENSOR

#include <torch/torch.h>
#include <nusol/nusol-tensor/nusol_tools.h>

namespace NuSol
{
    namespace Tensor
    {
        // masses = [W, Top, Neutrino]
        torch::Tensor BaseMatrix(
                torch::Tensor pmc_b, torch::Tensor pmc_mu, 
                torch::Tensor masses); 

        std::tuple<torch::Tensor, torch::Tensor> Intersection(
                torch::Tensor A, torch::Tensor B, const double null); 

        std::map<std::string, torch::Tensor> Nu(
                torch::Tensor pmc_b, torch::Tensor pmc_mu, 
                torch::Tensor met_xy, 
                torch::Tensor masses, 
                torch::Tensor sigma); 
        
        std::map<std::string, torch::Tensor> Nu(
                torch::Tensor pmc_b, torch::Tensor pmc_mu, 
                torch::Tensor met_xy, 
                torch::Tensor masses, 
                torch::Tensor sigma, const double null); 

        std::map<std::string, torch::Tensor> NuNu(
                torch::Tensor pmc_b1, torch::Tensor pmc_b2, 
                torch::Tensor pmc_l1, torch::Tensor pmc_l2,
                torch::Tensor met_xy, 
                torch::Tensor masses, const double null); 

        namespace Polar
        {
            std::map<std::string, torch::Tensor> Nu(
                    torch::Tensor pmu_b, torch::Tensor pmu_mu, 
                    torch::Tensor met_phi, torch::Tensor masses, 
                    torch::Tensor sigma, const double null); 

            std::map<std::string, torch::Tensor> Nu(
                torch::Tensor pt_b, torch::Tensor eta_b, torch::Tensor phi_b, torch::Tensor e_b, 
                torch::Tensor pt_mu, torch::Tensor eta_mu, torch::Tensor phi_mu, torch::Tensor e_mu, 
                torch::Tensor met, torch::Tensor phi, torch::Tensor masses, 
                torch::Tensor sigma, const double null); 


            std::map<std::string, torch::Tensor> NuNu(
                torch::Tensor pmu_b1 , torch::Tensor pmu_b2, 
                torch::Tensor pmu_mu1, torch::Tensor pmu_mu2, 
                torch::Tensor met_phi, torch::Tensor masses, 
                const double null); 

            std::map<std::string, torch::Tensor> NuNu(
                torch::Tensor pt_b1, torch::Tensor eta_b1, torch::Tensor phi_b1, torch::Tensor e_b1, 
                torch::Tensor pt_b2, torch::Tensor eta_b2, torch::Tensor phi_b2, torch::Tensor e_b2, 

                torch::Tensor pt_mu1, torch::Tensor eta_mu1, torch::Tensor phi_mu1, torch::Tensor e_mu1, 
                torch::Tensor pt_mu2, torch::Tensor eta_mu2, torch::Tensor phi_mu2, torch::Tensor e_mu2, 

                torch::Tensor met, torch::Tensor phi, 
                torch::Tensor masses, const double null); 
        }

        namespace Cartesian
        {
            std::map<std::string, torch::Tensor> Nu(
                    torch::Tensor pmc_b, torch::Tensor pmc_mu, 
                    torch::Tensor met_xy, torch::Tensor masses, 
                    torch::Tensor sigma, const double null); 

            std::map<std::string, torch::Tensor> Nu(
                    torch::Tensor px_b, torch::Tensor py_b, torch::Tensor pz_b, torch::Tensor e_b, 
                    torch::Tensor px_mu, torch::Tensor py_mu, torch::Tensor pz_mu, torch::Tensor e_mu, 
                    torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, 
                    torch::Tensor sigma, const double null); 

            std::map<std::string, torch::Tensor> NuNu(
                torch::Tensor pmc_b1, torch::Tensor pmc_b2, 
                torch::Tensor pmc_mu1, torch::Tensor pmc_mu2,
                torch::Tensor met_xy, torch::Tensor masses, const double null); 

            std::map<std::string, torch::Tensor> NuNu(
                torch::Tensor px_b1, torch::Tensor py_b1, torch::Tensor pz_b1, torch::Tensor e_b1, 
                torch::Tensor px_b2, torch::Tensor py_b2, torch::Tensor pz_b2, torch::Tensor e_b2, 

                torch::Tensor px_mu1, torch::Tensor py_mu1, torch::Tensor pz_mu1, torch::Tensor e_mu1, 
                torch::Tensor px_mu2, torch::Tensor py_mu2, torch::Tensor pz_mu2, torch::Tensor e_mu2, 

                torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, const double null); 
        }
    }
}

#endif
