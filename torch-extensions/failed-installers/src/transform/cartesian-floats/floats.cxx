#include "floats.h" 

double TransformFloats::Px(double pt, double phi)
{
	return pt * std::cos(phi); 
}

double TransformFloats::Py(double pt, double phi)
{
	return pt * std::sin(phi); 
}

double TransformFloats::Pz(double pt, double eta)
{
	return pt * std::sinh(eta); 
}

std::vector<double> TransformFloats::PxPyPz(double pt, double eta, double phi)
{
	return {Px(pt, phi), Py(pt, phi), Pz(pt, eta)}; 
}
