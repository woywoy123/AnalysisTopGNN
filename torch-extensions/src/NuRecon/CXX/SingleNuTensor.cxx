#include "../Headers/NuSolTensor.h"

torch::Tensor SingleNuTensor::Sigma2(
		torch::Tensor Sxx, torch::Tensor Sxy, 
		torch::Tensor Syx, torch::Tensor Syy)
{
	torch::Tensor _S = torch::cat({Sxx, Sxy, Syx, Syy}, -1).view({-1, 2, 2});
	_S = torch::inverse(_S); 
	_S = torch::pad(_S, {0, 1, 0, 1}, "constant", 0);
	_S = torch::transpose(_S, 1, 2);
	return _S; 
}

std::vector<torch::Tensor> SingleNuTensor::Nu(
		std::vector<torch::Tensor> b_P, std::vector<torch::Tensor> mu_P, 
		std::vector<torch::Tensor> b_C, std::vector<torch::Tensor> mu_C, 
		torch::Tensor met_x, torch::Tensor met_y, 
		torch::Tensor Sxx, torch::Tensor Sxy, torch::Tensor Syx, torch::Tensor Syy, 
		torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff)
{

	NuSolTensors::_FixEnergyTensor(&b_C, &b_P); 
	NuSolTensors::_FixEnergyTensor(&mu_C, &mu_P); 

	// Some useful values
	torch::Tensor muP_ = PhysicsTensors::P(mu_C[0], mu_C[1], mu_C[2]); 
	torch::Tensor mu_e   = mu_P[3]; 
	torch::Tensor b_e = b_P[3]; 
	
	// Square the masses 
	torch::Tensor mT2 = mT.view({-1, 1}).pow(2); 
	torch::Tensor mW2 = mW.view({-1, 1}).pow(2); 
	torch::Tensor mNu2 = mNu.view({-1, 1}).pow(2);
	
	// Starting the algorithm 
	torch::Tensor sols_ = NuSolTensors::Solutions(b_C, mu_C, b_e, mu_e, mT2, mW2, mNu2);
	torch::Tensor H_ = NuSolTensors::H_Matrix(sols_, b_C, mu_P[2], mu_C[2], muP_); 

	// ---- Protection Against non-invertible Matrices ---- //
	torch::Tensor SkipEvent = torch::det(H_) != 0;
	H_ = H_.index({SkipEvent}); 
	met_x = met_x.index({SkipEvent}); 
	met_y = met_y.index({SkipEvent});
	if (H_.size(0) == 0){return {SkipEvent == false, SkipEvent == false, SkipEvent == false};}
	// ---------------------------------------------------- //
	
	// ---- MET uncertainity ---- //	
	Sxx = Sxx.index({SkipEvent}).view({-1, 1}); 
	Sxy = Sxy.index({SkipEvent}).view({-1, 1}); 
	Syx = Syx.index({SkipEvent}).view({-1, 1}); 
	Syy = Syy.index({SkipEvent}).view({-1, 1});
	torch::Tensor S2_ = SingleNuTensor::Sigma2(Sxx, Sxy, Syx, Syy); 
	// -------------------------- //

	torch::Tensor delta_ = NuSolTensors::V0(met_x, met_y) - H_; 
	torch::Tensor X_ = torch::matmul(torch::transpose(delta_, 1, 2), S2_); 
	X_ = torch::matmul(X_, delta_).view({-1, 3, 3});

	torch::Tensor M_ = X_.matmul(NuSolTensors::Derivative(X_)); 
	M_ = M_ + torch::transpose(M_, 1, 2); 	

	std::vector<torch::Tensor> _sol = NuSolTensors::Intersection(M_, NuSolTensors::UnitCircle(M_), cutoff); 

	torch::Tensor v = _sol[1].index({
			torch::indexing::Slice(), 0,
			torch::indexing::Slice(), 
			torch::indexing::Slice()}).view({-1, 3, 3});

	torch::Tensor v_ = _sol[1].index({
			torch::indexing::Slice(), 1, 
			torch::indexing::Slice(), 
			torch::indexing::Slice()}).view({-1, 3, 3});
	
	v = torch::cat({v, v_}, 1);
	torch::Tensor chi2 = (v.view({-1, 6, 1, 3}) * X_.view({-1, 1, 3, 3})).sum({-1}); 
	chi2 = (chi2.view({-1, 6, 3}) * v.view({-1, 6, 3})).sum(-1); 
	
	std::tuple<torch::Tensor, torch::Tensor> idx = chi2.sort(1, false);
	torch::Tensor diag = std::get<0>(idx); 
	torch::Tensor id = std::get<1>(idx); 
	
	// ------------ Sorted ------------- //
	torch::Tensor _t0 = torch::gather(v.index({
				torch::indexing::Slice(), 
				torch::indexing::Slice(), 
				0}), 1, id).view({-1, 6}); 

	torch::Tensor _t1 = torch::gather(v.index({
				torch::indexing::Slice(), 
				torch::indexing::Slice(), 
				1}), 1, id).view({-1, 6}); 

	torch::Tensor _t2 = torch::gather(v.index({
				torch::indexing::Slice(), 
				torch::indexing::Slice(), 
				2}), 1, id).view({-1, 6}); 

	torch::Tensor msk = (diag!=0.)*torch::arange(6, 0, -1, torch::TensorOptions().device(v.device())); 
	msk = torch::argmax(msk, -1, true); 
	_t0 = torch::gather(_t0, 1, msk).view({-1, 1, 1}); 
	_t1 = torch::gather(_t1, 1, msk).view({-1, 1, 1}); 
	_t2 = torch::gather(_t2, 1, msk).view({-1, 1, 1}); 
	_t2 = torch::cat({_t0, _t1, _t2}, -1); 
	_t2 = (H_*_t2).sum(-1); 

	return {SkipEvent == false, _t2, chi2, (H_.view({-1, 1, 3, 3})*v.view({-1, 6, 1, 3})).sum(-1)}; 
}

