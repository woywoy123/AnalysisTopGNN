#include "../Headers/NuSolTensor.h"

torch::Tensor DoubleNuTensor::H_Perp(torch::Tensor H)
{
	torch::Tensor H_ = torch::clone(H); 
	H_.index_put_({torch::indexing::Slice(), 2, torch::indexing::Slice()}, 0); 
	H_.index_put_({torch::indexing::Slice(), 2, 2}, 1);
	return H_; 
}

torch::Tensor DoubleNuTensor::N(torch::Tensor H)
{
	torch::Tensor H_ = DoubleNuTensor::H_Perp(H); 
	H_ = torch::inverse(H_); 
	torch::Tensor H_T = torch::transpose(H_, 1, 2); 
	H_T = torch::matmul(H_T, NuSolTensors::UnitCircle(H_)); 
	return torch::matmul(H_T, H_); 
}

std::vector<torch::Tensor> DoubleNuTensor::Residuals(
					torch::Tensor H_perp, torch::Tensor H__perp, 
					torch::Tensor met_x, torch::Tensor met_y, torch::Tensor resid)
{
	pybind11::gil_scoped_release no_gil; 
	H_perp = H_perp.index({resid}).view({-1, 3, 3}); 
	H__perp = H__perp.index({resid}).view({-1, 3, 3}); 
	met_x = met_x.index({resid}).view({-1, 1}); 
	met_y = met_y.index({resid}).view({-1, 1});

	if (met_x.size(0) == 0){ return {}; }
	
	torch::Tensor t1 = torch::ones_like(met_y);
	torch::Tensor MET = torch::cat({met_x, met_y, t1}, -1); 	
	
	torch::Tensor t0 = torch::zeros_like(met_x); 
	torch::Tensor pi = torch::cos(t0)*2; 
	t0 = torch::cat({t0, t0}, -1); 
	
	torch::Tensor t = torch::zeros({met_x.size(0), 1}, torch::TensorOptions().dtype(t0.dtype()).device(t0.device()).requires_grad(true)); 
	torch::Tensor t_ = torch::zeros({met_x.size(0), 1}, torch::TensorOptions().dtype(t0.dtype()).device(t0.device()).requires_grad(true));
	
	torch::optim::AdamOptions set(0.5); 
	torch::optim::Adam opti({t, t_}, set); 
	
	torch::Tensor nu; 
	torch::Tensor nu_;
	torch::Tensor nus; 
	for (int i(0); i < 100; ++i)
	{
		nu = (H_perp*(torch::cat({torch::cos(pi*t), torch::sin(pi*t), t1}, -1).view({-1, 1, 3}))).sum(-1); 
		nu_ = (H__perp*(torch::cat({torch::cos(pi*t_), torch::sin(pi*t_), t1}, -1).view({-1, 1, 3}))).sum(-1);
		nus = (nu_ + nu - MET).index({torch::indexing::Slice(), torch::indexing::Slice(torch::indexing::None, 2)}).view({-1, 2}); 
		
		opti.zero_grad(); 
		torch::Tensor loss = torch::nn::functional::mse_loss(nus, t0); 
		loss.backward(); 
		opti.step();
	}

	nu = (H_perp*(torch::cat({torch::cos(pi*t), torch::sin(pi*t), t1}, -1).view({-1, 1, 3}))).sum(-1).detach().clone().view({-1, 1, 3}); 
	nu_ = (H__perp*(torch::cat({torch::cos(pi*t_), torch::sin(pi*t_), t1}, -1).view({-1, 1, 3}))).sum(-1).detach().clone().view({-1, 1, 3});
	t0 = torch::zeros_like(nu);
	nu = torch::cat({nu, t0, t0, t0, t0, t0}, -2).view({-1, 6, 3}); 
	nu_ = torch::cat({nu_, t0, t0, t0, t0, t0}, -2).view({-1, 6, 3}); 
	return {nu, nu_};  
}

