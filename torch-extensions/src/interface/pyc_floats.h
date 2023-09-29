#ifndef H_PYC_FLOATS
#define H_PYC_FLOATS

#include <transform/cartesian-floats/cartesian.h>
#include <transform/polar-floats/polar.h>
#include <nusol/nusol-floats/nusol.h>

namespace pyc
{
    namespace transform 
    {
        namespace separate
        {
            double Pt(double px, double py);
            double Eta(double px, double py, double pz); 
            double Phi(double px, double py); 
            std::vector<double> PtEtaPhi(double px, double py, double pz); 
            std::vector<double> PtEtaPhiE(double px, double py, double pz, double e); 

            double Px(double pt, double phi);
            double Py(double pt, double phi); 
            double Pz(double pt, double eta); 
            std::vector<double> PxPyPz(double pt, double eta, double phi); 
            std::vector<double> PxPyPzE(double pt, double eta, double phi, double e); 
        }
        namespace combined
        {
            std::vector<double> Pt(std::vector<std::vector<double>> pmc);
            std::vector<double> Eta(std::vector<std::vector<double>> pmc); 
            std::vector<double> Phi(std::vector<std::vector<double>> pmc);
            std::vector<std::vector<double>> PtEtaPhi(std::vector<std::vector<double>> pmc); 
            std::vector<std::vector<double>> PtEtaPhiE(std::vector<std::vector<double>> pmc); 

            std::vector<double> Px(std::vector<std::vector<double>> pmu);
            std::vector<double> Py(std::vector<std::vector<double>> pmu); 
            std::vector<double> Pz(std::vector<std::vector<double>> pmu); 
            std::vector<std::vector<double>> PxPyPz(std::vector<std::vector<double>> pmu); 
            std::vector<std::vector<double>> PxPyPzE(std::vector<std::vector<double>> pmu); 
        }
    }
    namespace nusol
    {
        namespace polar
        {
            namespace combined
            {
                std::vector<torch::Tensor> Nu(
                        std::vector<std::vector<double>> pmu_b, std::vector<std::vector<double>> pmu_mu,
                        std::vector<std::vector<double>> met_phi, 
                        std::vector<std::vector<double>> masses,
                        std::vector<std::vector<double>> sigma, const double null); 
    
                std::vector<torch::Tensor> NuNu(
                        std::vector<std::vector<double>> pmu_b1,  std::vector<std::vector<double>> pmu_b2, 
                        std::vector<std::vector<double>> pmu_mu1, std::vector<std::vector<double>> pmu_mu2,
                        std::vector<std::vector<double>> met_phi, 
                        std::vector<std::vector<double>> masses, const double null);
            }
        }
        namespace cartesian
        {
            namespace combined
            {
                std::vector<torch::Tensor> Nu(
                        std::vector<std::vector<double>> pmc_b, std::vector<std::vector<double>> pmc_mu,
                        std::vector<std::vector<double>> met_xy, 
                        std::vector<std::vector<double>> masses,
                        std::vector<std::vector<double>> sigma, const double null); 
                
                std::vector<torch::Tensor> NuNu(
                        std::vector<std::vector<double>> pmc_b1,  std::vector<std::vector<double>> pmc_b2, 
                        std::vector<std::vector<double>> pmc_mu1, std::vector<std::vector<double>> pmc_mu2,
                        std::vector<std::vector<double>> met_xy, 
                        std::vector<std::vector<double>> masses, const double null); 
            }
        }
    }
}

#endif