std::vector<torch::Tensor> NuTensor::PtEtaPhiE(
			torch::Tensor b, torch::Tensor mu, torch::Tensor met, torch::Tensor phi, 
			torch::Tensor Sxx, torch::Tensor Sxy, torch::Tensor Syx, torch::Tensor Syy, 
			torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff)
{
		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_P = NuSolTensors::_Format(b.view({-1, 4}), 4);
		std::vector<torch::Tensor> mu_P = NuSolTensors::_Format(mu.view({-1, 4}), 4); 
		
		// ---- Cartesian Version of Particles ---- //
		std::vector<torch::Tensor> b_C = NuSolTensors::_Format(TransformTensors::PxPyPz(b_P[0], b_P[1], b_P[2]), 3); 
		std::vector<torch::Tensor> mu_C = NuSolTensors::_Format(TransformTensors::PxPyPz(mu_P[0], mu_P[1], mu_P[2]), 3); 

		// ---- Cartesian Version of Event Met ---- //
		std::vector<torch::Tensor> _met = NuSolTensors::_MetXY(met, phi);

		// ---- Standardize Tensors ---- //
		std::vector<torch::Tensor> _S = NuSolTensors::_Format1D({Sxx, Sxy, Syx, Syy}); 
		std::vector<torch::Tensor> _m = NuSolTensors::_Format1D({mT, mW, mNu}); 

		return SingleNuTensor::Nu(b_P, mu_P, b_C, mu_C, _met[0], _met[1], _S[0], _S[1], _S[2], _S[3], _m[0], _m[1], _m[2], cutoff); 
}

std::vector<torch::Tensor> NuTensor::PxPyPzE(
		torch::Tensor b, torch::Tensor mu, torch::Tensor met_x, torch::Tensor met_y, 
		torch::Tensor Sxx, torch::Tensor Sxy, torch::Tensor Syx, torch::Tensor Syy, 
		torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff)
{

	// ---- Cartesian Version of Particles ---- //
	std::vector<torch::Tensor> b_C = NuSolTensors::_Format(b.view({-1, 4}), 4);
	std::vector<torch::Tensor> mu_C = NuSolTensors::_Format(mu.view({-1, 4}), 4); 
	
	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(b_C[0], b_C[1], b_C[2]), 3); 
	std::vector<torch::Tensor> mu_P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(mu_C[0], mu_C[1], mu_C[2]), 3); 

	// ---- Cartesian Version of Event Met ---- //
	std::vector<torch::Tensor> _met = NuSolTensors::_Format1D({met_x, met_y});

	// ---- Standardize Tensors ---- //
	std::vector<torch::Tensor> _S = NuSolTensors::_Format1D({Sxx, Sxy, Syx, Syy}); 
	std::vector<torch::Tensor> _m = NuSolTensors::_Format1D({mT, mW, mNu}); 

	return SingleNuTensor::Nu(b_P, mu_P, b_C, mu_C, _met[0], _met[1], _S[0], _S[1], _S[2], _S[3], _m[0], _m[1], _m[2], cutoff); 
}

