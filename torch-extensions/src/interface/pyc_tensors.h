#ifndef H_PYC_TENSORS_
#define H_PYC_TENSORS_

#include <transform/cartesian-tensors/cartesian.h>
#include <transform/polar-tensors/polar.h>
#include <physics/physics-tensor/physics.h>
#include <physics/physics-tensor/cartesian.h>
#include <physics/physics-tensor/polar.h>
#include <operators/operators-tensor/operators.h>
#include <nusol/nusol-tensor/nusol.h>
#include <graph/graph-tensor/graph.h>


namespace pyc
{
    namespace transform
    {
        namespace separate
        {
            torch::Tensor Pt(torch::Tensor px, torch::Tensor py); 
            torch::Tensor Eta(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
            torch::Tensor Phi(torch::Tensor px, torch::Tensor py); 
            torch::Tensor PtEtaPhi(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
            torch::Tensor PtEtaPhiE(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);

            torch::Tensor Px(torch::Tensor pt, torch::Tensor phi); 
            torch::Tensor Py(torch::Tensor pt, torch::Tensor phi); 
            torch::Tensor Pz(torch::Tensor pt, torch::Tensor eta); 
            torch::Tensor PxPyPz(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi); 
            torch::Tensor PxPyPzE(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e); 
        }
        namespace combined
        {
            torch::Tensor Pt(torch::Tensor pmc); 
            torch::Tensor Eta(torch::Tensor pmc); 
            torch::Tensor Phi(torch::Tensor pmc); 
            torch::Tensor PtEtaPhi(torch::Tensor pmc); 
            torch::Tensor PtEtaPhiE(torch::Tensor pmc); 

            torch::Tensor Px(torch::Tensor pmu); 
            torch::Tensor Py(torch::Tensor pmu); 
            torch::Tensor Pz(torch::Tensor pmu); 
            torch::Tensor PxPyPz(torch::Tensor pmu); 
            torch::Tensor PxPyPzE(torch::Tensor pmu); 
        }
    }  

    namespace physics
    {
        namespace cartesian
        {
            namespace separate
            {
                torch::Tensor P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
                torch::Tensor P (torch::Tensor px, torch::Tensor py, torch::Tensor pz);
                torch::Tensor Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);
                torch::Tensor Beta (torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);
                torch::Tensor M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);
                torch::Tensor M (torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);
                torch::Tensor Mt2(torch::Tensor pz, torch::Tensor e);
                torch::Tensor Mt (torch::Tensor pz, torch::Tensor e);
                torch::Tensor Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
                torch::Tensor DeltaR(torch::Tensor px1, torch::Tensor px2, torch::Tensor py1, torch::Tensor py2, torch::Tensor pz1, torch::Tensor pz2);

            }

            namespace combined 
            {
                torch::Tensor P2(torch::Tensor pmc); 
                torch::Tensor P(torch::Tensor pmc); 
                torch::Tensor Beta2(torch::Tensor pmc); 
                torch::Tensor Beta(torch::Tensor pmc); 
                torch::Tensor M2(torch::Tensor pmc);
                torch::Tensor M(torch::Tensor pmc);
                torch::Tensor Mt2(torch::Tensor pmc);
                torch::Tensor Mt(torch::Tensor pmc);
                torch::Tensor Theta(torch::Tensor pmc); 
                torch::Tensor DeltaR(torch::Tensor pmc1, torch::Tensor pmc2); 
            }
        }
        namespace polar
        {

