#ifndef H_TRANSFORM_TOCARTESIAN_F
#define H_TRANSFORM_TOCARTESIAN_F

#include <iostream>
#include <torch/extension.h>

namespace TransformFloats
{
	double Px(double pt, double phi); 
	double Py(double pt, double phi); 
	double Pz(double pt, double eta);
	std::vector<double> PxPyPz(double pt, double eta, double phi);
}

#endif 
