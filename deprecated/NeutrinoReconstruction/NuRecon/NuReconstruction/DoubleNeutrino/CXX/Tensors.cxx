#include "../../Physics/Tensors/Headers/PhysicsTensors.h"
#include "../../Physics/Floats/Headers/PhysicsFloats.h"
#include "../Headers/Floats.h"

torch::Tensor DoubleNu::Tensors::V0(torch::Tensor metx, torch::Tensor mety)
{
	torch::Tensor matrix = torch::cat({metx, mety}, -1).view({-1, 2}); 
	matrix = torch::pad(matrix, {0, 1, 0, 0}, "constant", 0);
	torch::Tensor _m = PhysicsTensors::Slicer(matrix, 2, 3); 	
	_m = torch::cat({_m, _m, _m +1}, -1).view({-1, 1, 3}); 
	matrix = torch::einsum("ij,ijk->ijk", {matrix, _m}); 
	return matrix; 
}

torch::Tensor DoubleNu::Tensors::N(torch::Tensor H)
{
	H = DoubleNu::Tensors::H_Perp(H); 
	torch::Tensor H_T = torch::transpose(H, 1, 2); 
	torch::Tensor C_ = NuSolutionTensors::UnitCircle(H).repeat({H.sizes()[0], 1, 1}); 
	H_T = (H_T.view({-1, 3, 3, 1}) * C_.view({-1, 1, 3, 3})).sum(2); 
	return (H_T.view({-1, 3, 3, 1}) * H.view({-1, 1, 3, 3})).sum(2); 
}

torch::Tensor DoubleNu::Tensors::H_Perp(torch::Tensor H)
{
	H = torch::clone(H); 	
	H.index_put_({
			torch::indexing::Slice(), 
			2, 
			torch::indexing::Slice()
	}, 0); 
	H.index_put_({torch::indexing::Slice(), 2, 2}, 1); 
	H = torch::linalg::inv(H); 
	return H; 
}

std::vector<torch::Tensor> DoubleNu::Tensors::Init(
		torch::Tensor _b1, torch::Tensor _b2, 
		torch::Tensor _mu1, torch::Tensor _mu2, 
		torch::Tensor massTop, torch::Tensor massW, torch::Tensor massNu,
		torch::Tensor met, torch::Tensor phi, float cutoff)
{
	// First particle Solutions 
	torch::Tensor _bC1 = PhysicsTensors::ToPxPyPzE(_b1); 
	torch::Tensor _muC1 = PhysicsTensors::ToPxPyPzE(_mu1); 
	torch::Tensor Sol1_ = NuSolutionTensors::AnalyticalSolutionsCartesian(_bC1, _muC1, massTop, massW, massNu);
	
	// Second particle Solutions 
	torch::Tensor _bC2 = PhysicsTensors::ToPxPyPzE(_b2); 
	torch::Tensor _muC2 = PhysicsTensors::ToPxPyPzE(_mu2); 
	torch::Tensor Sol2_ = NuSolutionTensors::AnalyticalSolutionsCartesian(_bC2, _muC2, massTop, massW, massNu);
	
	// Get the Solution sets.
	torch::Tensor H1_ = NuSolutionTensors::H_Algo(_b1, _mu1, Sol1_); 
	torch::Tensor H2_ = NuSolutionTensors::H_Algo(_b2, _mu2, Sol2_);
	
	// Lets check if the determinant of the HX_ matrices are invertiable, else we skip this event 
	torch::Tensor _UseEvent = (torch::det(H1_) != 0) * (torch::det(H2_) != 0);
	H1_ = H1_.index({_UseEvent}); 
	H2_ = H2_.index({_UseEvent}); 

	_bC1 = _bC1.index({_UseEvent}); 
	_bC2 = _bC2.index({_UseEvent}); 

	_muC1 = _muC1.index({_UseEvent}); 
	_muC2 = _muC2.index({_UseEvent}); 

	Sol1_ = Sol1_.index({_UseEvent}); 
	Sol2_ = Sol2_.index({_UseEvent}); 
	
	met = met.index({_UseEvent});
	phi = phi.index({_UseEvent}); 

	// Create S_
	torch::Tensor V0_ = DoubleNu::Tensors::V0Polar(met, phi); 
	torch::Tensor C_ = NuSolutionTensors::UnitCircle(_muC1).repeat({_muC1.sizes()[0], 1, 1}); 
	torch::Tensor S_ = V0_ - C_; 
	
	torch::Tensor N1_ = DoubleNu::Tensors::N(H1_); 
	torch::Tensor N2_ = DoubleNu::Tensors::N(H2_);

	torch::Tensor H1_P = DoubleNu::Tensors::H_Perp(H1_); 
	torch::Tensor H2_P = DoubleNu::Tensors::H_Perp(H2_); 

	torch::Tensor n_ = torch::transpose(S_, 1, 2); 
	n_ = (n_.view({-1, 3, 3, 1}) * N2_.view({-1, 1, 3, 3})).sum(2);
	n_ = (n_.view({-1, 3, 3, 1}) * S_.view({-1, 1, 3, 3})).sum(2); 	
	
	// Calculate the intersection 
	torch::Tensor v = NuSolutionTensors::Intersections(N1_, n_, cutoff).view({-1, 6, 3}); 
	torch::Tensor v_ = (S_.view({-1, 1, 3, 3}) * v.view({-1, 6, 1, 3})).sum(-1); 	
	
	// Use Solutions to find neutrino momenta
	torch::Tensor K1_ = (H1_.view({-1, 3, 3, 1}) * H1_P.view({-1, 1, 3, 3})).sum(2); 
	torch::Tensor K2_ = (H2_.view({-1, 3, 3, 1}) * H2_P.view({-1, 1, 3, 3})).sum(2); 
	K1_ = (K1_.view({-1, 1, 3, 3}) * v.view({-1, 6, 1, 3})).sum(-1); 
	K2_ = (K2_.view({-1, 1, 3, 3}) * v_.view({-1, 6, 1, 3})).sum(-1); 
	return {_UseEvent, K1_, K2_, v, v_, n_}; 
}
