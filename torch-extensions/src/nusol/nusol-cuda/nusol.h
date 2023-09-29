#ifndef H_NUSOL_CUDA
#define H_NUSOL_CUDA
#include <torch/torch.h>
#include <stdio.h>

torch::Tensor _Base_Matrix(
        torch::Tensor pmc_b, torch::Tensor pmc_mu, 
        torch::Tensor masses_W_top_nu); 

std::tuple<torch::Tensor, torch::Tensor> _Intersection(
        torch::Tensor A, torch::Tensor B, const double null); 

std::map<std::string, torch::Tensor> _Nu(
        torch::Tensor pmc_b, torch::Tensor pmc_mu, 
        torch::Tensor met_xy, torch::Tensor masses, 
        torch::Tensor sigma); 

std::map<std::string, torch::Tensor> _Nu(
        torch::Tensor pmc_b, torch::Tensor pmc_mu, 
        torch::Tensor met_xy, torch::Tensor masses, 
        torch::Tensor sigma, const double null); 

std::map<std::string, torch::Tensor> _NuPolar(
        torch::Tensor pmu_b, torch::Tensor pmu_mu, 
        torch::Tensor met_phi, torch::Tensor masses, 
        torch::Tensor sigma, const double null); 

std::map<std::string, torch::Tensor> _NuPolar(
        torch::Tensor pt_b, torch::Tensor eta_b, torch::Tensor phi_b, torch::Tensor e_b, 
        torch::Tensor pt_mu, torch::Tensor eta_mu, torch::Tensor phi_mu, torch::Tensor e_mu, 
        torch::Tensor met, torch::Tensor phi, torch::Tensor masses, 
        torch::Tensor sigma, const double null); 

std::map<std::string, torch::Tensor> _NuCart(
        torch::Tensor pmc_b, torch::Tensor pmc_mu, 
        torch::Tensor met_xy, torch::Tensor masses, 
        torch::Tensor sigma, const double null); 

std::map<std::string, torch::Tensor> _NuCart(
        torch::Tensor px_b, torch::Tensor py_b, torch::Tensor pz_b, torch::Tensor e_b, 
        torch::Tensor px_mu, torch::Tensor py_mu, torch::Tensor pz_mu, torch::Tensor e_mu, 
        torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, 
        torch::Tensor sigma, const double null); 


std::map<std::string, torch::Tensor> _NuNu(
        torch::Tensor pmc_b1, torch::Tensor pmc_b2, 
        torch::Tensor pmc_l1, torch::Tensor pmc_l2,
        torch::Tensor met_xy, torch::Tensor masses, 
        const double null);

std::map<std::string, torch::Tensor> _NuNuPolar(
        torch::Tensor pmu_b1 , torch::Tensor pmu_b2, 
        torch::Tensor pmu_mu1, torch::Tensor pmu_mu2, 
        torch::Tensor met_phi, torch::Tensor masses, 
        const double null); 

std::map<std::string, torch::Tensor> _NuNuPolar(
        torch::Tensor pt_b1, torch::Tensor eta_b1, torch::Tensor phi_b1, torch::Tensor e_b1, 
        torch::Tensor pt_b2, torch::Tensor eta_b2, torch::Tensor phi_b2, torch::Tensor e_b2, 

        torch::Tensor pt_mu1, torch::Tensor eta_mu1, torch::Tensor phi_mu1, torch::Tensor e_mu1, 
        torch::Tensor pt_mu2, torch::Tensor eta_mu2, torch::Tensor phi_mu2, torch::Tensor e_mu2, 

        torch::Tensor met, torch::Tensor phi, 
        torch::Tensor masses, const double null); 

std::map<std::string, torch::Tensor> _NuNuCart(
        torch::Tensor pmc_b1, torch::Tensor pmc_b2, 
        torch::Tensor pmc_mu1, torch::Tensor pmc_mu2,
        torch::Tensor met_xy, torch::Tensor masses, const double null); 

std::map<std::string, torch::Tensor> _NuNuCart(
        torch::Tensor px_b1, torch::Tensor py_b1, torch::Tensor pz_b1, torch::Tensor e_b1, 
        torch::Tensor px_b2, torch::Tensor py_b2, torch::Tensor pz_b2, torch::Tensor e_b2, 

        torch::Tensor px_mu1, torch::Tensor py_mu1, torch::Tensor pz_mu1, torch::Tensor e_mu1, 
        torch::Tensor px_mu2, torch::Tensor py_mu2, torch::Tensor pz_mu2, torch::Tensor e_mu2, 

        torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, const double null); 


namespace NuSol
{
    namespace CUDA
    {
        // masses = [W, Top, Neutrino]
        inline torch::Tensor BaseMatrix(
                torch::Tensor pmc_b, torch::Tensor pmc_mu, 
                torch::Tensor masses)
        {
            return _Base_Matrix(pmc_b, pmc_mu, masses);             
        }
      
        inline std::tuple<torch::Tensor, torch::Tensor> Intersection(
                torch::Tensor A, torch::Tensor B, const double null)
        {
            return _Intersection(A, B, null);  
        } 

        inline std::map<std::string, torch::Tensor> Nu(
                torch::Tensor pmc_b, torch::Tensor pmc_mu, 
                torch::Tensor met_xy, torch::Tensor masses, 
                torch::Tensor sigma)
        {
            return _Nu(pmc_b, pmc_mu, met_xy, masses, sigma); 
        }

