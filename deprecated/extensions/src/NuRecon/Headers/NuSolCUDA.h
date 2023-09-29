#ifndef H_NUSOL_CUDA
#define H_NUSOL_CUDA 

#include <iostream>
#include <torch/extension.h>
//#include "../CUDA/NuSolTorch.cu"
#include "../../Physics/Headers/CUDA.h"
#include "../../Transform/Headers/ToCartesianCUDA.h"
#include "../../Transform/Headers/ToPolarCUDA.h"
#include "../../Operators/Headers/CUDA.h"

torch::Tensor _Solutions(
		torch::Tensor _muP2, torch::Tensor _bP2, 
		torch::Tensor _mu_e, torch::Tensor _b_e, 
		torch::Tensor _cos, torch::Tensor _sin, 
		torch::Tensor mT2, torch::Tensor mW2, torch::Tensor mNu2);

torch::Tensor _H_Matrix(
		torch::Tensor x1, torch::Tensor y1, torch::Tensor Z, 
		torch::Tensor Om, torch::Tensor w, 
		std::vector<torch::Tensor> b_C, 
		torch::Tensor mu_phi, torch::Tensor mu_pz, torch::Tensor mu_P, 
		torch::Tensor mu_theta, torch::Tensor Rx, torch::Tensor Ry, torch::Tensor Rz); 

torch::Tensor _H_Matrix(torch::Tensor sols, torch::Tensor mu_P); 
torch::Tensor _Pi_2(torch::Tensor V);
torch::Tensor _Unit(torch::Tensor v, std::vector<int> diag); 
torch::Tensor _Factorization(torch::Tensor G); 
torch::Tensor _Factorization(torch::Tensor G, torch::Tensor Q, torch::Tensor Cofactors); 
torch::Tensor _SwapXY(torch::Tensor G, torch::Tensor Q);
std::vector<torch::Tensor> _EllipseLines(torch::Tensor Lines, torch::Tensor Q, torch::Tensor A, double cutoff); 

#define CHECK_CUDA(x) TORCH_CHECK(x.device().is_cuda(), "#x must be on CUDA")
#define CHECK_CONTIGUOUS(x) TORCH_CHECK(x.is_contiguous(), "#x must be contiguous")
#define CHECK_INPUT(x) CHECK_CUDA(x); CHECK_CONTIGUOUS(x)


namespace NuSolCUDA
{
	const void _CheckTensors(std::vector<torch::Tensor> T){for (torch::Tensor x : T){CHECK_INPUT(x);}}
	const std::vector<torch::Tensor> _MetXY(torch::Tensor met, torch::Tensor phi)
	{
		met = met.view({-1, 1}).contiguous(); 
		phi = phi.view({-1, 1}).contiguous(); 
		NuSolCUDA::_CheckTensors({met, phi}); 
		return { TransformCUDA::Px(met, phi), TransformCUDA::Py(met, phi) }; 
	}
	const std::vector<torch::Tensor> _Format1D(std::vector<torch::Tensor> inpt)
	{
		std::vector<torch::Tensor> out = {}; 
		out.reserve(inpt.size());
		for (unsigned int i = 0; i < inpt.size(); ++i){ out.push_back(inpt[i].view({-1, 1}).to(torch::kFloat64)); }
		return out; 
	}

	const std::vector<torch::Tensor> _Format(torch::Tensor t, int dim)
	{
		std::vector<torch::Tensor> _out; 
		for (int i = 0; i < dim; ++i)
		{
			_out.push_back((t.index({torch::indexing::Slice(), i}).view({-1, 1}).contiguous())); 
		}
		return _out; 
	}

	const std::vector<torch::Tensor> _Format(std::vector<std::vector<double>> inpt)
	{
		std::vector<torch::Tensor> out = {}; 
		out.reserve(inpt.size()); 
		for (unsigned int i = 0; i < inpt.size(); ++i)
		{
			out.push_back(OperatorsCUDA::TransferToCUDA(inpt[i]).view({-1, (unsigned int)inpt[i].size()})); 
		}
		return NuSolCUDA::_Format(torch::cat(out, 0), inpt[0].size()); 
	}

	const void _FixEnergyTensor(std::vector<torch::Tensor>* v1, std::vector<torch::Tensor>* v2)
	{
		if (v1 -> size() == 4)
		{
			v2 -> insert(v2 -> end(), (*v1)[3]); 
			v1 -> erase(v1 -> begin() + 3); 
		}
	}