std::vector<torch::Tensor> DoubleNuTensor::NuNu(
		std::vector<torch::Tensor> b_P, std::vector<torch::Tensor> b__P, std::vector<torch::Tensor> mu_P, std::vector<torch::Tensor> mu__P, 
		std::vector<torch::Tensor> b_C, std::vector<torch::Tensor> b__C, std::vector<torch::Tensor> mu_C, std::vector<torch::Tensor> mu__C, 
		torch::Tensor met_x, torch::Tensor met_y, 
		torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff)
{
	// ---- Format Input Vectors ---- // 
	NuSolTensors::_FixEnergyTensor(&b_C, &b_P); 
	NuSolTensors::_FixEnergyTensor(&mu_C, &mu_P); 
	NuSolTensors::_FixEnergyTensor(&b__C, &b__P); 
	NuSolTensors::_FixEnergyTensor(&mu__C, &mu__P); 
	
	// ---- Precalculate the Mass Squared ---- //
	torch::Tensor mT2 = mT.view({-1, 1}).pow(2); 
	torch::Tensor mW2 = mW.view({-1, 1}).pow(2); 
	torch::Tensor mNu2 = mNu.view({-1, 1}).pow(2);
	
	// ---- Starting the algorithm ----- //
	torch::Tensor sols_ = NuSolTensors::Solutions(b_C, mu_C, b_P[3], mu_P[3], mT2, mW2, mNu2);
	torch::Tensor sols__ = NuSolTensors::Solutions(b__C, mu__C, b__P[3], mu__P[3], mT2, mW2, mNu2);
	
	torch::Tensor H_ = NuSolTensors::H_Matrix(sols_, b_C, mu_P[2], mu_C[2], PhysicsTensors::P(mu_C[0], mu_C[1], mu_C[2])); 
	torch::Tensor H__ = NuSolTensors::H_Matrix(sols__, b__C, mu__P[2], mu__C[2], PhysicsTensors::P(mu__C[0], mu__C[1], mu__C[2]));

	// ---- Protection Against non-invertible Matrices ---- //
	torch::Tensor SkipEvent = (torch::det(H_) != 0)*(torch::det(H__) != 0);
	H_ = H_.index({SkipEvent}); 
	H__ = H__.index({SkipEvent}); 
	met_x = met_x.index({SkipEvent}); 
	met_y = met_y.index({SkipEvent});
	if (H_.size(0) == 0){return {SkipEvent == false, SkipEvent == false, SkipEvent == false};}
	// ---------------------------------------------------- //
	torch::Tensor H_perp = DoubleNuTensor::H_Perp(H_); 
	torch::Tensor H__perp = DoubleNuTensor::H_Perp(H__); 

	torch::Tensor N_ = DoubleNuTensor::N(H_); 
	torch::Tensor N__ = DoubleNuTensor::N(H__); 

	torch::Tensor S_ = NuSolTensors::V0(met_x, met_y) - NuSolTensors::UnitCircle(met_y); 
	torch::Tensor n_ = torch::matmul(torch::matmul(S_.transpose(1, 2), N__), S_); 

	// ----- Launching the Intersection code ------- //
	std::vector<torch::Tensor> _sol = NuSolTensors::Intersection(N_, n_, cutoff);

	torch::Tensor v = _sol[1].index({
			torch::indexing::Slice(), 0,
			torch::indexing::Slice(), 
			torch::indexing::Slice()}).view({-1, 3, 3});

	torch::Tensor v_ = _sol[1].index({
			torch::indexing::Slice(), 1, 
			torch::indexing::Slice(), 
			torch::indexing::Slice()}).view({-1, 3, 3});
	

	torch::Tensor resid = torch::sum(torch::sum(v + v_, -1), -1) == 0.0;
	std::vector<torch::Tensor> lstsq = DoubleNuTensor::Residuals(H_perp, H__perp, met_x, met_y, resid); 
	v = torch::cat({v, v_}, 1);
	v_ = torch::sum(S_.view({-1, 1, 3, 3})*v.view({-1, 6, 1, 3}), -1);
	if (lstsq.size() != 0)
	{
		v.index_put_({resid}, lstsq[0]); 
		v_.index_put_({resid}, lstsq[1]); 
	}

	// ------ Neutrino Solutions -------- //
	torch::Tensor K = torch::matmul(H_, torch::inverse( H_perp )); 
	torch::Tensor K_ = torch::matmul(H__, torch::inverse( H__perp )); 
	
	K = (K.view({-1, 1, 3, 3}) * v.view({-1, 6, 1, 3})).sum(-1); 
	K_ = (K_.view({-1, 1, 3, 3}) * v_.view({-1, 6, 1, 3})).sum(-1); 
	
	K = torch::nan_to_num(K, 0, 0); 
	K_ = torch::nan_to_num(K_, 0, 0); 

	return {SkipEvent == false, K, K_, v, v_, n_, _sol[2], _sol[3]}; 
}

