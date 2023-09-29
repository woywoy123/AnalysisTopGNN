#include <torch/extension.h>
#include "pyc_floats.h"

double pyc::transform::separate::Pt(double px, double py){ return Transform::Floats::Pt(px, py); }
double pyc::transform::separate::Eta(double px, double py, double pz){ return Transform::Floats::Eta(px, py, pz); }
double pyc::transform::separate::Phi(double px, double py){ return Transform::Floats::Phi(px, py); }
std::vector<double> pyc::transform::separate::PtEtaPhi(double px, double py, double pz){ return Transform::Floats::PtEtaPhi(px, py, pz); }
std::vector<double> pyc::transform::separate::PtEtaPhiE(double px, double py, double pz, double e){ return Transform::Floats::PtEtaPhiE(px, py, pz, e); }

std::vector<double> pyc::transform::combined::Pt(std::vector<std::vector<double>> pmc){ return Transform::Floats::Pt(pmc); }
std::vector<double> pyc::transform::combined::Eta(std::vector<std::vector<double>> pmc){ return Transform::Floats::Eta(pmc); }
std::vector<double> pyc::transform::combined::Phi(std::vector<std::vector<double>> pmc){ return Transform::Floats::Phi(pmc); }
std::vector<std::vector<double>> pyc::transform::combined::PtEtaPhi(std::vector<std::vector<double>> pmc){ return Transform::Floats::PtEtaPhi(pmc); }
std::vector<std::vector<double>> pyc::transform::combined::PtEtaPhiE(std::vector<std::vector<double>> pmc){ return Transform::Floats::PtEtaPhiE(pmc); }

double pyc::transform::separate::Px(double pt, double phi){ return Transform::Floats::Px(pt, phi); }
double pyc::transform::separate::Py(double pt, double phi){ return Transform::Floats::Py(pt, phi); }
double pyc::transform::separate::Pz(double pt, double eta){ return Transform::Floats::Pz(pt, eta); }
std::vector<double> pyc::transform::separate::PxPyPz(double pt, double eta, double phi){ return Transform::Floats::PxPyPz(pt, eta, phi); }
std::vector<double> pyc::transform::separate::PxPyPzE(double pt, double eta, double phi, double e){ return Transform::Floats::PxPyPzE(pt, eta, phi, e); }

std::vector<double> pyc::transform::combined::Px(std::vector<std::vector<double>> pmu){ return Transform::Floats::Px(pmu); }
std::vector<double> pyc::transform::combined::Py(std::vector<std::vector<double>> pmu){ return Transform::Floats::Py(pmu); }
std::vector<double> pyc::transform::combined::Pz(std::vector<std::vector<double>> pmu){ return Transform::Floats::Pz(pmu); }
std::vector<std::vector<double>> pyc::transform::combined::PxPyPz(std::vector<std::vector<double>> pmu){ return Transform::Floats::PxPyPz(pmu); }
std::vector<std::vector<double>> pyc::transform::combined::PxPyPzE(std::vector<std::vector<double>> pmu){ return Transform::Floats::PxPyPzE(pmu); }

std::vector<torch::Tensor> pyc::nusol::polar::combined::Nu(
        std::vector<std::vector<double>> pmu_b, std::vector<std::vector<double>> pmu_mu,
        std::vector<std::vector<double>> met_phi, std::vector<std::vector<double>> masses,
        std::vector<std::vector<double>> sigma, const double null)
{
    std::map<std::string, torch::Tensor> out; 
    out = NuSol::Floats::Polar::Nu(pmu_b, pmu_mu, met_phi, masses, sigma, null); 
    return {out["NuVec"], out["chi2"]}; 
}

std::vector<torch::Tensor> pyc::nusol::polar::combined::NuNu(
        std::vector<std::vector<double>> pmu_b1, std::vector<std::vector<double>> pmu_b2, 
        std::vector<std::vector<double>> pmu_mu1, std::vector<std::vector<double>> pmu_mu2,
        std::vector<std::vector<double>> met_phi, 
        std::vector<std::vector<double>> masses, const double null)
{
    std::map<std::string, torch::Tensor> out; 
    out = NuSol::Floats::Polar::NuNu(pmu_b1, pmu_b2, pmu_mu1, pmu_mu2, met_phi, masses, null); 
    return { 
        out["NuVec_1"] , out["NuVec_2"], out["diagonal"], out["n_"],     
        out["H_perp_1"], out["H_perp_2"], out["NoSols"]
    }; 
}

std::vector<torch::Tensor> pyc::nusol::cartesian::combined::Nu(
        std::vector<std::vector<double>> pmc_b, std::vector<std::vector<double>> pmc_mu,
        std::vector<std::vector<double>> met_xy, 
        std::vector<std::vector<double>> masses,
        std::vector<std::vector<double>> sigma, const double null)
{
    std::map<std::string, torch::Tensor> out; 
    out = NuSol::Floats::Cartesian::Nu(pmc_b, pmc_mu, met_xy, masses, sigma, null); 
    return {out["NuVec"], out["chi2"]}; 
}

std::vector<torch::Tensor> pyc::nusol::cartesian::combined::NuNu(
        std::vector<std::vector<double>> pmc_b1, std::vector<std::vector<double>> pmc_b2, 
        std::vector<std::vector<double>> pmc_mu1, std::vector<std::vector<double>> pmc_mu2,
        std::vector<std::vector<double>> met_xy, 
        std::vector<std::vector<double>> masses, const double null)
{
    std::map<std::string, torch::Tensor> out; 
    out = NuSol::Floats::Cartesian::NuNu(pmc_b1, pmc_b2, pmc_mu1, pmc_mu2, met_xy, masses, null); 
    return { 
        out["NuVec_1"] , out["NuVec_2"], out["diagonal"], out["n_"],     
        out["H_perp_1"], out["H_perp_2"], out["NoSols"]
    }; 
}

TORCH_LIBRARY(pyc_float, m)
{
    // transformation classes for Tensors
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

    m.def("nusol_combined_polar_Nu",       &pyc::nusol::polar::combined::Nu);
    m.def("nusol_combined_polar_NuNu",     &pyc::nusol::polar::combined::NuNu);
    m.def("nusol_combined_cartesian_Nu",   &pyc::nusol::cartesian::combined::Nu);
    m.def("nusol_combined_cartesian_NuNu", &pyc::nusol::cartesian::combined::NuNu);
}
