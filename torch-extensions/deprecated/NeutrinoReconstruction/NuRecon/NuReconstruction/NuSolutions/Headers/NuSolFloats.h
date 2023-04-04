#ifndef H_NUSOL_FLOATS
#define H_NUSOL_FLOATS

#include <torch/extension.h>
#include <iostream>

namespace NuSolutionFloats
{
	torch::Tensor x0Polar(double LPt, double LEta, double LPhi, double LE, double MassH, double MassL, std::string device); 
	torch::Tensor x0Cartesian(double LPx, double LPy, double LPz, double LE, double MassH, double MassL, std::string device); 
	
	torch::Tensor SxPolar(double bPt, double bEta, double bPhi, double bE, 
			double muPt, double muEta, double muPhi, double muE, 
			double mW, double mNu, std::string device);

	torch::Tensor SyPolar(double bPt, double bEta, double bPhi, double bE, 
			double muPt, double muEta, double muPhi, double muE, 
			double mTop, double mW, double mNu, std::string device);

	torch::Tensor Eps2Cartesian(double mu_px, double mu_py, double mu_pz, double mu_e, 
			double mW, double mNu,std::string device);
	torch::Tensor Eps2Polar(double mu_pt, double mu_eta, double mu_phi, double mu_e, 
			double mW, double mNu, std::string device);

	torch::Tensor wCartesian(double b_px, double b_py, double b_pz, double b_e, 
			double mu_px, double mu_py, double mu_pz, double mu_e, int factor, std::string device); 
	torch::Tensor wPolar(double b_pt, double b_eta, double b_phi, double b_e, 
			double mu_pt, double mu_eta, double mu_phi, double mu_e, int factor, std::string device);

	torch::Tensor Omega2Cartesian(double b_px, double b_py, double b_pz, double b_e, 
			double mu_px, double mu_py, double mu_pz, double mu_e, std::string device);
	torch::Tensor Omega2Polar(double b_pt, double b_eta, double b_phi, double b_e, 
			double mu_pt, double mu_eta, double mu_phi, double mu_e, std::string device);

	torch::Tensor AnalyticalSolutionsCartesian(double b_px, double b_py, double b_pz, double b_e, 
			double mu_px, double mu_py, double mu_pz, double mu_e, 
			double massTop, double massW, double massNu, std::string device);
	torch::Tensor AnalyticalSolutionsPolar(double b_pt, double b_eta, double b_phi, double b_e, 
			double mu_pt, double mu_eta, double mu_phi, double mu_e, 
			double massTop, double massW, double massNu, std::string device);
}
#endif