std::vector<torch::Tensor> NuNuTensor::PtEtaPhiE(
		torch::Tensor b, torch::Tensor b_, torch::Tensor mu, torch::Tensor mu_,
		torch::Tensor met, torch::Tensor phi, 
		torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff)
{
	
	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_P = NuSolTensors::_Format(b.view({-1, 4}), 4);
	std::vector<torch::Tensor> b__P = NuSolTensors::_Format(b_.view({-1, 4}), 4);
	std::vector<torch::Tensor> mu_P = NuSolTensors::_Format(mu.view({-1, 4}), 4); 
	std::vector<torch::Tensor> mu__P = NuSolTensors::_Format(mu_.view({-1, 4}), 4); 
	
	// ---- Cartesian Version of Particles ---- //
	std::vector<torch::Tensor> b_C = NuSolTensors::_Format(TransformTensors::PxPyPz(b_P[0], b_P[1], b_P[2]), 3); 
	std::vector<torch::Tensor> b__C = NuSolTensors::_Format(TransformTensors::PxPyPz(b__P[0], b__P[1], b__P[2]), 3); 
	std::vector<torch::Tensor> mu_C = NuSolTensors::_Format(TransformTensors::PxPyPz(mu_P[0], mu_P[1], mu_P[2]), 3); 
	std::vector<torch::Tensor> mu__C = NuSolTensors::_Format(TransformTensors::PxPyPz(mu__P[0], mu__P[1], mu__P[2]), 3);

	// ---- Cartesian Version of Event Met ---- //
	std::vector<torch::Tensor> _met = NuSolTensors::_MetXY(met, phi); 
	
	return DoubleNuTensor::NuNu(b_P, b__P, mu_P, mu__P, b_C, b__C, mu_C, mu__C, _met[0], _met[1], mT, mW, mNu, cutoff); 
}

std::vector<torch::Tensor> NuNuTensor::PxPyPzE(
		torch::Tensor b, torch::Tensor b_, torch::Tensor mu, torch::Tensor mu_,
		torch::Tensor met_x, torch::Tensor met_y, 
		torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff)
{

	// ---- Cartesian Version of Particles ---- //
	std::vector<torch::Tensor> b_C = NuSolTensors::_Format(b.view({-1, 4}), 4);
	std::vector<torch::Tensor> b__C = NuSolTensors::_Format(b_.view({-1, 4}), 4);
	std::vector<torch::Tensor> mu_C = NuSolTensors::_Format(mu.view({-1, 4}), 4); 
	std::vector<torch::Tensor> mu__C = NuSolTensors::_Format(mu_.view({-1, 4}), 4);

	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(b_C[0], b_C[1], b_C[2]), 3); 
	std::vector<torch::Tensor> b__P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(b__C[0], b__C[1], b__C[2]), 3); 
	std::vector<torch::Tensor> mu_P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(mu_C[0], mu_C[1], mu_C[2]), 3); 
	std::vector<torch::Tensor> mu__P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(mu__C[0], mu__C[1], mu__C[2]), 3);

	// ---- Standardize Tensors ---- //
	std::vector<torch::Tensor> _met = NuSolTensors::_Format1D({met_x, met_y});
	std::vector<torch::Tensor> _m = NuSolTensors::_Format1D({mT, mW, mNu}); 

	return DoubleNuTensor::NuNu(b_P, b__P, mu_P, mu__P, b_C, b__C, mu_C, mu__C, _met[0], _met[1], _m[0], _m[1], _m[2], cutoff);
}