        inline std::map<std::string, torch::Tensor> Nu(
                torch::Tensor pmc_b, torch::Tensor pmc_mu, 
                torch::Tensor met_xy, 
                torch::Tensor masses, 
                torch::Tensor sigma, const double null)
        {
            return _Nu(pmc_b, pmc_mu, met_xy, masses, sigma, null); 
        }

        inline std::map<std::string, torch::Tensor> NuNu(
                torch::Tensor pmc_b1, torch::Tensor pmc_b2, 
                torch::Tensor pmc_l1, torch::Tensor pmc_l2,
                torch::Tensor met_xy, 
                torch::Tensor masses, const double null)
        {
            return _NuNu(pmc_b1, pmc_b2, pmc_l1, pmc_l2, met_xy, masses, null); 
        }

        namespace Polar
        {
            inline std::map<std::string, torch::Tensor> Nu(
                    torch::Tensor pmu_b, torch::Tensor pmu_mu, 
                    torch::Tensor met_phi, torch::Tensor masses, 
                    torch::Tensor sigma, const double null)
            {
                return _NuPolar(pmu_b, pmu_mu, met_phi, masses, sigma, null); 
            }

            inline std::map<std::string, torch::Tensor> Nu(
                torch::Tensor pt_b, torch::Tensor eta_b, torch::Tensor phi_b, torch::Tensor e_b, 
                torch::Tensor pt_mu, torch::Tensor eta_mu, torch::Tensor phi_mu, torch::Tensor e_mu, 
                torch::Tensor met, torch::Tensor phi, torch::Tensor masses, 
                torch::Tensor sigma, const double null)
            {
                return _NuPolar(
                        pt_b , eta_b , phi_b , e_b, 
                        pt_mu, eta_mu, phi_mu, e_mu, 
                        met, phi, masses, sigma, null); 
            }


            inline std::map<std::string, torch::Tensor> NuNu(
                torch::Tensor pmu_b1 , torch::Tensor pmu_b2, 
                torch::Tensor pmu_mu1, torch::Tensor pmu_mu2, 
                torch::Tensor met_phi, torch::Tensor masses, 
                const double null)
            {
                return _NuNuPolar(pmu_b1, pmu_b2, pmu_mu1, pmu_mu2, met_phi, masses, null);
            }

            inline std::map<std::string, torch::Tensor> NuNu(
                torch::Tensor pt_b1, torch::Tensor eta_b1, torch::Tensor phi_b1, torch::Tensor e_b1, 
                torch::Tensor pt_b2, torch::Tensor eta_b2, torch::Tensor phi_b2, torch::Tensor e_b2, 

                torch::Tensor pt_mu1, torch::Tensor eta_mu1, torch::Tensor phi_mu1, torch::Tensor e_mu1, 
                torch::Tensor pt_mu2, torch::Tensor eta_mu2, torch::Tensor phi_mu2, torch::Tensor e_mu2, 

                torch::Tensor met, torch::Tensor phi, 
                torch::Tensor masses, const double null)
            {
                return _NuNuPolar(
                        pt_b1,  eta_b1,  phi_b1,  e_b1 , pt_b2,  eta_b2,  phi_b2,  e_b2, 
                        pt_mu1, eta_mu1, phi_mu1, e_mu1, pt_mu2, eta_mu2, phi_mu2, e_mu2, 
                        met, phi, masses, null);
            }
        }

        namespace Cartesian
        {
            inline std::map<std::string, torch::Tensor> Nu(
                    torch::Tensor pmc_b, torch::Tensor pmc_mu, 
                    torch::Tensor met_xy, torch::Tensor masses, 
                    torch::Tensor sigma, const double null)
            {
                return _NuCart(pmc_b, pmc_mu, met_xy, masses, sigma, null); 
            }

            inline std::map<std::string, torch::Tensor> Nu(
                    torch::Tensor px_b, torch::Tensor py_b, torch::Tensor pz_b, torch::Tensor e_b, 
                    torch::Tensor px_mu, torch::Tensor py_mu, torch::Tensor pz_mu, torch::Tensor e_mu, 
                    torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, 
                    torch::Tensor sigma, const double null)
            {
                return _NuCart(
                        px_b, py_b, pz_b, e_b, px_mu, py_mu, pz_mu, e_mu, 
                        metx, mety, masses, sigma, null); 
            }

            inline std::map<std::string, torch::Tensor> NuNu(
                torch::Tensor pmc_b1, torch::Tensor pmc_b2, 
                torch::Tensor pmc_mu1, torch::Tensor pmc_mu2,
                torch::Tensor met_xy, torch::Tensor masses, const double null)
            {
                return _NuNuCart(pmc_b1, pmc_b2, pmc_mu1, pmc_mu2, met_xy, masses, null);
            }

            inline std::map<std::string, torch::Tensor> NuNu(
                torch::Tensor px_b1, torch::Tensor py_b1, torch::Tensor pz_b1, torch::Tensor e_b1, 
                torch::Tensor px_b2, torch::Tensor py_b2, torch::Tensor pz_b2, torch::Tensor e_b2, 

                torch::Tensor px_mu1, torch::Tensor py_mu1, torch::Tensor pz_mu1, torch::Tensor e_mu1, 
                torch::Tensor px_mu2, torch::Tensor py_mu2, torch::Tensor pz_mu2, torch::Tensor e_mu2, 

                torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, const double null)
            {

                return _NuNuCart(
                        px_b1,  py_b1,  pz_b1,  e_b1, px_b2,  py_b2,  pz_b2,  e_b2, 
                        px_mu1, py_mu1, pz_mu1, e_mu1, px_mu2, py_mu2, pz_mu2, e_mu2, 
                        metx, mety, masses, null); 

            }

        }
    }
}

#endif
