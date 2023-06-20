#ifndef H_TRANSFORM_TOPOLAR_F
#define H_TRANSFORM_TOPOLAR_F
#include <iostream>
#include <cmath>
#include <vector>

namespace TransformFloats
{
	double PT(double px, double py);
	double Phi(double px, double py);	
	double Eta(double px, double py, double pz); 
	double _Eta(double pt, double pz); 
	std::vector<double> PtEtaPhi(double px, double py, double pz);
}
#endif
