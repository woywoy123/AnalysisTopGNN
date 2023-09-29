#include "cartesian.h"

double Transform::Floats::Px(double pt, double phi)
{
    return pt*std::cos(phi); 
}

double Transform::Floats::Py(double pt, double phi)
{
    return pt*std::sin(phi); 
}

double Transform::Floats::Pz(double pt, double eta)
{
    return pt*std::sinh(eta); 
}

std::vector<double> Transform::Floats::PxPyPz(double pt, double eta, double phi)
{
    double px = Transform::Floats::Px(pt, phi); 
    double py = Transform::Floats::Py(pt, phi); 
    double pz = Transform::Floats::Pz(pt, eta); 
    return {px, py, pz}; 
}

std::vector<double> Transform::Floats::PxPyPzE(double pt, double eta, double phi, double e)
{
    double px = Transform::Floats::Px(pt, phi); 
    double py = Transform::Floats::Py(pt, phi); 
    double pz = Transform::Floats::Pz(pt, eta); 
    return {px, py, pz}; 
}


std::vector<double> Transform::Floats::Px(std::vector<std::vector<double>> pmu)
{
    std::vector<double> out; 
    for (unsigned int i(0); i < pmu.size(); ++i)
    {
        double px = Transform::Floats::Px(pmu[i][0], pmu[i][2]); 
        out.push_back(px); 
    }
    return out; 
}

std::vector<double> Transform::Floats::Py(std::vector<std::vector<double>> pmu)
{
    std::vector<double> out; 
    for (unsigned int i(0); i < pmu.size(); ++i)
    {
        double py = Transform::Floats::Py(pmu[i][0], pmu[i][2]); 
        out.push_back(py); 
    }
    return out; 
}

std::vector<double> Transform::Floats::Pz(std::vector<std::vector<double>> pmu)
{
    std::vector<double> out; 
    for (unsigned int i(0); i < pmu.size(); ++i)
    {
        double py = Transform::Floats::Pz(pmu[i][0], pmu[i][1]); 
        out.push_back(py); 
    }
    return out; 
}

std::vector<std::vector<double>> Transform::Floats::PxPyPz(std::vector<std::vector<double>> pmu)
{
    std::vector<std::vector<double>> out; 
    for (unsigned int i(0); i < pmu.size(); ++i)
    {
        std::vector<double> pmc = Transform::Floats::PxPyPz(pmu[i][0], pmu[i][1], pmu[i][2]); 
        out.push_back(pmc); 
    }
    return out; 
}

std::vector<std::vector<double>> Transform::Floats::PxPyPzE(std::vector<std::vector<double>> pmu)
{
    std::vector<std::vector<double>> out; 
    for (unsigned int i(0); i < pmu.size(); ++i)
    {
        std::vector<double> pmc = Transform::Floats::PxPyPzE(pmu[i][0], pmu[i][1], pmu[i][2], pmu[i][3]); 
        out.push_back(pmc); 
    }
    return out; 
}