	const torch::Tensor Solutions(
		std::vector<torch::Tensor> b_P, std::vector<torch::Tensor> b_C, 
		std::vector<torch::Tensor> mu_P, std::vector<torch::Tensor> mu_C, 
		torch::Tensor massT2, torch::Tensor massW2, torch::Tensor massNu2)
	{
		_CheckTensors({massT2, massW2, massNu2});	
		torch::Tensor _muP2 = PhysicsCUDA::P2(mu_C[0], mu_C[1], mu_C[2]);	
		torch::Tensor _bP2 = PhysicsCUDA::P2(b_C[0], b_C[1], b_C[2]); 

		torch::Tensor _cos = OperatorsCUDA::CosTheta(
				torch::cat({b_C[0], b_C[1], b_C[2]}, -1), 
				torch::cat({mu_C[0], mu_C[1], mu_C[2]}, -1)
		);

		torch::Tensor _sin = OperatorsCUDA::_SinTheta(_cos); 

		return _Solutions(_muP2, _bP2, mu_P[3], b_P[3], _cos, _sin, massT2, massW2, massNu2);
	}

	const torch::Tensor V0(torch::Tensor metx, torch::Tensor mety)
	{
		torch::Tensor matrix = torch::cat({metx, mety}, -1).view({-1, 2});
		matrix = torch::pad(matrix, {0, 1, 0, 0}, "constant", 0).view({-1, 3, 1}); 
		torch::Tensor t0 = torch::zeros_like(matrix); 
		return torch::cat({t0, t0, matrix}, -1); 
	}
	
	const torch::Tensor H_Matrix(
			torch::Tensor Sols_, std::vector<torch::Tensor> b_C, 
			std::vector<torch::Tensor> mu_C, torch::Tensor mu_P, torch::Tensor mu_phi) 
	{
		torch::Tensor H_ = _H_Matrix(Sols_, mu_P); 
		torch::Tensor theta_ = PhysicsCUDA::Theta(mu_C[0], mu_C[1], mu_C[2]);
		torch::Tensor Rz = OperatorsCUDA::Rz(-mu_phi); 
		torch::Tensor Ry = OperatorsCUDA::Ry(torch::acos(torch::zeros_like(mu_phi)) - theta_); 
		torch::Tensor Rx = OperatorsCUDA::Mul(Rz, torch::cat(b_C, -1).view({-1, 3, 1})); 	
		Rx = OperatorsCUDA::Mul(Ry, Rx.view({-1, 3, 1})); 
		Rx = -torch::atan2(Rx.index({torch::indexing::Slice(), 2}), Rx.index({torch::indexing::Slice(), 1})).view({-1, 1}); 
		Rx = OperatorsCUDA::Rx(Rx); 

		Rx = torch::transpose(Rx, 1, 2).contiguous(); 
		Ry = torch::transpose(Ry, 1, 2).contiguous(); 
		Rz = torch::transpose(Rz, 1, 2).contiguous(); 

		return OperatorsCUDA::Mul(OperatorsCUDA::Mul(Rz, OperatorsCUDA::Mul(Ry, Rx)), H_); 
	}

	const torch::Tensor Derivative(torch::Tensor x)
	{
		return OperatorsCUDA::Mul(OperatorsCUDA::Rz(_Pi_2(x)), _Unit(x, {1, 1, 0}));
	}

	const std::vector<torch::Tensor> Intersection(torch::Tensor A, torch::Tensor B, double cutoff)
	{

		torch::Tensor swp = torch::abs(OperatorsCUDA::Det(B)) > torch::abs(OperatorsCUDA::Det(A));
		torch::Tensor _tmp = B.index({swp}); 
		B.index_put_({swp}, A.index({swp})); 
		A.index_put_({swp}, _tmp);
		
		_tmp = OperatorsCUDA::Inv(A); 
		_tmp = OperatorsCUDA::Mul(_tmp, B);
		_tmp = torch::linalg::eigvals(_tmp); 
		torch::Tensor _r = torch::real(_tmp); 
		torch::Tensor msk = torch::isreal(_tmp)*torch::arange(3, 0, -1, torch::TensorOptions().device(A.device())); 
		msk = torch::argmax(msk, -1, true); 
		_r = torch::gather(_r, 1, msk).view({-1, 1, 1}); 
		torch::Tensor G = B - _r*A;
		torch::Tensor Q = _Factorization(G); 
		Q = _Factorization(G, Q, OperatorsCUDA::Cofactors(Q)); 
		Q = _SwapXY(G, Q); 
		torch::Tensor Lines = Q;
		
		// ------- Cross Product ------ //
		Q = Q.view({-1, 3, 1, 3}); 	
		_tmp = torch::zeros_like(Q); 
		Q = torch::cat({Q, Q, Q}, 2).view({-1, 9, 1, 3}); 
		_tmp = torch::cat({_tmp, _tmp, _tmp}, 1); 
		Q = torch::cat({_tmp, Q}, 2); 
		
		_tmp = torch::cat({A.view({-1, 1, 3, 3}), A.view({-1, 1, 3, 3}), A.view({-1, 1, 3, 3})}, 1).view({-1, 9, 1, 3}); 
		Q = torch::cat({Q, _tmp}, 2); 
		Q = OperatorsCUDA::Cofactors(Q.view({-1, 3, 3})); 
		Q = Q.index({torch::indexing::Slice(), 0, torch::indexing::Slice()}).view({-1, 3, 3, 3}); 
		// ------- End of Cross Product ------ //
		
		Q = std::get<1>(torch::linalg::eig(torch::transpose(Q, 2, 3))); 
		Q = torch::real(Q);
		Q = torch::transpose(Q, 2, 3); 

		return _EllipseLines(Lines, Q, A, cutoff); 
	}
}