            namespace separate
            {
                torch::Tensor P2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi); 
                torch::Tensor P(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi); 
                torch::Tensor Beta2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e); 
                torch::Tensor Beta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e); 
                torch::Tensor M2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e); 
                torch::Tensor M(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e); 
                torch::Tensor Mt2(torch::Tensor pt, torch::Tensor eta, torch::Tensor e); 
                torch::Tensor Mt(torch::Tensor pt, torch::Tensor eta, torch::Tensor e); 
                torch::Tensor Theta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi); 
                torch::Tensor DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2); 
            }

            namespace combined 
            {
                torch::Tensor P2(torch::Tensor pmu); 
                torch::Tensor P(torch::Tensor pmu); 
                torch::Tensor Beta2(torch::Tensor pmu); 
                torch::Tensor Beta(torch::Tensor pmu); 
                torch::Tensor M2(torch::Tensor pmu); 
                torch::Tensor M(torch::Tensor pmu); 
                torch::Tensor Mt2(torch::Tensor pmu); 
                torch::Tensor Mt(torch::Tensor pmu); 
                torch::Tensor Theta(torch::Tensor pmu); 
                torch::Tensor DeltaR(torch::Tensor pmu1, torch::Tensor pmu2); 
            }
        }
    }
    
    namespace operators
    {
        torch::Tensor Dot(torch::Tensor v1, torch::Tensor v2); 
        torch::Tensor Mul(torch::Tensor v1, torch::Tensor v2); 
        torch::Tensor CosTheta(torch::Tensor v1, torch::Tensor v2); 
        torch::Tensor SinTheta(torch::Tensor v1, torch::Tensor v2);
        torch::Tensor Rx(torch::Tensor angle); 
        torch::Tensor Ry(torch::Tensor angle); 
        torch::Tensor Rz(torch::Tensor angle); 
        torch::Tensor CoFactors(torch::Tensor matrix);
        torch::Tensor Determinant(torch::Tensor matrix); 
        torch::Tensor Inverse(torch::Tensor matrix); 
    }

    namespace nusol
    {
        torch::Tensor BaseMatrix(
                torch::Tensor pmc_b, torch::Tensor pmc_mu, 
                torch::Tensor masses); 

        std::tuple<torch::Tensor, torch::Tensor> Intersection(
                torch::Tensor A, torch::Tensor B, const double null); 

        std::vector<torch::Tensor> Nu(
                torch::Tensor pmc_b, torch::Tensor pmc_mu, 
                torch::Tensor met_xy, torch::Tensor masses, 
                torch::Tensor sigma, const double null); 

        std::vector<torch::Tensor> NuNu(
                torch::Tensor pmc_b1, torch::Tensor pmc_b2, 
                torch::Tensor pmc_l1, torch::Tensor pmc_l2, 
                torch::Tensor met_xy, 
                torch::Tensor masses, const double null); 

        namespace polar
        {
            namespace combined 
            {
                std::vector<torch::Tensor> Nu(
                        torch::Tensor pmu_b, torch::Tensor pmu_mu, 
                        torch::Tensor met_phi, torch::Tensor masses, 
                        torch::Tensor sigma, const double null); 

                std::vector<torch::Tensor> NuNu(
                        torch::Tensor pmu_b1 , torch::Tensor pmu_b2, 
                        torch::Tensor pmu_mu1, torch::Tensor pmu_mu2, 
                        torch::Tensor met_phi, torch::Tensor masses, 
                        const double null); 
            }
            namespace separate
            {
                std::vector<torch::Tensor> Nu(
                        torch::Tensor pt_b, torch::Tensor eta_b, torch::Tensor phi_b, torch::Tensor e_b, 
                        torch::Tensor pt_mu, torch::Tensor eta_mu, torch::Tensor phi_mu, torch::Tensor e_mu, 
                        torch::Tensor met, torch::Tensor phi, torch::Tensor masses, 
                        torch::Tensor sigma, const double null); 

                std::vector<torch::Tensor> NuNu(
                        torch::Tensor pt_b1, torch::Tensor eta_b1, torch::Tensor phi_b1, torch::Tensor e_b1, 
                        torch::Tensor pt_b2, torch::Tensor eta_b2, torch::Tensor phi_b2, torch::Tensor e_b2, 
                
                        torch::Tensor pt_mu1, torch::Tensor eta_mu1, torch::Tensor phi_mu1, torch::Tensor e_mu1, 
                        torch::Tensor pt_mu2, torch::Tensor eta_mu2, torch::Tensor phi_mu2, torch::Tensor e_mu2, 
                
                        torch::Tensor met, torch::Tensor phi, 
                        torch::Tensor masses, const double null); 
            }
        }

        namespace cartesian
        {
            namespace combined
            {
                std::vector<torch::Tensor> Nu(
                        torch::Tensor pmc_b, torch::Tensor pmc_mu, 
                        torch::Tensor met_xy, torch::Tensor masses, 
                        torch::Tensor sigma, const double null); 

                std::vector<torch::Tensor> NuNu(
                        torch::Tensor pmc_b1, torch::Tensor pmc_b2, 
                        torch::Tensor pmc_mu1, torch::Tensor pmc_mu2,
                        torch::Tensor met_xy, torch::Tensor masses, const double null); 
            }
            namespace separate
            {
                std::vector<torch::Tensor> Nu(
                        torch::Tensor px_b , torch::Tensor py_b , torch::Tensor pz_b , torch::Tensor e_b, 
                        torch::Tensor px_mu, torch::Tensor py_mu, torch::Tensor pz_mu, torch::Tensor e_mu, 
                        torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, 
                        torch::Tensor sigma, const double null); 

                std::vector<torch::Tensor> NuNu(
                        torch::Tensor px_b1, torch::Tensor py_b1, torch::Tensor pz_b1, torch::Tensor e_b1, 
                        torch::Tensor px_b2, torch::Tensor py_b2, torch::Tensor pz_b2, torch::Tensor e_b2, 
                
                        torch::Tensor px_mu1, torch::Tensor py_mu1, torch::Tensor pz_mu1, torch::Tensor e_mu1, 
                        torch::Tensor px_mu2, torch::Tensor py_mu2, torch::Tensor pz_mu2, torch::Tensor e_mu2, 
                
                        torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, const double null); 
            }
        }
    }
    namespace graph
    {
        std::vector<std::vector<torch::Tensor>> dress(
                std::map<std::string, std::vector<torch::Tensor>> inpt); 

        std::vector<std::vector<torch::Tensor>> edge_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor node_feature, const bool include_zero); 

        std::vector<std::vector<torch::Tensor>> node_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor node_feature, const bool include_zero); 


        namespace polar
        {
            namespace combined
            {
                std::vector<std::vector<torch::Tensor>> edge_pmu(
                        torch::Tensor edge_index, torch::Tensor prediction, 
                        torch::Tensor pmu, const bool include_zero); 

                std::vector<std::vector<torch::Tensor>> node_pmu(
                        torch::Tensor edge_index, torch::Tensor prediction, 
                        torch::Tensor pmu, const bool include_zero); 
           }

            namespace separate
            {
                 std::vector<std::vector<torch::Tensor>> edge_pmu(
                        torch::Tensor edge_index, torch::Tensor prediction, 
                        torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  
                        const bool include_zero); 

                 std::vector<std::vector<torch::Tensor>> node_pmu(
                        torch::Tensor edge_index, torch::Tensor prediction, 
                        torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  
                        const bool include_zero);  
            }
        }

        namespace cartesian
        {
            namespace combined
            {
                std::vector<std::vector<torch::Tensor>> edge_pmc(
                        torch::Tensor edge_index, torch::Tensor prediction, 
                        torch::Tensor pmc, const bool include_zero); 

                std::vector<std::vector<torch::Tensor>> node_pmc(
                        torch::Tensor edge_index, torch::Tensor prediction, 
                        torch::Tensor pmc, const bool include_zero);  
            }

            namespace separate
            {
                std::vector<std::vector<torch::Tensor>> edge_pmc(
                      torch::Tensor edge_index, torch::Tensor prediction, 
                      torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  
                      const bool include_zero); 

                std::vector<std::vector<torch::Tensor>> node_pmc(
                      torch::Tensor edge_index, torch::Tensor prediction, 
                      torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  
                      const bool include_zero);  
            }
        }
    }
}
#endif
