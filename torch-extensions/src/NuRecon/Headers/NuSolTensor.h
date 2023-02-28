#ifndef H_NUSOL_TENSOR
#define H_NUSOL_TENSOR

#include <torch/extension.h>
#include "../../Physics/Headers/Tensors.h"
#include "../../Transform/Headers/ToCartesianTensors.h"
#include "../../Transform/Headers/ToPolarTensors.h"
#include "../../Operators/Headers/Tensors.h"

namespace NuSolTensors
{
	torch::Tensor x0(torch::Tensor _pe, torch::Tensor _pm2, torch::Tensor mH2, torch::Tensor mL2); 
	torch::Tensor _UnitCircle(torch::Tensor x, std::vector<int> diag); 
	torch::Tensor UnitCircle(torch::Tensor x);
	torch::Tensor Derivative(torch::Tensor x); 
	torch::Tensor V0(torch::Tensor metx, torch::Tensor mety); 
	torch::Tensor Cofactors(torch::Tensor Matrix, int i, int j);
	std::vector<torch::Tensor> _MetXY(torch::Tensor met, torch::Tensor phi); 
	std::vector<torch::Tensor> _Format(torch::Tensor t, int dim); 
	std::vector<torch::Tensor> _Format(std::vector<std::vector<double>> inpt); 
	std::vector<torch::Tensor> _Format1D(std::vector<torch::Tensor> inpt); 
	torch::Tensor _TransferToTensor(std::vector<double> inpt); 
	void _FixEnergyTensor(std::vector<torch::Tensor>* v1, std::vector<torch::Tensor>* v2); 

	torch::Tensor H_Matrix(
			torch::Tensor Sols_, std::vector<torch::Tensor> b_C, 
			torch::Tensor mu_phi, torch::Tensor mu_pz, torch::Tensor mu_P); 

	torch::Tensor Solutions(
		std::vector<torch::Tensor> b_C, std::vector<torch::Tensor> mu_C, 
		torch::Tensor b_e, torch::Tensor mu_e,
		torch::Tensor massT2, torch::Tensor massW2, torch::Tensor massNu2); 
	
	torch::Tensor Solutions(
			torch::Tensor b, torch::Tensor mu, 
			torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu);

	torch::Tensor HorizontalVertical(torch::Tensor G);
	torch::Tensor Parallel(torch::Tensor G); 
	torch::Tensor Intersecting(torch::Tensor G, torch::Tensor g22); 
	std::vector<torch::Tensor> Intersection(torch::Tensor A, torch::Tensor B, double cutoff); 
	
}

namespace SingleNuTensor
{
	torch::Tensor Sigma2(torch::Tensor Sxx, torch::Tensor Sxy, torch::Tensor Syx, torch::Tensor Syy); 
	std::vector<torch::Tensor> Nu(
		std::vector<torch::Tensor> b_P, std::vector<torch::Tensor> mu_P, 
		std::vector<torch::Tensor> b_C, std::vector<torch::Tensor> mu_C, 
		torch::Tensor met_x, torch::Tensor met_y, 
		torch::Tensor Sxx, torch::Tensor Sxy, torch::Tensor Syx, torch::Tensor Syy, 
		torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff);
}

namespace NuTensor
{
	std::vector<torch::Tensor> PtEtaPhiE(
			torch::Tensor b, torch::Tensor mu, torch::Tensor met, torch::Tensor phi, 
			torch::Tensor Sxx, torch::Tensor Sxy, torch::Tensor Syx, torch::Tensor Syy, 
			torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff); 

	std::vector<torch::Tensor> PxPyPzE(
			torch::Tensor b, torch::Tensor mu, torch::Tensor met_x, torch::Tensor met_y, 
			torch::Tensor Sxx, torch::Tensor Sxy, torch::Tensor Syx, torch::Tensor Syy, 
			torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff); 
	
	std::vector<torch::Tensor> PtEtaPhiE_Double(
			double b_pt, double b_eta, double b_phi, double b_e, 
			double mu_pt, double mu_eta, double mu_phi, double mu_e, 
			double met, double phi,
			double Sxx, double Sxy, double Syx, double Syy, 
			double mT, double mW, double mNu, double cutoff); 
	