namespace SingleNuCUDA
{
	const torch::Tensor Sigma2(
			torch::Tensor Sxx, torch::Tensor Sxy, 
			torch::Tensor Syx, torch::Tensor Syy)
	{
		torch::Tensor _S = torch::cat({Sxx, Sxy, Syx, Syy}, -1).view({-1, 2, 2});
		_S = torch::inverse(_S); 
		_S = torch::pad(_S, {0, 1, 0, 1}, "constant", 0);
		_S = torch::transpose(_S, 1, 2);
		return _S.contiguous(); 
	}

	const std::vector<torch::Tensor> Nu(
			std::vector<torch::Tensor> b_P, std::vector<torch::Tensor> mu_P, 
			std::vector<torch::Tensor> b_C, std::vector<torch::Tensor> mu_C,
			torch::Tensor met_x, torch::Tensor met_y, 
			torch::Tensor Sxx, torch::Tensor Sxy, torch::Tensor Syx, torch::Tensor Syy,
			torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff)
	{
		// ---- Format Input Vectors ---- // 
		NuSolCUDA::_FixEnergyTensor(&b_C, &b_P); 
		NuSolCUDA::_FixEnergyTensor(&mu_C, &mu_P); 

		// ---- Precalculate the Mass Squared ---- //
		torch::Tensor mT2 = OperatorsCUDA::Dot(mT, mT); 
		torch::Tensor mW2 = OperatorsCUDA::Dot(mW, mW); 
		torch::Tensor mNu2 = OperatorsCUDA::Dot(mNu, mNu); 

		// ---- Calculate the Solutions ---- //
		torch::Tensor sols_ = NuSolCUDA::Solutions(b_P, b_C, mu_P, mu_C, mT2, mW2, mNu2);
		torch::Tensor H_ = NuSolCUDA::H_Matrix(sols_, b_C, mu_C, PhysicsCUDA::P(mu_C[0], mu_C[1], mu_C[2]), mu_P[2]); 
		
		// ---- Protection Against non-invertible Matrices ---- //
		torch::Tensor SkipEvent = OperatorsCUDA::Det(H_) != 0;
		H_ = H_.index({SkipEvent}); 
		met_x = met_x.index({SkipEvent}); 
		met_y = met_y.index({SkipEvent});
		Sxx = Sxx.index({SkipEvent}).view({-1, 1}); 
		Sxy = Sxy.index({SkipEvent}).view({-1, 1}); 
		Syx = Syx.index({SkipEvent}).view({-1, 1}); 
		Syy = Syy.index({SkipEvent}).view({-1, 1});
		// ---------------------------------------------------- //
		
		torch::Tensor delta_ = NuSolCUDA::V0(met_x, met_y) - H_; 
		torch::Tensor X_ = OperatorsCUDA::Mul(torch::transpose(delta_, 1, 2).contiguous(), Sigma2(Sxx, Sxy, Syx, Syy)); 
		X_ = OperatorsCUDA::Mul(X_, delta_).view({-1, 3, 3}); 
		
		torch::Tensor M_ = OperatorsCUDA::Mul(X_, NuSolCUDA::Derivative(X_)); 
		M_ = M_ + torch::transpose(M_, 1, 2); 
		
		std::vector<torch::Tensor> _sol = NuSolCUDA::Intersection(M_, _Unit(M_, {1, 1, -1}), cutoff);
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
}

namespace NuCUDA
{
	const std::vector<torch::Tensor> PtEtaPhiE(
			torch::Tensor b, torch::Tensor mu, torch::Tensor met, torch::Tensor phi, 
			torch::Tensor Sxx, torch::Tensor Sxy, torch::Tensor Syx, torch::Tensor Syy, 
			torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff)
	{

		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_P = NuSolCUDA::_Format(b.view({-1, 4}), 4);
		std::vector<torch::Tensor> mu_P = NuSolCUDA::_Format(mu.view({-1, 4}), 4); 
		
		// ---- Cartesian Version of Particles ---- //
		std::vector<torch::Tensor> b_C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(b_P[0], b_P[1], b_P[2]), 3); 
		std::vector<torch::Tensor> mu_C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(mu_P[0], mu_P[1], mu_P[2]), 3); 

		// ---- Cartesian Version of Event Met ---- //
		std::vector<torch::Tensor> _met = NuSolCUDA::_MetXY(met, phi);

		// ---- Standardize Tensors ---- //
		std::vector<torch::Tensor> _S = NuSolCUDA::_Format1D({Sxx, Sxy, Syx, Syy}); 
		std::vector<torch::Tensor> _m = NuSolCUDA::_Format1D({mT, mW, mNu}); 