std::vector<torch::Tensor> NuTensor::PtEtaPhiE_Double(
		double b_pt, double b_eta, double b_phi, double b_e, 
		double mu_pt, double mu_eta, double mu_phi, double mu_e, 
		double met, double phi,
		double Sxx, double Sxy, double Syx, double Syy, 
		double mT, double mW, double mNu, double cutoff)
{
	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_P = NuSolTensors::_Format({{b_pt, b_eta, b_phi, b_e}}); 
	std::vector<torch::Tensor> mu_P = NuSolTensors::_Format({{mu_pt, mu_eta, mu_phi, mu_e}});  
	
	// ---- Cartesian Version of Particles ---- //
	std::vector<torch::Tensor> b_C = NuSolTensors::_Format(TransformTensors::PxPyPz(b_P[0], b_P[1], b_P[2]), 3); 
	std::vector<torch::Tensor> mu_C = NuSolTensors::_Format(TransformTensors::PxPyPz(mu_P[0], mu_P[1], mu_P[2]), 3); 

	std::vector<torch::Tensor> _met = NuSolTensors::_Format({{met, phi}}); 
	_met = NuSolTensors::_MetXY(_met[0], _met[1]); 

	std::vector<torch::Tensor> _S = NuSolTensors::_Format({{Sxx, Sxy, Syx, Syy}}); 
	std::vector<torch::Tensor> _m = NuSolTensors::_Format({{mT, mW, mNu}});

	return SingleNuTensor::Nu(b_P, mu_P, b_C, mu_C, _met[0], _met[1], _S[0], _S[1], _S[2], _S[3], _m[0], _m[1], _m[2], cutoff); 
}

std::vector<torch::Tensor> NuTensor::PxPyPzE_Double(
		double b_px, double b_py, double b_pz, double b_e, 
		double mu_px, double mu_py, double mu_pz, double mu_e, 
		double met_x, double met_y,
		double Sxx, double Sxy, double Syx, double Syy, 
		double mT, double mW, double mNu, double cutoff)
{
	// ---- Cartesian Version of Particles ---- //
	std::vector<torch::Tensor> b_C = NuSolTensors::_Format({{b_px, b_py, b_pz, b_e}}); 
	std::vector<torch::Tensor> mu_C = NuSolTensors::_Format({{mu_px, mu_py, mu_pz, mu_e}});  

	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(b_C[0], b_C[1], b_C[2]), 3); 
	std::vector<torch::Tensor> mu_P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(mu_C[0], mu_C[1], mu_C[2]), 3); 

	std::vector<torch::Tensor> _met = NuSolTensors::_Format({{met_x, met_y}}); 
	std::vector<torch::Tensor> _S = NuSolTensors::_Format({{Sxx, Sxy, Syx, Syy}}); 
	std::vector<torch::Tensor> _m = NuSolTensors::_Format({{mT, mW, mNu}}); 

	return SingleNuTensor::Nu(b_P, mu_P, b_C, mu_C, _met[0], _met[1], _S[0], _S[1], _S[2], _S[3], _m[0], _m[1], _m[2], cutoff); 
}

std::vector<torch::Tensor> NuTensor::PtEtaPhiE_DoubleList(
		std::vector<std::vector<double>> b, std::vector<std::vector<double>> mu, 
		std::vector<std::vector<double>> met, std::vector<std::vector<double>> S, 
		std::vector<std::vector<double>> Mass, double cutoff)
{
	
	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_P = NuSolTensors::_Format(b); 
	std::vector<torch::Tensor> mu_P = NuSolTensors::_Format(mu); 

	// ---- Cartesian Version of Particles ---- //
	std::vector<torch::Tensor> b_C = NuSolTensors::_Format(TransformTensors::PxPyPz(b_P[0], b_P[1], b_P[2]), 3); 
	std::vector<torch::Tensor> mu_C = NuSolTensors::_Format(TransformTensors::PxPyPz(mu_P[0], mu_P[1], mu_P[2]), 3); 

	std::vector<torch::Tensor> _S = NuSolTensors::_Format(S); 
	std::vector<torch::Tensor> _m = NuSolTensors::_Format(Mass); 

	std::vector<torch::Tensor> _met = NuSolTensors::_Format(met); 
	_met = NuSolTensors::_MetXY(_met[0], _met[1]); 

	return SingleNuTensor::Nu(b_P, mu_P, b_C, mu_C, _met[0], _met[1], _S[0], _S[1], _S[2], _S[3], _m[0], _m[1], _m[2], cutoff); 
}

std::vector<torch::Tensor> NuTensor::PxPyPzE_DoubleList(
		std::vector<std::vector<double>> b, std::vector<std::vector<double>> mu, 
		std::vector<std::vector<double>> met, std::vector<std::vector<double>> S, 
		std::vector<std::vector<double>> Mass, double cutoff)
{
	// ---- Cartesian Version of Particles ---- //
	std::vector<torch::Tensor> b_C = NuSolTensors::_Format(b); 
	std::vector<torch::Tensor> mu_C = NuSolTensors::_Format(mu); 

	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(b_C[0], b_C[1], b_C[2]), 3); 
	std::vector<torch::Tensor> mu_P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(mu_C[0], mu_C[1], mu_C[2]), 3); 

	std::vector<torch::Tensor> _S = NuSolTensors::_Format(S); 
	std::vector<torch::Tensor> _m = NuSolTensors::_Format(Mass); 

	std::vector<torch::Tensor> _met = NuSolTensors::_Format(met); 
	return SingleNuTensor::Nu(b_P, mu_P, b_C, mu_C, _met[0], _met[1], _S[0], _S[1], _S[2], _S[3], _m[0], _m[1], _m[2], cutoff); 
}

