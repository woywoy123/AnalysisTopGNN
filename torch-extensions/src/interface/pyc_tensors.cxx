#include <torch/extension.h>
#include "pyc_tensors.h"

// ======= Transform ========= //
torch::Tensor pyc::transform::separate::Pt(
        torch::Tensor px, torch::Tensor py)
{ 
    return Transform::Tensors::Pt(px, py); 
}

torch::Tensor pyc::transform::separate::Eta(
        torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{ 
    return Transform::Tensors::Eta(px, py, pz); 
}

torch::Tensor pyc::transform::separate::Phi(
        torch::Tensor px, torch::Tensor py)
{ 
    return Transform::Tensors::Phi(px, py); 
}

torch::Tensor pyc::transform::separate::PtEtaPhi(
        torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{ 
    return Transform::Tensors::PtEtaPhi(px, py, pz); 
}

torch::Tensor pyc::transform::separate::PtEtaPhiE(
        torch::Tensor px, torch::Tensor py, 
        torch::Tensor pz, torch::Tensor e)
{ 
    return Transform::Tensors::PtEtaPhiE(px, py, pz, e); 
}

torch::Tensor pyc::transform::separate::Px(
        torch::Tensor pt, torch::Tensor phi)
{ 
    return Transform::Tensors::Px(pt, phi); 
}

torch::Tensor pyc::transform::separate::Py(
        torch::Tensor pt, torch::Tensor phi)
{ 
    return Transform::Tensors::Py(pt, phi); 
}

torch::Tensor pyc::transform::separate::Pz(
        torch::Tensor pt, torch::Tensor eta)
{ 
    return Transform::Tensors::Pz(pt, eta); 
}

torch::Tensor pyc::transform::separate::PxPyPz(
        torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
{ 
    return Transform::Tensors::PxPyPz(pt, eta, phi); 
}

torch::Tensor pyc::transform::separate::PxPyPzE(
        torch::Tensor pt, torch::Tensor eta, 
        torch::Tensor phi, torch::Tensor e)
{ 
    return Transform::Tensors::PxPyPzE(pt, eta, phi, e); 
}

torch::Tensor pyc::transform::combined::Pt(torch::Tensor pmc)
{ 
    return Transform::Tensors::Pt(pmc); 
}

torch::Tensor pyc::transform::combined::Eta(torch::Tensor pmc)
{ 
    return Transform::Tensors::Eta(pmc); 
}

torch::Tensor pyc::transform::combined::Phi(torch::Tensor pmc)
{ 
    return Transform::Tensors::Phi(pmc); 
}

torch::Tensor pyc::transform::combined::PtEtaPhi(torch::Tensor pmc)
{ 
    return Transform::Tensors::PtEtaPhi(pmc); 
}

torch::Tensor pyc::transform::combined::PtEtaPhiE(torch::Tensor pmc)
{ 
    return Transform::Tensors::PtEtaPhiE(pmc); 
}

torch::Tensor pyc::transform::combined::Px(torch::Tensor pmu)
{ 
    return Transform::Tensors::Px(pmu); 
}

torch::Tensor pyc::transform::combined::Py(torch::Tensor pmu)
{ 
    return Transform::Tensors::Py(pmu); 
}

torch::Tensor pyc::transform::combined::Pz(torch::Tensor pmu)
{ 
    return Transform::Tensors::Pz(pmu); 
}

torch::Tensor pyc::transform::combined::PxPyPz(torch::Tensor pmu)
{ 
    return Transform::Tensors::PxPyPz(pmu); 
}

torch::Tensor pyc::transform::combined::PxPyPzE(torch::Tensor pmu)
{ 
    return Transform::Tensors::PxPyPzE(pmu); 
}

// ======= Physics ========= //
torch::Tensor pyc::physics::cartesian::separate::P2(
        torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
    return Physics::Tensors::Cartesian::P2(px, py, pz);
}

torch::Tensor pyc::physics::cartesian::combined::P2(torch::Tensor pmc)
{
    return Physics::Tensors::Cartesian::P2(pmc);
}

torch::Tensor pyc::physics::cartesian::separate::P(
        torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
    return Physics::Tensors::Cartesian::P(px, py, pz);
}

torch::Tensor pyc::physics::cartesian::combined::P(torch::Tensor pmc)
{
    return Physics::Tensors::Cartesian::P(pmc);
}

torch::Tensor pyc::physics::polar::separate::P2(
        torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
{
    return Physics::Tensors::Polar::P2(pt, eta, phi);
}

torch::Tensor pyc::physics::polar::combined::P2(torch::Tensor pmu)
{
    return Physics::Tensors::Polar::P2(pmu);
}

torch::Tensor pyc::physics::polar::separate::P(
        torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
{
    return Physics::Tensors::Polar::P(pt, eta, phi);
}

torch::Tensor pyc::physics::polar::combined::P(torch::Tensor pmu)
{
    return Physics::Tensors::Polar::P(pmu);
}

torch::Tensor pyc::physics::cartesian::separate::Beta2(
        torch::Tensor px, torch::Tensor py, 
        torch::Tensor pz, torch::Tensor e)
{
    return Physics::Tensors::Cartesian::Beta2(px, py, pz, e);
}

torch::Tensor pyc::physics::cartesian::combined::Beta2(torch::Tensor pmc)
{
    return Physics::Tensors::Cartesian::Beta2(pmc);
}

torch::Tensor pyc::physics::cartesian::separate::Beta(
        torch::Tensor px, torch::Tensor py, 
        torch::Tensor pz, torch::Tensor e)
{
    return Physics::Tensors::Cartesian::Beta(px, py, pz, e);
}

torch::Tensor pyc::physics::cartesian::combined::Beta(torch::Tensor pmc)
{
    return Physics::Tensors::Cartesian::Beta(pmc);
}

torch::Tensor pyc::physics::polar::separate::Beta2(
        torch::Tensor pt, torch::Tensor eta, 
        torch::Tensor phi, torch::Tensor e)
{
    return Physics::Tensors::Polar::Beta2(pt, eta, phi, e);
}

torch::Tensor pyc::physics::polar::combined::Beta2(torch::Tensor pmu)
{
    return Physics::Tensors::Polar::Beta2(pmu);
}

torch::Tensor pyc::physics::polar::separate::Beta(
        torch::Tensor pt, torch::Tensor eta, 
        torch::Tensor phi, torch::Tensor e)
{
    return Physics::Tensors::Polar::Beta(pt, eta, phi, e);
}

torch::Tensor pyc::physics::polar::combined::Beta(torch::Tensor pmu)
{
    return Physics::Tensors::Polar::Beta(pmu);
}

torch::Tensor pyc::physics::cartesian::separate::M2(
        torch::Tensor px, torch::Tensor py, 
        torch::Tensor pz, torch::Tensor e)
{ 
    return Physics::Tensors::Cartesian::M2(px, py, pz, e); 
}

torch::Tensor pyc::physics::cartesian::combined::M2(torch::Tensor pmc)
{ 
    return Physics::Tensors::Cartesian::M2(pmc); 
}

torch::Tensor pyc::physics::cartesian::separate::M(
        torch::Tensor px, torch::Tensor py, 
        torch::Tensor pz, torch::Tensor e)
{ 
    return Physics::Tensors::Cartesian::M(px, py, pz, e); 
}

torch::Tensor pyc::physics::cartesian::combined::M(torch::Tensor pmc)
{ 
    return Physics::Tensors::Cartesian::M(pmc); 
}

torch::Tensor pyc::physics::cartesian::separate::Mt2(torch::Tensor pz, torch::Tensor e)
{ 
    return Physics::Tensors::Cartesian::Mt2(pz, e); 
}

torch::Tensor pyc::physics::cartesian::combined::Mt2(torch::Tensor pmc)
{ 
    return Physics::Tensors::Cartesian::Mt2(pmc); 
}

torch::Tensor pyc::physics::cartesian::separate::Mt(torch::Tensor pz, torch::Tensor e)
{ 
    return Physics::Tensors::Cartesian::Mt(pz, e); 
}

torch::Tensor pyc::physics::cartesian::combined::Mt(torch::Tensor pmc)
{ 
    return Physics::Tensors::Cartesian::Mt(pmc); 
}

torch::Tensor pyc::physics::cartesian::separate::Theta(
        torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{ 
    return Physics::Tensors::Cartesian::Theta(px, py, pz); 
}

torch::Tensor pyc::physics::cartesian::combined::Theta(torch::Tensor pmc)
{ 
    return Physics::Tensors::Cartesian::Theta(pmc); 
}

torch::Tensor pyc::physics::cartesian::separate::DeltaR(
        torch::Tensor px1, torch::Tensor px2, 
        torch::Tensor py1, torch::Tensor py2, 
        torch::Tensor pz1, torch::Tensor pz2)
{ 
    return Physics::Tensors::Cartesian::DeltaR(px1, px2, py1, py2, pz1, pz2); 
}

torch::Tensor pyc::physics::cartesian::combined::DeltaR(
        torch::Tensor pmc1, torch::Tensor pmc2)
{ 
    return Physics::Tensors::Cartesian::DeltaR(pmc1, pmc2); 
} 

torch::Tensor pyc::physics::polar::separate::M2(
        torch::Tensor pt, torch::Tensor eta, 
        torch::Tensor phi, torch::Tensor e)
{ 
    return Physics::Tensors::Polar::M2(pt, eta, phi, e); 
}

torch::Tensor pyc::physics::polar::combined::M2(torch::Tensor pmu)
{ 
    return Physics::Tensors::Polar::M2(pmu); 
}

torch::Tensor pyc::physics::polar::separate::M(
        torch::Tensor pt, torch::Tensor eta, 
        torch::Tensor phi, torch::Tensor e)
{ 
    return Physics::Tensors::Polar::M(pt, eta, phi, e); 
}

torch::Tensor pyc::physics::polar::combined::M(torch::Tensor pmu)
{ 
    return Physics::Tensors::Polar::M(pmu); 
} 

torch::Tensor pyc::physics::polar::separate::Mt2(
        torch::Tensor pt, torch::Tensor eta, torch::Tensor e)
{ 
    return Physics::Tensors::Polar::Mt2(pt, eta, e); 
}

torch::Tensor pyc::physics::polar::combined::Mt2(torch::Tensor pmu)
{ 
    return Physics::Tensors::Polar::Mt2(pmu); 
}

torch::Tensor pyc::physics::polar::separate::Mt(
        torch::Tensor pt, torch::Tensor eta, torch::Tensor e)
{ 
    return Physics::Tensors::Polar::Mt(pt, eta, e); 
}

torch::Tensor pyc::physics::polar::combined::Mt(torch::Tensor pmu)
{ 
    return Physics::Tensors::Polar::Mt(pmu); 
} 

torch::Tensor pyc::physics::polar::separate::Theta(
        torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
{ 
    return Physics::Tensors::Polar::Theta(pt, eta, phi); 
}

torch::Tensor pyc::physics::polar::combined::Theta(torch::Tensor pmu)
{
    return Physics::Tensors::Polar::Theta(pmu); 
}

torch::Tensor pyc::physics::polar::separate::DeltaR(
        torch::Tensor eta1, torch::Tensor eta2, 
        torch::Tensor phi1, torch::Tensor phi2)
{ 
    return Physics::Tensors::Polar::DeltaR(eta1, eta2, phi1, phi2); 
} 

torch::Tensor pyc::physics::polar::combined::DeltaR(
        torch::Tensor pmu1, torch::Tensor pmu2)
{ 
    return Physics::Tensors::Polar::DeltaR(pmu1, pmu2); 
} 

// Operators
torch::Tensor pyc::operators::Dot(
        torch::Tensor v1, torch::Tensor v2)
{ 
    return Operators::Tensors::Dot(v1, v2); 
}

torch::Tensor pyc::operators::Mul(
        torch::Tensor v1, torch::Tensor v2)
{ 
    return Operators::Tensors::Mul(v1, v2); 
}

torch::Tensor pyc::operators::CosTheta(
        torch::Tensor v1, torch::Tensor v2)
{ 
    return Operators::Tensors::CosTheta(v1, v2); 
}

torch::Tensor pyc::operators::SinTheta(
        torch::Tensor v1, torch::Tensor v2)
{ 
    return Operators::Tensors::SinTheta(v1, v2); 
}

torch::Tensor pyc::operators::Rx(torch::Tensor angle)
{
    return Operators::Tensors::Rx(angle); 
}

torch::Tensor pyc::operators::Ry(torch::Tensor angle)
{ 
    return Operators::Tensors::Ry(angle); 
}

torch::Tensor pyc::operators::Rz(torch::Tensor angle)
{ 
    return Operators::Tensors::Rz(angle); 
}

torch::Tensor pyc::operators::CoFactors(torch::Tensor matrix)
{ 
    return Operators::Tensors::CoFactors(matrix); 
}

torch::Tensor pyc::operators::Determinant(torch::Tensor matrix)
{
    return Operators::Tensors::Determinant(matrix); 
}

torch::Tensor pyc::operators::Inverse(torch::Tensor matrix)
{ 
    return Operators::Tensors::Inverse(matrix); 
}

torch::Tensor pyc::nusol::BaseMatrix(
        torch::Tensor pmc_b, torch::Tensor pmc_mu, 
        torch::Tensor masses)
{ 
    return NuSol::Tensor::BaseMatrix(pmc_b, pmc_mu, masses); 
}

std::tuple<torch::Tensor, torch::Tensor> pyc::nusol::Intersection(
        torch::Tensor A, torch::Tensor B, const double null)
{ 
    return NuSol::Tensor::Intersection(A, B, null); 
}

std::vector<torch::Tensor> pyc::nusol::Nu(
        torch::Tensor pmc_b, torch::Tensor pmc_mu, 
        torch::Tensor met_xy, torch::Tensor masses, 
        torch::Tensor sigma, const double null)
{ 
    std::map<std::string, torch::Tensor> out; 
    if (null == -1)
    {
        out = NuSol::Tensor::Nu(pmc_b, pmc_mu, met_xy, masses, sigma); 
        return {out["M"]}; 
    }
    out = NuSol::Tensor::Nu(pmc_b, pmc_mu, met_xy, masses, sigma, null);
    return {out["NuVec"], out["chi2"]}; 
}

std::vector<torch::Tensor> pyc::nusol::polar::combined::Nu(
        torch::Tensor pmu_b, torch::Tensor pmu_mu, 
        torch::Tensor met_phi, torch::Tensor masses, 
        torch::Tensor sigma, const double null)
{
    std::map<std::string, torch::Tensor> out;
    out  = NuSol::Tensor::Polar::Nu(pmu_b, pmu_mu, met_phi, masses, sigma, null);   
    return {out["NuVec"], out["chi2"]}; 
}

std::vector<torch::Tensor> pyc::nusol::polar::separate::Nu(
        torch::Tensor pt_b, torch::Tensor eta_b, torch::Tensor phi_b, torch::Tensor e_b, 
        torch::Tensor pt_mu, torch::Tensor eta_mu, torch::Tensor phi_mu, torch::Tensor e_mu, 
        torch::Tensor met, torch::Tensor phi, torch::Tensor masses, 
        torch::Tensor sigma, const double null)
{
    std::map<std::string, torch::Tensor> out;
    out  = NuSol::Tensor::Polar::Nu(
            pt_b, eta_b, phi_b, e_b, 
            pt_mu, eta_mu, phi_mu, e_mu, 
            met, phi, masses, sigma, null); 
    return {out["NuVec"], out["chi2"]}; 
}

std::vector<torch::Tensor> pyc::nusol::cartesian::combined::Nu(
        torch::Tensor pmc_b, torch::Tensor pmc_mu, 
        torch::Tensor met_xy, torch::Tensor masses, 
        torch::Tensor sigma, const double null)
{
    std::map<std::string, torch::Tensor> out;
    out  = NuSol::Tensor::Cartesian::Nu(pmc_b, pmc_mu, met_xy, masses, sigma, null);   
    return {out["NuVec"], out["chi2"]}; 
}


std::vector<torch::Tensor> pyc::nusol::cartesian::separate::Nu(
        torch::Tensor px_b , torch::Tensor py_b , torch::Tensor pz_b , torch::Tensor e_b, 
        torch::Tensor px_mu, torch::Tensor py_mu, torch::Tensor pz_mu, torch::Tensor e_mu, 
        torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, 
        torch::Tensor sigma, const double null)
{
    std::map<std::string, torch::Tensor> out;
    out  = NuSol::Tensor::Cartesian::Nu(
            px_b , py_b , pz_b , e_b, 
            px_mu, py_mu, pz_mu, e_mu, 
            metx, mety, masses, sigma, null); 
    return {out["NuVec"], out["chi2"]}; 
}

std::vector<torch::Tensor> pyc::nusol::NuNu(
        torch::Tensor pmc_b1, torch::Tensor pmc_b2, 
        torch::Tensor pmc_l1, torch::Tensor pmc_l2, 
        torch::Tensor met_xy, torch::Tensor masses, const double null)
{ 
    std::map<std::string, torch::Tensor> out; 
    out = NuSol::Tensor::NuNu(pmc_b1, pmc_b2, pmc_l1, pmc_l2, met_xy, masses, null);
    return { 
        out["NuVec_1"] , out["NuVec_2"], out["diagonal"], out["n_"],     
        out["H_perp_1"], out["H_perp_2"], out["NoSols"]
    }; 
}

std::vector<torch::Tensor> pyc::nusol::polar::combined::NuNu(
        torch::Tensor pmu_b1 , torch::Tensor pmu_b2, 
        torch::Tensor pmu_mu1, torch::Tensor pmu_mu2, 
        torch::Tensor met_phi, torch::Tensor masses, 
        const double null) 
{ 
    std::map<std::string, torch::Tensor> out; 
    out = NuSol::Tensor::Polar::NuNu(pmu_b1, pmu_b2, pmu_mu1, pmu_mu2, met_phi, masses, null);
    return { 
        out["NuVec_1"] , out["NuVec_2"], out["diagonal"], out["n_"],     
        out["H_perp_1"], out["H_perp_2"], out["NoSols"]
    }; 
}

std::vector<torch::Tensor> pyc::nusol::polar::separate::NuNu(
        torch::Tensor pt_b1, torch::Tensor eta_b1, torch::Tensor phi_b1, torch::Tensor e_b1, 
        torch::Tensor pt_b2, torch::Tensor eta_b2, torch::Tensor phi_b2, torch::Tensor e_b2, 

        torch::Tensor pt_mu1, torch::Tensor eta_mu1, torch::Tensor phi_mu1, torch::Tensor e_mu1, 
        torch::Tensor pt_mu2, torch::Tensor eta_mu2, torch::Tensor phi_mu2, torch::Tensor e_mu2, 

        torch::Tensor met, torch::Tensor phi, 
        torch::Tensor masses, const double null)
{ 
    std::map<std::string, torch::Tensor> out; 
    out = NuSol::Tensor::Polar::NuNu(
        pt_b1,  eta_b1 , phi_b1 , e_b1 , pt_b2 , eta_b2 , phi_b2 , e_b2 , 
        pt_mu1, eta_mu1, phi_mu1, e_mu1, pt_mu2, eta_mu2, phi_mu2, e_mu2,
        met, phi, masses, null); 

    return { 
        out["NuVec_1"] , out["NuVec_2"], out["diagonal"], out["n_"],     
        out["H_perp_1"], out["H_perp_2"], out["NoSols"]
    }; 
}

std::vector<torch::Tensor> pyc::nusol::cartesian::combined::NuNu(
        torch::Tensor pmc_b1 , torch::Tensor pmc_b2, 
        torch::Tensor pmc_mu1, torch::Tensor pmc_mu2,
        torch::Tensor met_xy , torch::Tensor masses, const double null)
{ 
    std::map<std::string, torch::Tensor> out; 
    out = NuSol::Tensor::Cartesian::NuNu(pmc_b1, pmc_b2, pmc_mu1, pmc_mu2, met_xy, masses, null);
    return { 
        out["NuVec_1"] , out["NuVec_2"], out["diagonal"], out["n_"],     
        out["H_perp_1"], out["H_perp_2"], out["NoSols"]
    }; 
}

std::vector<torch::Tensor> pyc::nusol::cartesian::separate::NuNu(
        torch::Tensor px_b1, torch::Tensor py_b1, torch::Tensor pz_b1, torch::Tensor e_b1, 
        torch::Tensor px_b2, torch::Tensor py_b2, torch::Tensor pz_b2, torch::Tensor e_b2, 

        torch::Tensor px_mu1, torch::Tensor py_mu1, torch::Tensor pz_mu1, torch::Tensor e_mu1, 
        torch::Tensor px_mu2, torch::Tensor py_mu2, torch::Tensor pz_mu2, torch::Tensor e_mu2, 

        torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, const double null)
{ 
    std::map<std::string, torch::Tensor> out; 
    out = NuSol::Tensor::Cartesian::NuNu(
        px_b1 , py_b1 , pz_b1 , e_b1 , px_b2 , py_b2 , pz_b2 , e_b2 , 
        px_mu1, py_mu1, pz_mu1, e_mu1, px_mu2, py_mu2, pz_mu2, e_mu2, 
        metx, mety, masses, null);
    return { 
        out["NuVec_1"] , out["NuVec_2"], out["diagonal"], out["n_"],     
        out["H_perp_1"], out["H_perp_2"], out["NoSols"]
    }; 
}

std::vector<std::vector<torch::Tensor>> pyc::graph::dress(
        std::map<std::string, std::vector<torch::Tensor>> inpt)
{
    std::vector<std::vector<torch::Tensor>> output = {};
    std::map<std::string, std::vector<torch::Tensor>>::iterator it; 
    for (it = inpt.begin(); it != inpt.end(); ++it){output.push_back(it -> second);}
    return output; 
}

std::vector<std::vector<torch::Tensor>> pyc::graph::edge_aggregation(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor node_feature, const bool include_zero)
{
    std::map<std::string, std::vector<torch::Tensor>> map;
    map = Graph::Tensors::edge_aggregation(edge_index, prediction, node_feature, include_zero); 
    return pyc::graph::dress(map); 
}

std::vector<std::vector<torch::Tensor>> pyc::graph::node_aggregation(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor node_feature, const bool include_zero)
{
    std::map<std::string, std::vector<torch::Tensor>> map;
    map = Graph::Tensors::node_aggregation(edge_index, prediction, node_feature, include_zero); 
    return pyc::graph::dress(map); 
}

std::vector<std::vector<torch::Tensor>> pyc::graph::polar::combined::edge_pmu(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor pmu, const bool include_zero)
{
    std::map<std::string, std::vector<torch::Tensor>> map; 
    map = Graph::Tensors::Polar::edge_pmu(edge_index, prediction, pmu, include_zero);
    return pyc::graph::dress(map); 
}
std::vector<std::vector<torch::Tensor>> pyc::graph::polar::combined::node_pmu(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor pmu, const bool include_zero)
{
    std::map<std::string, std::vector<torch::Tensor>> map; 
    map = Graph::Tensors::Polar::node_pmu(edge_index, prediction, pmu, include_zero);
    return pyc::graph::dress(map); 
}

std::vector<std::vector<torch::Tensor>> pyc::graph::polar::separate::edge_pmu(
       torch::Tensor edge_index, torch::Tensor prediction, 
       torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  
       const bool include_zero)
{
    std::map<std::string, std::vector<torch::Tensor>> map; 
    map = Graph::Tensors::Polar::edge_pmu(edge_index, prediction, pt, eta, phi, e, include_zero);
    return pyc::graph::dress(map); 
}

std::vector<std::vector<torch::Tensor>> pyc::graph::polar::separate::node_pmu(
       torch::Tensor edge_index, torch::Tensor prediction, 
       torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  
       const bool include_zero)
{
    std::map<std::string, std::vector<torch::Tensor>> map; 
    map = Graph::Tensors::Polar::node_pmu(edge_index, prediction, pt, eta, phi, e, include_zero);
    return pyc::graph::dress(map); 
}

std::vector<std::vector<torch::Tensor>> pyc::graph::cartesian::combined::edge_pmc(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor pmc, const bool include_zero)
{
    std::map<std::string, std::vector<torch::Tensor>> map; 
    map = Graph::Tensors::Cartesian::edge_pmc(edge_index, prediction, pmc, include_zero);
    return pyc::graph::dress(map); 
}

std::vector<std::vector<torch::Tensor>> pyc::graph::cartesian::combined::node_pmc(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor pmc, const bool include_zero)
{
    std::map<std::string, std::vector<torch::Tensor>> map; 
    map = Graph::Tensors::Cartesian::node_pmc(edge_index, prediction, pmc, include_zero);
    return pyc::graph::dress(map); 
}

std::vector<std::vector<torch::Tensor>> pyc::graph::cartesian::separate::edge_pmc(
      torch::Tensor edge_index, torch::Tensor prediction, 
      torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  
      const bool include_zero)
{
    std::map<std::string, std::vector<torch::Tensor>> map; 
    map = Graph::Tensors::Cartesian::edge_pmc(edge_index, prediction, px, py, pz, e, include_zero);
    return pyc::graph::dress(map); 
}

std::vector<std::vector<torch::Tensor>> pyc::graph::cartesian::separate::node_pmc(
      torch::Tensor edge_index, torch::Tensor prediction, 
      torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  
      const bool include_zero)
{
    std::map<std::string, std::vector<torch::Tensor>> map; 
    map = Graph::Tensors::Cartesian::node_pmc(edge_index, prediction, px, py, pz, e, include_zero);
    return pyc::graph::dress(map); 
}

TORCH_LIBRARY(pyc_tensor, m)
{
    // transformation classes for Tensor
    m.def("transform_separate_Px",        &pyc::transform::separate::Px);
    m.def("transform_separate_Py",        &pyc::transform::separate::Py);
    m.def("transform_separate_Pz",        &pyc::transform::separate::Pz);
    m.def("transform_separate_PxPyPz",    &pyc::transform::separate::PxPyPz);
    m.def("transform_separate_PxPyPzE",   &pyc::transform::separate::PxPyPzE);

    m.def("transform_combined_Px",        &pyc::transform::combined::Px);
    m.def("transform_combined_Py",        &pyc::transform::combined::Py);
    m.def("transform_combined_Pz",        &pyc::transform::combined::Pz);
    m.def("transform_combined_PxPyPz",    &pyc::transform::combined::PxPyPz);
    m.def("transform_combined_PxPyPzE",   &pyc::transform::combined::PxPyPzE);

    m.def("transform_separate_Pt",        &pyc::transform::separate::Pt);
    m.def("transform_separate_Phi",       &pyc::transform::separate::Phi);
    m.def("transform_separate_Eta",       &pyc::transform::separate::Eta);
    m.def("transform_separate_PtEtaPhi",  &pyc::transform::separate::PtEtaPhi);
    m.def("transform_separate_PtEtaPhiE", &pyc::transform::separate::PtEtaPhiE);

    m.def("transform_combined_Pt",        &pyc::transform::combined::Pt);
    m.def("transform_combined_Phi",       &pyc::transform::combined::Phi);
    m.def("transform_combined_Eta",       &pyc::transform::combined::Eta);
    m.def("transform_combined_PtEtaPhi",  &pyc::transform::combined::PtEtaPhi);
    m.def("transform_combined_PtEtaPhiE", &pyc::transform::combined::PtEtaPhiE);

    m.def("physics_separate_cartesian_P2", &pyc::physics::cartesian::separate::P2); 
    m.def("physics_combined_cartesian_P2", &pyc::physics::cartesian::combined::P2); 
    m.def("physics_separate_cartesian_P",  &pyc::physics::cartesian::separate::P); 
    m.def("physics_combined_cartesian_P",  &pyc::physics::cartesian::combined::P); 

    m.def("physics_separate_polar_P2", &pyc::physics::polar::separate::P2);  
    m.def("physics_combined_polar_P2", &pyc::physics::polar::combined::P2);  
    m.def("physics_separate_polar_P",  &pyc::physics::polar::separate::P); 
    m.def("physics_combined_polar_P",  &pyc::physics::polar::combined::P); 

    m.def("physics_separate_cartesian_Beta2", &pyc::physics::cartesian::separate::Beta2); 
    m.def("physics_combined_cartesian_Beta2", &pyc::physics::cartesian::combined::Beta2); 
    m.def("physics_separate_polar_Beta2", &pyc::physics::polar::separate::Beta2);  
    m.def("physics_combined_polar_Beta2", &pyc::physics::polar::combined::Beta2);  
 
    m.def("physics_separate_cartesian_Beta",  &pyc::physics::cartesian::separate::Beta); 
    m.def("physics_combined_cartesian_Beta",  &pyc::physics::cartesian::combined::Beta); 
    m.def("physics_separate_polar_Beta",  &pyc::physics::polar::separate::Beta); 
    m.def("physics_combined_polar_Beta",  &pyc::physics::polar::combined::Beta); 

    m.def("physics_separate_cartesian_M2", &pyc::physics::cartesian::separate::M2);          
    m.def("physics_combined_cartesian_M2", &pyc::physics::cartesian::combined::M2);          
    m.def("physics_separate_polar_M2", &pyc::physics::polar::separate::M2); 
    m.def("physics_combined_polar_M2", &pyc::physics::polar::combined::M2);

    m.def("physics_separate_cartesian_M", &pyc::physics::cartesian::separate::M);          
    m.def("physics_combined_cartesian_M", &pyc::physics::cartesian::combined::M);           
    m.def("physics_separate_polar_M", &pyc::physics::polar::separate::M);
    m.def("physics_combined_polar_M", &pyc::physics::polar::combined::M);
 
    m.def("physics_separate_polar_Mt2", &pyc::physics::polar::separate::Mt2);
    m.def("physics_combined_polar_Mt2", &pyc::physics::polar::combined::Mt2);
    m.def("physics_separate_cartesian_Mt2", &pyc::physics::cartesian::separate::Mt2);         
    m.def("physics_combined_cartesian_Mt2", &pyc::physics::cartesian::combined::Mt2);         
 
    m.def("physics_separate_polar_Mt", &pyc::physics::polar::separate::Mt);
    m.def("physics_combined_polar_Mt", &pyc::physics::polar::combined::Mt);
    m.def("physics_separate_cartesian_Mt", &pyc::physics::cartesian::separate::Mt);          
    m.def("physics_combined_cartesian_Mt", &pyc::physics::cartesian::combined::Mt);          
    
    m.def("physics_separate_cartesian_Theta", &pyc::physics::cartesian::separate::Theta);       
    m.def("physics_combined_cartesian_Theta", &pyc::physics::cartesian::combined::Theta);       
    m.def("physics_separate_polar_Theta", &pyc::physics::polar::separate::Theta); 
    m.def("physics_combined_polar_Theta", &pyc::physics::polar::combined::Theta); 

    m.def("physics_separate_cartesian_DeltaR", &pyc::physics::cartesian::separate::DeltaR);      
    m.def("physics_combined_cartesian_DeltaR", &pyc::physics::cartesian::combined::DeltaR);      
    m.def("physics_separate_polar_DeltaR", &pyc::physics::polar::separate::DeltaR);
    m.def("physics_combined_polar_DeltaR", &pyc::physics::polar::combined::DeltaR);

    m.def("operators_Dot", &pyc::operators::Dot); 
    m.def("operators_Mul", &pyc::operators::Mul); 
    m.def("operators_CosTheta", &pyc::operators::CosTheta); 
    m.def("operators_SinTheta", &pyc::operators::SinTheta); 

    m.def("operators_Rx", &pyc::operators::Rx); 
    m.def("operators_Ry", &pyc::operators::Ry); 
    m.def("operators_Rz", &pyc::operators::Rz); 
 
    m.def("operators_CoFactors",   &pyc::operators::CoFactors); 
    m.def("operators_Determinant", &pyc::operators::Determinant); 
    m.def("operators_Inverse",     &pyc::operators::Inverse); 

    m.def("nusol_BaseMatrix",   &pyc::nusol::BaseMatrix);
    m.def("nusol_Intersection", &pyc::nusol::Intersection); 

    m.def("nusol_Nu", &pyc::nusol::Nu);
    m.def("nusol_combined_polar_Nu", &pyc::nusol::polar::combined::Nu); 
    m.def("nusol_separate_polar_Nu", &pyc::nusol::polar::separate::Nu); 
    m.def("nusol_combined_cartesian_Nu", &pyc::nusol::cartesian::combined::Nu); 
    m.def("nusol_separate_cartesian_Nu", &pyc::nusol::cartesian::separate::Nu); 

    m.def("nusol_NuNu", &pyc::nusol::NuNu); 
    m.def("nusol_combined_polar_NuNu", &pyc::nusol::polar::combined::NuNu); 
    m.def("nusol_separate_polar_NuNu", &pyc::nusol::polar::separate::NuNu); 
    m.def("nusol_combined_cartesian_NuNu", &pyc::nusol::cartesian::combined::NuNu); 
    m.def("nusol_separate_cartesian_NuNu", &pyc::nusol::cartesian::separate::NuNu); 
  
    m.def("graph_base_combined_edge_aggregation", &pyc::graph::edge_aggregation); 
    m.def("graph_base_combined_node_aggregation", &pyc::graph::node_aggregation); 

    m.def("graph_polar_combined_edge", &pyc::graph::polar::combined::edge_pmu); 
    m.def("graph_polar_combined_node", &pyc::graph::polar::combined::node_pmu); 

    m.def("graph_polar_separate_edge", &pyc::graph::polar::separate::edge_pmu); 
    m.def("graph_polar_separate_node", &pyc::graph::polar::separate::node_pmu); 

    m.def("graph_cartesian_combined_edge", &pyc::graph::cartesian::combined::edge_pmc); 
    m.def("graph_cartesian_combined_node", &pyc::graph::cartesian::combined::node_pmc); 

    m.def("graph_cartesian_separate_edge", &pyc::graph::cartesian::separate::edge_pmc); 
    m.def("graph_cartesian_separate_node", &pyc::graph::cartesian::separate::node_pmc); 
}