		return SingleNuCUDA::Nu(b_P, mu_P, b_C, mu_C, _met[0], _met[1], _S[0], _S[1], _S[2], _S[3], _m[0], _m[1], _m[2], cutoff); 
	}

	const std::vector<torch::Tensor> PxPyPzE(
			torch::Tensor b, torch::Tensor mu, torch::Tensor met_x, torch::Tensor met_y, 
			torch::Tensor Sxx, torch::Tensor Sxy, torch::Tensor Syx, torch::Tensor Syy, 
			torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff)
	{

		// ---- Cartesian Version of Particles ---- //
		std::vector<torch::Tensor> b_C = NuSolCUDA::_Format(b.view({-1, 4}), 4);
		std::vector<torch::Tensor> mu_C = NuSolCUDA::_Format(mu.view({-1, 4}), 4); 
		
		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(b_C[0], b_C[1], b_C[2]), 3); 
		std::vector<torch::Tensor> mu_P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(mu_C[0], mu_C[1], mu_C[2]), 3); 

		// ---- Cartesian Version of Event Met ---- //
		std::vector<torch::Tensor> _met = NuSolCUDA::_Format1D({met_x, met_y});

		// ---- Standardize Tensors ---- //
		std::vector<torch::Tensor> _S = NuSolCUDA::_Format1D({Sxx, Sxy, Syx, Syy}); 
		std::vector<torch::Tensor> _m = NuSolCUDA::_Format1D({mT, mW, mNu}); 

		return SingleNuCUDA::Nu(b_P, mu_P, b_C, mu_C, _met[0], _met[1], _S[0], _S[1], _S[2], _S[3], _m[0], _m[1], _m[2], cutoff); 
	}


	const std::vector<torch::Tensor> PtEtaPhiE_Double(
			double b_pt, double b_eta, double b_phi, double b_e, 
			double mu_pt, double mu_eta, double mu_phi, double mu_e, 
			double met, double phi,
			double Sxx, double Sxy, double Syx, double Syy, 
			double mT, double mW, double mNu, double cutoff)
	{
		// ---- Make into Tensors ---- //
		torch::Tensor b = OperatorsCUDA::TransferToCUDA({b_pt, b_eta, b_phi, b_e}).view({-1, 4}); 
		torch::Tensor mu = OperatorsCUDA::TransferToCUDA({mu_pt, mu_eta, mu_phi, mu_e}).view({-1, 4}); 

		std::vector<torch::Tensor> _met = NuSolCUDA::_Format(OperatorsCUDA::TransferToCUDA({met, phi}).view({-1, 2}), 2); 
		torch::Tensor met_x = TransformCUDA::Px(_met[0], _met[1]); 
		torch::Tensor met_y = TransformCUDA::Py(_met[0], _met[1]);
		
		std::vector<torch::Tensor> _S = NuSolCUDA::_Format(OperatorsCUDA::TransferToCUDA({Sxx, Sxy, Syx, Syy}).view({-1, 4}), 4);
		std::vector<torch::Tensor> _m = NuSolCUDA::_Format(OperatorsCUDA::TransferToCUDA({mT, mW, mNu}).view({-1, 3}), 3);

		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_P = NuSolCUDA::_Format(b, 4);
		std::vector<torch::Tensor> mu_P = NuSolCUDA::_Format(mu, 4); 
		
		// ---- Cartesian Version of Particles ---- //
		std::vector<torch::Tensor> b_C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(b_P[0], b_P[1], b_P[2]), 3); 
		std::vector<torch::Tensor> mu_C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(mu_P[0], mu_P[1], mu_P[2]), 3); 

		return SingleNuCUDA::Nu(b_P, mu_P, b_C, mu_C, met_x, met_y, _S[0], _S[1], _S[2], _S[3], _m[0], _m[1], _m[2], cutoff); 
	}

	const std::vector<torch::Tensor> PxPyPzE_Double(
			double b_px, double b_py, double b_pz, double b_e, 
			double mu_px, double mu_py, double mu_pz, double mu_e, 
			double met_x, double met_y,
			double Sxx, double Sxy, double Syx, double Syy, 
			double mT, double mW, double mNu, double cutoff)
	{
		// ---- Make into Tensors ---- //
		torch::Tensor b = OperatorsCUDA::TransferToCUDA({b_px, b_py, b_pz, b_e}).view({-1, 4}); 
		torch::Tensor mu = OperatorsCUDA::TransferToCUDA({mu_px, mu_py, mu_pz, mu_e}).view({-1, 4}); 
		std::vector<torch::Tensor> _met = NuSolCUDA::_Format(OperatorsCUDA::TransferToCUDA({met_x, met_y}).view({-1, 2}), 2); 
		std::vector<torch::Tensor> _S = NuSolCUDA::_Format(OperatorsCUDA::TransferToCUDA({Sxx, Sxy, Syx, Syy}).view({-1, 4}), 4);
		std::vector<torch::Tensor> _m = NuSolCUDA::_Format(OperatorsCUDA::TransferToCUDA({mT, mW, mNu}).view({-1, 3}), 3);

		// ---- Cartesian Version of Particles ---- //
		std::vector<torch::Tensor> b_C = NuSolCUDA::_Format(b, 4);
		std::vector<torch::Tensor> mu_C = NuSolCUDA::_Format(mu, 4); 

		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(b_C[0], b_C[1], b_C[2]), 3); 
		std::vector<torch::Tensor> mu_P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(mu_C[0], mu_C[1], mu_C[2]), 3); 

		return SingleNuCUDA::Nu(b_P, mu_P, b_C, mu_C, _met[0], _met[1], _S[0], _S[1], _S[2], _S[3], _m[0], _m[1], _m[2], cutoff); 
	}

	const std::vector<torch::Tensor> PtEtaPhiE_DoubleList(
			std::vector<std::vector<double>> b, std::vector<std::vector<double>> mu, 
			std::vector<std::vector<double>> met, std::vector<std::vector<double>> S, 
			std::vector<std::vector<double>> Mass, double cutoff)
	{
		
		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_P = NuSolCUDA::_Format(b); 
		std::vector<torch::Tensor> mu_P = NuSolCUDA::_Format(mu); 

		// ---- Cartesian Version of Particles ---- //
		std::vector<torch::Tensor> b_C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(b_P[0], b_P[1], b_P[2]), 3); 
		std::vector<torch::Tensor> mu_C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(mu_P[0], mu_P[1], mu_P[2]), 3); 

		std::vector<torch::Tensor> _S = NuSolCUDA::_Format(S); 
		std::vector<torch::Tensor> _m = NuSolCUDA::_Format(Mass); 
	
		std::vector<torch::Tensor> _met = NuSolCUDA::_Format(met); 
		torch::Tensor met_x = TransformCUDA::Px(_met[0], _met[1]); 
		torch::Tensor met_y = TransformCUDA::Py(_met[0], _met[1]);

		return SingleNuCUDA::Nu(b_P, mu_P, b_C, mu_C, met_x, met_y, _S[0], _S[1], _S[2], _S[3], _m[0], _m[1], _m[2], cutoff); 
	}

	const std::vector<torch::Tensor> PxPyPzE_DoubleList(
			std::vector<std::vector<double>> b, std::vector<std::vector<double>> mu, 
			std::vector<std::vector<double>> met, std::vector<std::vector<double>> S, 
			std::vector<std::vector<double>> Mass, double cutoff)
	{
		// ---- Cartesian Version of Particles ---- //
		std::vector<torch::Tensor> b_C = NuSolCUDA::_Format(b); 
		std::vector<torch::Tensor> mu_C = NuSolCUDA::_Format(mu); 

		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(b_C[0], b_C[1], b_C[2]), 3); 
		std::vector<torch::Tensor> mu_P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(mu_C[0], mu_C[1], mu_C[2]), 3); 

		std::vector<torch::Tensor> _S = NuSolCUDA::_Format(S); 
		std::vector<torch::Tensor> _m = NuSolCUDA::_Format(Mass); 
	
		std::vector<torch::Tensor> _met = NuSolCUDA::_Format(met); 
		return SingleNuCUDA::Nu(b_P, mu_P, b_C, mu_C, _met[0], _met[1], _S[0], _S[1], _S[2], _S[3], _m[0], _m[1], _m[2], cutoff); 
	}
}

