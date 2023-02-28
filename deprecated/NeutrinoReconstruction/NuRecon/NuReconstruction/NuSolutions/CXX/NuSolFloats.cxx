#include "../Headers/NuSolFloats.h"
#include "../Headers/NuSolTensors.h"
#include "../../Physics/Floats/Headers/PhysicsFloats.h"

torch::Tensor NuSolutionFloats::x0Polar(double LPt, double LEta, double LPhi, double LE, 
		double MassH, double MassL, std::string device)
{
	return -(PhysicsFloats::ToTensor(MassH, device).pow(2) 
			- PhysicsFloats::ToTensor(MassL, device).pow(2) 
			- PhysicsFloats::Mass2Polar(LPt, LEta, LPhi, LE, device)
		)/(2*PhysicsFloats::ToTensor(LE, device)); 
}

torch::Tensor NuSolutionFloats::x0Cartesian(double LPx, double LPy, double LPz, double LE, 
		double MassH, double MassL, std::string device)
{
	return -(PhysicsFloats::ToTensor(MassH, device).pow(2) 
			- PhysicsFloats::ToTensor(MassL, device).pow(2) 
			- PhysicsFloats::Mass2Cartesian(LPx, LPy, LPz, LE, device)
		)/(2*PhysicsFloats::ToTensor(LE, device)); 
}

torch::Tensor NuSolutionFloats::SxPolar(
		double bPt, double bEta, double bPhi, double bE, 
		double muPt, double muEta, double muPhi, double muE, 
		double mW, double mNu, std::string device)
{
	torch::Tensor _b = PhysicsFloats::ToPxPyPzE(bPt, bEta, bPhi, bE, device); 
	torch::Tensor _mu = PhysicsFloats::ToPxPyPzE(muPt, muEta, muPhi, muE, device); 

	return NuSolutionTensors::SxCartesian(_b, _mu, 
			PhysicsFloats::ToTensor(mW, device), 
			PhysicsFloats::ToTensor(mNu, device)); 
}

torch::Tensor NuSolutionFloats::SyPolar(
		double bPt, double bEta, double bPhi, double bE, 
		double muPt, double muEta, double muPhi, double muE, 
		double mTop, double mW, double mNu, std::string device)
{
	torch::Tensor _b = PhysicsFloats::ToPxPyPzE(bPt, bEta, bPhi, bE, device); 
	torch::Tensor _mu = PhysicsFloats::ToPxPyPzE(muPt, muEta, muPhi, muE, device); 

	torch::Tensor _mTop = PhysicsFloats::ToTensor(mTop, device); 
	torch::Tensor _mW = PhysicsFloats::ToTensor(mW, device); 
	torch::Tensor _mNu = PhysicsFloats::ToTensor(mNu, device); 

	torch::Tensor Sx = NuSolutionTensors::SxCartesian(_b, _mu, _mW, _mNu); 
	return NuSolutionTensors::SyCartesian(_b, _mu, _mTop, _mW, Sx); 
}

torch::Tensor NuSolutionFloats::Eps2Cartesian(double mu_px, double mu_py, double mu_pz, double mu_e, double mW, double mNu, std::string device)
{
	torch::Tensor _mu = PhysicsFloats::ToTensor(mu_px, mu_py, mu_pz, mu_e, device);
	return NuSolutionTensors::Eps2Cartesian(PhysicsFloats::ToTensor(mW, device), PhysicsFloats::ToTensor(mNu, device), _mu); 
}

torch::Tensor NuSolutionFloats::Eps2Polar(double mu_pt, double mu_eta, double mu_phi, double mu_e, double mW, double mNu, std::string device)
{
	torch::Tensor _mu = PhysicsFloats::ToPxPyPzE(mu_pt, mu_eta, mu_phi, mu_e, device); 
	return NuSolutionTensors::Eps2Cartesian(PhysicsFloats::ToTensor(mW, device), PhysicsFloats::ToTensor(mNu, device), _mu); 
}

torch::Tensor NuSolutionFloats::wCartesian(double b_px, double b_py, double b_pz, double b_e, 
			double mu_px, double mu_py, double mu_pz, double mu_e, int factor, std::string device)
{
	torch::Tensor _mu = PhysicsFloats::ToTensor(mu_px, mu_py, mu_pz, mu_e, device);
	torch::Tensor _b = PhysicsFloats::ToTensor(b_px, b_py, b_pz, b_e, device);
	return NuSolutionTensors::wCartesian(_b, _mu, factor); 
}

torch::Tensor NuSolutionFloats::wPolar(double b_pt, double b_eta, double b_phi, double b_e, 
			double mu_pt, double mu_eta, double mu_phi, double mu_e, int factor, std::string device)
{
	torch::Tensor _mu = PhysicsFloats::ToPxPyPzE(b_pt, b_eta, b_phi, b_e, device); 
	torch::Tensor _b = PhysicsFloats::ToPxPyPzE(mu_pt, mu_eta, mu_phi, mu_e, device); 
	return NuSolutionTensors::wCartesian(_b, _mu, factor);
}

torch::Tensor NuSolutionFloats::Omega2Cartesian(double b_px, double b_py, double b_pz, double b_e, 
			double mu_px, double mu_py, double mu_pz, double mu_e, std::string device)
{
	torch::Tensor _mu = PhysicsFloats::ToTensor(mu_px, mu_py, mu_pz, mu_e, device);
	torch::Tensor _b = PhysicsFloats::ToTensor(b_px, b_py, b_pz, b_e, device);

	return NuSolutionTensors::Omega2Cartesian(_b, _mu); 
}

torch::Tensor NuSolutionFloats::Omega2Polar(double b_pt, double b_eta, double b_phi, double b_e, 
			double mu_pt, double mu_eta, double mu_phi, double mu_e, std::string device)
{
	torch::Tensor _mu = PhysicsFloats::ToPxPyPzE(b_pt, b_eta, b_phi, b_e, device); 
	torch::Tensor _b = PhysicsFloats::ToPxPyPzE(mu_pt, mu_eta, mu_phi, mu_e, device); 
	return NuSolutionTensors::Omega2Cartesian(_b, _mu);
}

torch::Tensor NuSolutionFloats::AnalyticalSolutionsCartesian(double b_px, double b_py, double b_pz, double b_e, 
		double mu_px, double mu_py, double mu_pz, double mu_e, 
		double massTop, double massW, double massNu, std::string device)
{
	return NuSolutionTensors::AnalyticalSolutionsCartesian(
			PhysicsFloats::ToTensor(b_px, b_py, b_pz, b_e, device), 
			PhysicsFloats::ToTensor(mu_px, mu_py, mu_pz, mu_e, device), 
			PhysicsFloats::ToTensor(massTop, device), 
			PhysicsFloats::ToTensor(massW, device), 
			PhysicsFloats::ToTensor(massNu, device));
}

torch::Tensor NuSolutionFloats::AnalyticalSolutionsPolar(double b_pt, double b_eta, double b_phi, double b_e, 
		double mu_pt, double mu_eta, double mu_phi, double mu_e, 
		double massTop, double massW, double massNu, std::string device)
{
	return NuSolutionTensors::AnalyticalSolutionsCartesian(
			PhysicsFloats::ToPxPyPzE(b_pt, b_eta, b_phi, b_e, device), 
			PhysicsFloats::ToPxPyPzE(mu_pt, mu_eta, mu_phi, mu_e, device), 
			PhysicsFloats::ToTensor(massTop, device), 
			PhysicsFloats::ToTensor(massW, device), 
			PhysicsFloats::ToTensor(massNu, device));
}