	std::vector<torch::Tensor> PxPyPzE_Double(
			double b_px, double b_py, double b_pz, double b_e, 
			double mu_px, double mu_py, double mu_pz, double mu_e, 
			double met_x, double met_y,
			double Sxx, double Sxy, double Syx, double Syy, 
			double mT, double mW, double mNu, double cutoff); 
	
	std::vector<torch::Tensor> PtEtaPhiE_DoubleList(
			std::vector<std::vector<double>> b, std::vector<std::vector<double>> mu, 
			std::vector<std::vector<double>> met, std::vector<std::vector<double>> S, 
			std::vector<std::vector<double>> Mass, double cutoff); 
	
	std::vector<torch::Tensor> PxPyPzE_DoubleList(
			std::vector<std::vector<double>> b, std::vector<std::vector<double>> mu, 
			std::vector<std::vector<double>> met, std::vector<std::vector<double>> S, 
			std::vector<std::vector<double>> Mass, double cutoff); 
	
}

namespace DoubleNuTensor 
{
	torch::Tensor N(torch::Tensor H); 
	torch::Tensor H_Perp(torch::Tensor H); 
	std::vector<torch::Tensor> Residuals(
			torch::Tensor H_perp, torch::Tensor H__perp, 
			torch::Tensor metx, torch::Tensor mety, torch::Tensor resid); 

	std::vector<torch::Tensor> NuNu(
			std::vector<torch::Tensor> b_P, std::vector<torch::Tensor> b__P, 
			std::vector<torch::Tensor> mu_P, std::vector<torch::Tensor> mu__P, 
			std::vector<torch::Tensor> b_C, std::vector<torch::Tensor> b__C, 
			std::vector<torch::Tensor> mu_C, std::vector<torch::Tensor> mu__C, 
			torch::Tensor met_x, torch::Tensor met_y, 
			torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff); 
}


namespace NuNuTensor
{
	std::vector<torch::Tensor> PtEtaPhiE(
			torch::Tensor b, torch::Tensor b_, torch::Tensor mu, torch::Tensor mu_,
			torch::Tensor met, torch::Tensor phi, 
			torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff);

	std::vector<torch::Tensor> PxPyPzE(
			torch::Tensor b, torch::Tensor b_, torch::Tensor mu, torch::Tensor mu_,
			torch::Tensor met_x, torch::Tensor met_y, 
			torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff); 
	
	std::vector<torch::Tensor> PtEtaPhiE_Double(
			double b_pt, double b_eta, double b_phi, double b_e, 
			double b__pt, double b__eta, double b__phi, double b__e, 
			double mu_pt, double mu_eta, double mu_phi, double mu_e, 
			double mu__pt, double mu__eta, double mu__phi, double mu__e, 
			double met, double phi,
			double mT, double mW, double mNu, double cutoff); 

	std::vector<torch::Tensor> PxPyPzE_Double(
			double b_px, double b_py, double b_pz, double b_e, 
			double b__px, double b__py, double b__pz, double b__e, 
			double mu_px, double mu_py, double mu_pz, double mu_e, 
			double mu__px, double mu__py, double mu__pz, double mu__e, 
			double met_x, double met_y,
			double mT, double mW, double mNu, double cutoff); 

	std::vector<torch::Tensor> PtEtaPhiE_DoubleList(
			std::vector<std::vector<double>> b, std::vector<std::vector<double>> b_, 
			std::vector<std::vector<double>> mu, std::vector<std::vector<double>> mu_, 
			std::vector<std::vector<double>> met, std::vector<std::vector<double>> Mass, double cutoff); 

	std::vector<torch::Tensor> PxPyPzE_DoubleList(
			std::vector<std::vector<double>> b, std::vector<std::vector<double>> b_, 
			std::vector<std::vector<double>> mu, std::vector<std::vector<double>> mu_, 
			std::vector<std::vector<double>> met, std::vector<std::vector<double>> Mass, double cutoff);
}


#endif 