namespace DoubleNuCUDA
{
	const torch::Tensor H_perp(torch::Tensor H)
	{
		torch::Tensor H_ = torch::clone(H); 
		H_.index_put_({torch::indexing::Slice(), 2, torch::indexing::Slice()}, 0); 
		H_.index_put_({torch::indexing::Slice(), 2, 2}, 1);
		return H_.contiguous();
	}

	const torch::Tensor N(torch::Tensor H)
	{
		torch::Tensor H_ = H_perp(H); 
		H_ = OperatorsCUDA::Inv(H_);
		torch::Tensor H_T = torch::transpose(H_, 1, 2).contiguous(); 
		H_T = OperatorsCUDA::Mul(H_T, _Unit(H_, {1, 1, -1})); 
		return OperatorsCUDA::Mul(H_T, H_); 
	}
	
	const std::vector<torch::Tensor> Residuals(
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

	const std::vector<torch::Tensor> NuNu(
			std::vector<torch::Tensor> b_P, std::vector<torch::Tensor> b__P, std::vector<torch::Tensor> mu_P, std::vector<torch::Tensor> mu__P, 
			std::vector<torch::Tensor> b_C, std::vector<torch::Tensor> b__C, std::vector<torch::Tensor> mu_C, std::vector<torch::Tensor> mu__C, 
			torch::Tensor met_x, torch::Tensor met_y, 
			torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff)
	{

		// ---- Format Input Vectors ---- // 
		NuSolCUDA::_FixEnergyTensor(&b_C, &b_P); 
		NuSolCUDA::_FixEnergyTensor(&mu_C, &mu_P); 
		NuSolCUDA::_FixEnergyTensor(&b__C, &b__P); 
		NuSolCUDA::_FixEnergyTensor(&mu__C, &mu__P); 

		torch::Tensor muP_ = PhysicsCUDA::P(mu_C[0], mu_C[1], mu_C[2]); 
		torch::Tensor muP__ = PhysicsCUDA::P(mu__C[0], mu__C[1], mu__C[2]); 

		// ---- Precalculate the Mass Squared ---- //
		torch::Tensor mT2 = OperatorsCUDA::Dot(mT, mT); 
		torch::Tensor mW2 = OperatorsCUDA::Dot(mW, mW); 
		torch::Tensor mNu2 = OperatorsCUDA::Dot(mNu, mNu); 

		// ---- Starting the algorithm ---- //
		torch::Tensor sols_ = NuSolCUDA::Solutions(b_P, b_C, mu_P, mu_C, mT2, mW2, mNu2);
		torch::Tensor sols__ = NuSolCUDA::Solutions(b__P, b__C, mu__P, mu__C, mT2, mW2, mNu2);
		
		torch::Tensor H_ = NuSolCUDA::H_Matrix(sols_, b_C, mu_C, muP_, mu_P[2]); 
		torch::Tensor H__ = NuSolCUDA::H_Matrix(sols__, b__C, mu__C, muP__, mu__P[2]); 

		// ---- Protection Against non-invertible Matrices ---- //
		torch::Tensor SkipEvent = OperatorsCUDA::Dot(OperatorsCUDA::Det(H_).view({-1, 1}), OperatorsCUDA::Det(H__).view({-1, 1})) != 0.; 
		SkipEvent = SkipEvent.view({-1}); 
		H_ = H_.index({SkipEvent}); 
		H__ = H__.index({SkipEvent}); 
		met_x = met_x.index({SkipEvent}); 
		met_y = met_y.index({SkipEvent});

		if (H_.size(0) == 0)
		{
			return {SkipEvent == false, SkipEvent == false, SkipEvent == false, SkipEvent == false, SkipEvent == false};
		}

		torch::Tensor H__P = H_perp(H__);
		torch::Tensor H_P = H_perp(H_); 

		torch::Tensor N_ = DoubleNuCUDA::N(H_); 
		torch::Tensor N__ = DoubleNuCUDA::N(H__); 
		torch::Tensor S_ = NuSolCUDA::V0(met_x, met_y) - _Unit(met_y, {1, 1, -1});
		torch::Tensor n_ = OperatorsCUDA::Mul(OperatorsCUDA::Mul(S_.transpose(1, 2).contiguous(), N__), S_); 
		
		// ----- Launching the Intersection code ------- //
		std::vector<torch::Tensor> _sol = NuSolCUDA::Intersection(N_, n_, cutoff);
		torch::Tensor v = _sol[1].index({
				torch::indexing::Slice(), 0,
				torch::indexing::Slice(), 
				torch::indexing::Slice()}).view({-1, 3, 3});

		torch::Tensor v_ = _sol[1].index({
				torch::indexing::Slice(), 1, 
				torch::indexing::Slice(), 
				torch::indexing::Slice()}).view({-1, 3, 3});
		
		torch::Tensor resid = torch::sum(torch::sum(v + v_, -1), -1) == 0.0;
		std::vector<torch::Tensor> lstsq = Residuals(H_P, H__P, met_x, met_y, resid); 

		v = torch::cat({v, v_}, 1);
		v_ = torch::sum(S_.view({-1, 1, 3, 3})*v.view({-1, 6, 1, 3}), -1);
	
		if (lstsq.size() != 0)
		{
			v.index_put_({resid}, lstsq[0]); 
			v_.index_put_({resid}, lstsq[1]); 
		}

		// ------ Neutrino Solutions -------- //
		torch::Tensor K = OperatorsCUDA::Mul(H_, OperatorsCUDA::Inv( H_P )); 
		torch::Tensor K_ = OperatorsCUDA::Mul(H__, OperatorsCUDA::Inv( H__P )); 
		
		K = (K.view({-1, 1, 3, 3}) * v.view({-1, 6, 1, 3})).sum(-1); 
		K_ = (K_.view({-1, 1, 3, 3}) * v_.view({-1, 6, 1, 3})).sum(-1); 
		return {SkipEvent == false, K, K_, v, v_, n_, _sol[2], _sol[3]}; 
	}
}

namespace NuNuCUDA
{
	const std::vector<torch::Tensor> PtEtaPhiE(
			torch::Tensor b, torch::Tensor b_, torch::Tensor mu, torch::Tensor mu_,
			torch::Tensor met, torch::Tensor phi, 
			torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff)
	{
		
		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_P = NuSolCUDA::_Format(b.view({-1, 4}), 4);
		std::vector<torch::Tensor> b__P = NuSolCUDA::_Format(b_.view({-1, 4}), 4);
		std::vector<torch::Tensor> mu_P = NuSolCUDA::_Format(mu.view({-1, 4}), 4); 
		std::vector<torch::Tensor> mu__P = NuSolCUDA::_Format(mu_.view({-1, 4}), 4); 
		
		// ---- Cartesian Version of Particles ---- //
		std::vector<torch::Tensor> b_C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(b_P[0], b_P[1], b_P[2]), 3); 
		std::vector<torch::Tensor> b__C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(b__P[0], b__P[1], b__P[2]), 3); 
		std::vector<torch::Tensor> mu_C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(mu_P[0], mu_P[1], mu_P[2]), 3); 
		std::vector<torch::Tensor> mu__C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(mu__P[0], mu__P[1], mu__P[2]), 3);

		// ---- Cartesian Version of Event Met ---- //
		NuSolCUDA::_CheckTensors({met, phi}); 
		std::vector<torch::Tensor> _met = NuSolCUDA::_MetXY(met, phi); 
		
		return DoubleNuCUDA::NuNu(b_P, b__P, mu_P, mu__P, b_C, b__C, mu_C, mu__C, _met[0], _met[1], mT, mW, mNu, cutoff); 
	}

	const std::vector<torch::Tensor> PxPyPzE(
			torch::Tensor b, torch::Tensor b_, torch::Tensor mu, torch::Tensor mu_,
			torch::Tensor met_x, torch::Tensor met_y, 
			torch::Tensor mT, torch::Tensor mW, torch::Tensor mNu, double cutoff)
	{

		// ---- Cartesian Version of Particles ---- //
		std::vector<torch::Tensor> b_C = NuSolCUDA::_Format(b.view({-1, 4}), 4);
		std::vector<torch::Tensor> b__C = NuSolCUDA::_Format(b_.view({-1, 4}), 4);
		std::vector<torch::Tensor> mu_C = NuSolCUDA::_Format(mu.view({-1, 4}), 4); 
		std::vector<torch::Tensor> mu__C = NuSolCUDA::_Format(mu_.view({-1, 4}), 4);

		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(b_C[0], b_C[1], b_C[2]), 3); 
		std::vector<torch::Tensor> b__P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(b__C[0], b__C[1], b__C[2]), 3); 
		std::vector<torch::Tensor> mu_P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(mu_C[0], mu_C[1], mu_C[2]), 3); 
		std::vector<torch::Tensor> mu__P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(mu__C[0], mu__C[1], mu__C[2]), 3);

		// ---- Standardize Tensors ---- //
		std::vector<torch::Tensor> _met = NuSolCUDA::_Format1D({met_x, met_y});
		std::vector<torch::Tensor> _m = NuSolCUDA::_Format1D({mT, mW, mNu}); 

		return DoubleNuCUDA::NuNu(b_P, b__P, mu_P, mu__P, b_C, b__C, mu_C, mu__C, _met[0], _met[1], _m[0], _m[1], _m[2], cutoff);
	}


	const std::vector<torch::Tensor> PtEtaPhiE_Double(
			double b_pt, double b_eta, double b_phi, double b_e, 
			double b__pt, double b__eta, double b__phi, double b__e, 
			double mu_pt, double mu_eta, double mu_phi, double mu_e, 
			double mu__pt, double mu__eta, double mu__phi, double mu__e, 
			double met, double phi,
			double mT, double mW, double mNu, double cutoff)
	{
		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_P = NuSolCUDA::_Format({{b_pt, b_eta, b_phi, b_e}});
		std::vector<torch::Tensor> b__P = NuSolCUDA::_Format({{b__pt, b__eta, b__phi, b__e}});
		std::vector<torch::Tensor> mu_P = NuSolCUDA::_Format({{mu_pt, mu_eta, mu_phi, mu_e}});
		std::vector<torch::Tensor> mu__P = NuSolCUDA::_Format({{mu__pt, mu__eta, mu__phi, mu__e}});

		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(b_P[0], b_P[1], b_P[2]), 3); 
		std::vector<torch::Tensor> b__C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(b__P[0], b__P[1], b__P[2]), 3); 
		std::vector<torch::Tensor> mu_C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(mu_P[0], mu_P[1], mu_P[2]), 3); 
		std::vector<torch::Tensor> mu__C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(mu__P[0], mu__P[1], mu__P[2]), 3);

		// ---- Make into Tensors ---- //
		std::vector<torch::Tensor> _m = NuSolCUDA::_Format({{mT, mW, mNu}}); 
		std::vector<torch::Tensor> _met = NuSolCUDA::_Format({{met, phi}});
		_met = NuSolCUDA::_MetXY(_met[0], _met[1]); 
		
		return DoubleNuCUDA::NuNu(b_P, b__P, mu_P, mu__P, b_C, b__C, mu_C, mu__C, _met[0], _met[1], _m[0], _m[1], _m[2], cutoff);
	}

	const std::vector<torch::Tensor> PxPyPzE_Double(
			double b_px, double b_py, double b_pz, double b_e, 
			double b__px, double b__py, double b__pz, double b__e, 
			double mu_px, double mu_py, double mu_pz, double mu_e, 
			double mu__px, double mu__py, double mu__pz, double mu__e, 
			double met_x, double met_y,
			double mT, double mW, double mNu, double cutoff)
	{

		// ---- Cartesian Version of Particles ---- //
		std::vector<torch::Tensor> b_C = NuSolCUDA::_Format({{b_px, b_py, b_pz, b_e}});
		std::vector<torch::Tensor> b__C = NuSolCUDA::_Format({{b__px, b__py, b__pz, b__e}});
		std::vector<torch::Tensor> mu_C = NuSolCUDA::_Format({{mu_px, mu_py, mu_pz, mu_e}});
		std::vector<torch::Tensor> mu__C = NuSolCUDA::_Format({{mu__px, mu__py, mu__pz, mu__e}});

		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(b_C[0], b_C[1], b_C[2]), 3); 
		std::vector<torch::Tensor> b__P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(b__C[0], b__C[1], b__C[2]), 3); 
		std::vector<torch::Tensor> mu_P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(mu_C[0], mu_C[1], mu_C[2]), 3); 
		std::vector<torch::Tensor> mu__P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(mu__C[0], mu__C[1], mu__C[2]), 3);

		// ---- Make into Tensors ---- //
		std::vector<torch::Tensor> _met = NuSolCUDA::_Format({{met_x, met_y}});
		std::vector<torch::Tensor> _m = NuSolCUDA::_Format({{mT, mW, mNu}}); 
		
		return DoubleNuCUDA::NuNu(b_P, b__P, mu_P, mu__P, b_C, b__C, mu_C, mu__C, _met[0], _met[1], _m[0], _m[1], _m[2], cutoff);
	}

	const std::vector<torch::Tensor> PtEtaPhiE_DoubleList(
			std::vector<std::vector<double>> b, std::vector<std::vector<double>> b_, 
			std::vector<std::vector<double>> mu, std::vector<std::vector<double>> mu_, 
			std::vector<std::vector<double>> met, std::vector<std::vector<double>> Mass, double cutoff)
	{
		
		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_P = NuSolCUDA::_Format(b);
		std::vector<torch::Tensor> b__P = NuSolCUDA::_Format(b_);
		std::vector<torch::Tensor> mu_P = NuSolCUDA::_Format(mu);
		std::vector<torch::Tensor> mu__P = NuSolCUDA::_Format(mu_);

		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(b_P[0], b_P[1], b_P[2]), 3); 
		std::vector<torch::Tensor> b__C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(b__P[0], b__P[1], b__P[2]), 3); 
		std::vector<torch::Tensor> mu_C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(mu_P[0], mu_P[1], mu_P[2]), 3); 
		std::vector<torch::Tensor> mu__C = NuSolCUDA::_Format(TransformCUDA::PxPyPz(mu__P[0], mu__P[1], mu__P[2]), 3);

		// ---- Make into Tensors ---- //
		std::vector<torch::Tensor> _met = NuSolCUDA::_Format(met);
		_met = NuSolCUDA::_MetXY(_met[0], _met[1]); 
		std::vector<torch::Tensor> _m = NuSolCUDA::_Format(Mass); 
		
		return DoubleNuCUDA::NuNu(b_P, b__P, mu_P, mu__P, b_C, b__C, mu_C, mu__C, _met[0], _met[1], _m[0], _m[1], _m[2], cutoff);
	}

	const std::vector<torch::Tensor> PxPyPzE_DoubleList(
			std::vector<std::vector<double>> b, std::vector<std::vector<double>> b_, 
			std::vector<std::vector<double>> mu, std::vector<std::vector<double>> mu_, 
			std::vector<std::vector<double>> met, std::vector<std::vector<double>> Mass, double cutoff)
	{
		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_C = NuSolCUDA::_Format(b);
		std::vector<torch::Tensor> b__C = NuSolCUDA::_Format(b_);
		std::vector<torch::Tensor> mu_C = NuSolCUDA::_Format(mu);
		std::vector<torch::Tensor> mu__C = NuSolCUDA::_Format(mu_);

		// ---- Polar Version of Particles ---- //
		std::vector<torch::Tensor> b_P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(b_C[0], b_C[1], b_C[2]), 3); 
		std::vector<torch::Tensor> b__P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(b__C[0], b__C[1], b__C[2]), 3); 
		std::vector<torch::Tensor> mu_P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(mu_C[0], mu_C[1], mu_C[2]), 3); 
		std::vector<torch::Tensor> mu__P = NuSolCUDA::_Format(TransformCUDA::PtEtaPhi(mu__C[0], mu__C[1], mu__C[2]), 3);

		// ---- Make into Tensors ---- //
		std::vector<torch::Tensor> _met = NuSolCUDA::_Format(met);
		std::vector<torch::Tensor> _m = NuSolCUDA::_Format(Mass); 
		
		return DoubleNuCUDA::NuNu(b_P, b__P, mu_P, mu__P, b_C, b__C, mu_C, mu__C, _met[0], _met[1], _m[0], _m[1], _m[2], cutoff);
	}
}
#endif 
