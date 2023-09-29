#ifndef H_TRANSFORM_FLOATS_CARTESIAN
#define H_TRANSFORM_FLOATS_CARTESIAN

#include <iostream>
#include <cmath>
#include <vector>

namespace Transform
{
    namespace Floats
    {
        double Px(double pt, double phi); 
        double Py(double pt, double phi); 
        double Pz(double pt, double eta); 
        std::vector<double> PxPyPz(double pt, double eta, double phi); 
        std::vector<double> PxPyPzE(double pt, double eta, double phi, double e); 

        std::vector<double> Px(std::vector<std::vector<double>> pmu); 
        std::vector<double> Py(std::vector<std::vector<double>> pmu); 
        std::vector<double> Pz(std::vector<std::vector<double>> pmu); 
        std::vector<std::vector<double>> PxPyPz(std::vector<std::vector<double>> pmu); 
        std::vector<std::vector<double>> PxPyPzE(std::vector<std::vector<double>> pmu); 
    }
}

#endif
