#include "polar.h"

double Transform::Floats::Pt(double px, double py)
{
    return std::sqrt( std::pow(px, 2) + std::pow( py, 2) ); 
}

double Transform::Floats::Phi(double px, double py)
{
    return std::atan2(py, px); 
}

double Transform::Floats::PtEta(double pt, double pz)
{
    return std::asinh(pz / pt); 
}

double Transform::Floats::Eta(double px, double py, double pz)
{
    double pt = Transform::Floats::Pt(py, px); 
    return Transform::Floats::PtEta(pt, pz); 
}

std::vector<double> Transform::Floats::PtEtaPhi(double px, double py, double pz)
{
    double pt = Transform::Floats::Pt(px, py); 
    double eta = Transform::Floats::PtEta(pt, pz); 
    double phi = Transform::Floats::Phi(px, py); 
    return {pt, eta, phi}; 
}

std::vector<double> Transform::Floats::PtEtaPhiE(double px, double py, double pz, double e)
{
    double pt = Transform::Floats::Pt(px, py); 
    double eta = Transform::Floats::PtEta(pt, pz); 
    double phi = Transform::Floats::Phi(px, py); 
    return {pt, eta, phi, e}; 
}



std::vector<double> Transform::Floats::Pt(std::vector<std::vector<double>> pmc)
{
    std::vector<double> out; 
    for (unsigned int i(0); i < pmc.size(); ++i)
    {
        double pt = Transform::Floats::Pt(pmc[i][0], pmc[i][1]); 
        out.push_back(pt); 
    }
    return out; 
}

std::vector<double> Transform::Floats::Phi(std::vector<std::vector<double>> pmc)
{
    std::vector<double> out; 
    for (unsigned int i(0); i < pmc.size(); ++i)
    {
        double phi = Transform::Floats::Phi(pmc[i][0], pmc[i][1]); 
        out.push_back(phi); 
    }
    return out; 
}

std::vector<double> Transform::Floats::Eta(std::vector<std::vector<double>> pmc)
{
    std::vector<double> out; 
    for (unsigned int i(0); i < pmc.size(); ++i)
    {
        double eta = Transform::Floats::Eta(pmc[i][0], pmc[i][1], pmc[i][2]); 
        out.push_back(eta); 
    }
    return out; 
}

std::vector<std::vector<double>> Transform::Floats::PtEtaPhi(std::vector<std::vector<double>> pmc)
{
    std::vector<std::vector<double>> out; 
    for (unsigned int i(0); i < pmc.size(); ++i)
    {
        std::vector<double> pmu = Transform::Floats::PtEtaPhi(pmc[i][0], pmc[i][1], pmc[i][2]); 
        out.push_back(pmu); 
    }
    return out; 
}

std::vector<std::vector<double>> Transform::Floats::PtEtaPhiE(std::vector<std::vector<double>> pmc)
{
    std::vector<std::vector<double>> out; 
    for (unsigned int i(0); i < pmc.size(); ++i)
    {
        std::vector<double> pmu = Transform::Floats::PtEtaPhiE(pmc[i][0], pmc[i][1], pmc[i][2], pmc[i][3]); 
        out.push_back(pmu); 
    }
    return out; 
}