std::vector<torch::Tensor> NuNuTensor::PtEtaPhiE_Double(
		double b_pt, double b_eta, double b_phi, double b_e, 
		double b__pt, double b__eta, double b__phi, double b__e, 
		double mu_pt, double mu_eta, double mu_phi, double mu_e, 
		double mu__pt, double mu__eta, double mu__phi, double mu__e, 
		double met, double phi,
		double mT, double mW, double mNu, double cutoff)
{
	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_P = NuSolTensors::_Format({{b_pt, b_eta, b_phi, b_e}});
	std::vector<torch::Tensor> b__P = NuSolTensors::_Format({{b__pt, b__eta, b__phi, b__e}});
	std::vector<torch::Tensor> mu_P = NuSolTensors::_Format({{mu_pt, mu_eta, mu_phi, mu_e}});
	std::vector<torch::Tensor> mu__P = NuSolTensors::_Format({{mu__pt, mu__eta, mu__phi, mu__e}});

	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_C = NuSolTensors::_Format(TransformTensors::PxPyPz(b_P[0], b_P[1], b_P[2]), 3); 
	std::vector<torch::Tensor> b__C = NuSolTensors::_Format(TransformTensors::PxPyPz(b__P[0], b__P[1], b__P[2]), 3); 
	std::vector<torch::Tensor> mu_C = NuSolTensors::_Format(TransformTensors::PxPyPz(mu_P[0], mu_P[1], mu_P[2]), 3); 
	std::vector<torch::Tensor> mu__C = NuSolTensors::_Format(TransformTensors::PxPyPz(mu__P[0], mu__P[1], mu__P[2]), 3);

	// ---- Make into Tensors ---- //
	std::vector<torch::Tensor> _m = NuSolTensors::_Format({{mT, mW, mNu}}); 
	std::vector<torch::Tensor> _met = NuSolTensors::_Format({{met, phi}});
	_met = NuSolTensors::_MetXY(_met[0], _met[1]); 
	
	return DoubleNuTensor::NuNu(b_P, b__P, mu_P, mu__P, b_C, b__C, mu_C, mu__C, _met[0], _met[1], _m[0], _m[1], _m[2], cutoff);
}

 std::vector<torch::Tensor> NuNuTensor::PxPyPzE_Double(
		double b_px, double b_py, double b_pz, double b_e, 
		double b__px, double b__py, double b__pz, double b__e, 
		double mu_px, double mu_py, double mu_pz, double mu_e, 
		double mu__px, double mu__py, double mu__pz, double mu__e, 
		double met_x, double met_y,
		double mT, double mW, double mNu, double cutoff)
{

	// ---- Cartesian Version of Particles ---- //
	std::vector<torch::Tensor> b_C = NuSolTensors::_Format({{b_px, b_py, b_pz, b_e}});
	std::vector<torch::Tensor> b__C = NuSolTensors::_Format({{b__px, b__py, b__pz, b__e}});
	std::vector<torch::Tensor> mu_C = NuSolTensors::_Format({{mu_px, mu_py, mu_pz, mu_e}});
	std::vector<torch::Tensor> mu__C = NuSolTensors::_Format({{mu__px, mu__py, mu__pz, mu__e}});

	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(b_C[0], b_C[1], b_C[2]), 3); 
	std::vector<torch::Tensor> b__P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(b__C[0], b__C[1], b__C[2]), 3); 
	std::vector<torch::Tensor> mu_P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(mu_C[0], mu_C[1], mu_C[2]), 3); 
	std::vector<torch::Tensor> mu__P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(mu__C[0], mu__C[1], mu__C[2]), 3);

	// ---- Make into Tensors ---- //
	std::vector<torch::Tensor> _met = NuSolTensors::_Format({{met_x, met_y}});
	std::vector<torch::Tensor> _m = NuSolTensors::_Format({{mT, mW, mNu}}); 
	
	return DoubleNuTensor::NuNu(b_P, b__P, mu_P, mu__P, b_C, b__C, mu_C, mu__C, _met[0], _met[1], _m[0], _m[1], _m[2], cutoff);
}

 std::vector<torch::Tensor> NuNuTensor::PtEtaPhiE_DoubleList(
		std::vector<std::vector<double>> b, std::vector<std::vector<double>> b_, 
		std::vector<std::vector<double>> mu, std::vector<std::vector<double>> mu_, 
		std::vector<std::vector<double>> met, std::vector<std::vector<double>> Mass, double cutoff)
{
	
	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_P = NuSolTensors::_Format(b);
	std::vector<torch::Tensor> b__P = NuSolTensors::_Format(b_);
	std::vector<torch::Tensor> mu_P = NuSolTensors::_Format(mu);
	std::vector<torch::Tensor> mu__P = NuSolTensors::_Format(mu_);

	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_C = NuSolTensors::_Format(TransformTensors::PxPyPz(b_P[0], b_P[1], b_P[2]), 3); 
	std::vector<torch::Tensor> b__C = NuSolTensors::_Format(TransformTensors::PxPyPz(b__P[0], b__P[1], b__P[2]), 3); 
	std::vector<torch::Tensor> mu_C = NuSolTensors::_Format(TransformTensors::PxPyPz(mu_P[0], mu_P[1], mu_P[2]), 3); 
	std::vector<torch::Tensor> mu__C = NuSolTensors::_Format(TransformTensors::PxPyPz(mu__P[0], mu__P[1], mu__P[2]), 3);

	// ---- Make into Tensors ---- //
	std::vector<torch::Tensor> _met = NuSolTensors::_Format(met);
	_met = NuSolTensors::_MetXY(_met[0], _met[1]); 
	std::vector<torch::Tensor> _m = NuSolTensors::_Format(Mass); 
	
	return DoubleNuTensor::NuNu(b_P, b__P, mu_P, mu__P, b_C, b__C, mu_C, mu__C, _met[0], _met[1], _m[0], _m[1], _m[2], cutoff);
}

 std::vector<torch::Tensor> NuNuTensor::PxPyPzE_DoubleList(
		std::vector<std::vector<double>> b, std::vector<std::vector<double>> b_, 
		std::vector<std::vector<double>> mu, std::vector<std::vector<double>> mu_, 
		std::vector<std::vector<double>> met, std::vector<std::vector<double>> Mass, double cutoff)
{
	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_C = NuSolTensors::_Format(b);
	std::vector<torch::Tensor> b__C = NuSolTensors::_Format(b_);
	std::vector<torch::Tensor> mu_C = NuSolTensors::_Format(mu);
	std::vector<torch::Tensor> mu__C = NuSolTensors::_Format(mu_);

	// ---- Polar Version of Particles ---- //
	std::vector<torch::Tensor> b_P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(b_C[0], b_C[1], b_C[2]), 3); 
	std::vector<torch::Tensor> b__P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(b__C[0], b__C[1], b__C[2]), 3); 
	std::vector<torch::Tensor> mu_P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(mu_C[0], mu_C[1], mu_C[2]), 3); 
	std::vector<torch::Tensor> mu__P = NuSolTensors::_Format(TransformTensors::PtEtaPhi(mu__C[0], mu__C[1], mu__C[2]), 3);

	// ---- Make into Tensors ---- //
	std::vector<torch::Tensor> _met = NuSolTensors::_Format(met);
	std::vector<torch::Tensor> _m = NuSolTensors::_Format(Mass); 
	
	return DoubleNuTensor::NuNu(b_P, b__P, mu_P, mu__P, b_C, b__C, mu_C, mu__C, _met[0], _met[1], _m[0], _m[1], _m[2], cutoff);
}
