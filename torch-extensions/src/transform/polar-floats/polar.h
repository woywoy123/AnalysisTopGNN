#ifndef H_TRANSFORM_FLOATS_POLAR
#define H_TRANSFORM_FLOATS_POLAR

#include <iostream>
#include <cmath>
#include <vector>

namespace Transform 
{
    namespace Floats
    {
        double Pt(double px, double py); 
        double Phi(double px, double py); 
        double PtEta(double pt, double pz); 
        double Eta(double px, double py, double pz); 
        std::vector<double> PtEtaPhi(double px, double py, double pz);
        std::vector<double> PtEtaPhiE(double px, double py, double pz, double e);

        std::vector<double> Pt(std::vector<std::vector<double>> pmc); 
        std::vector<double> Phi(std::vector<std::vector<double>> pmc); 
        std::vector<double> PtEta(std::vector<std::vector<double>> pmc); 
        std::vector<double> Eta(std::vector<std::vector<double>> pmc); 
        std::vector<std::vector<double>> PtEtaPhi(std::vector<std::vector<double>> pmc); 
        std::vector<std::vector<double>> PtEtaPhiE(std::vector<std::vector<double>> pmc); 
    }
}

#endif
