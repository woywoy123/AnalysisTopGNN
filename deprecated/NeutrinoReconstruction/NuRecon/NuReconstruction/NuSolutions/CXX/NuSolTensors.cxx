#include "../Headers/NuSolTensors.h"
#include "../../Physics/Tensors/Headers/PhysicsTensors.h"

torch::Tensor NuSolutionTensors::x0Polar(torch::Tensor PolarL, torch::Tensor MassH, torch::Tensor MassL)
{
	return -(MassH.pow(2) 
			- MassL.pow(2) 
			- PhysicsTensors::Mass2Polar(PolarL)
		)/(2*PhysicsTensors::Slicer(PolarL, 3, 4)); 
}

torch::Tensor NuSolutionTensors::x0Cartesian(torch::Tensor CartesianL, torch::Tensor MassH, torch::Tensor MassL)
{
	return -(MassH.pow(2) 
			- MassL.pow(2) 
			- PhysicsTensors::Mass2Cartesian(CartesianL)
		)/(2*PhysicsTensors::Slicer(CartesianL, 3, 4)); 
}

torch::Tensor NuSolutionTensors::SxCartesian(torch::Tensor _b, torch::Tensor _mu, torch::Tensor mW, torch::Tensor mNu)
{
	torch::Tensor beta_muon = PhysicsTensors::BetaCartesian(_mu);
	torch::Tensor beta_muon2 = beta_muon.pow(2); 
	torch::Tensor x0 = NuSolutionTensors::x0Cartesian(_mu, mW, mNu); 

	return (x0 * beta_muon - PhysicsTensors::PCartesian(_mu)*(1 - beta_muon2))/(beta_muon2); 

}

torch::Tensor NuSolutionTensors::SyCartesian(torch::Tensor _b, torch::Tensor _mu, 
		torch::Tensor mTop, torch::Tensor mW, torch::Tensor Sx)
{
	torch::Tensor beta_b = PhysicsTensors::BetaCartesian(_b); 
	torch::Tensor costheta = PhysicsTensors::CosThetaCartesian(_b, _mu); 
	torch::Tensor sintheta = torch::sqrt(1 - costheta.pow(2)); 
	
	torch::Tensor x0 = NuSolutionTensors::x0Cartesian(_b, mTop, mW); 

	return ((x0 / beta_b) - costheta * Sx) / sintheta; 
}

torch::Tensor NuSolutionTensors::SxSyCartesian(torch::Tensor _b, torch::Tensor _mu, 
		torch::Tensor mTop, torch::Tensor mW, torch::Tensor mNu)
{
	torch::Tensor beta_b = PhysicsTensors::BetaCartesian(_b); 
	torch::Tensor beta_muon = PhysicsTensors::BetaCartesian(_mu);
	torch::Tensor beta_muon2 = beta_muon.pow(2); 
	
	torch::Tensor costheta = PhysicsTensors::CosThetaCartesian(_b, _mu); 
	torch::Tensor sintheta = torch::sqrt(1 - costheta.pow(2)); 

	torch::Tensor x0t = NuSolutionTensors::x0Cartesian(_b, mTop, mW);
	torch::Tensor x0m = NuSolutionTensors::x0Cartesian(_mu, mW, mNu);
	       
	torch::Tensor Sx = (x0m * beta_muon - PhysicsTensors::PCartesian(_mu)*(1 - beta_muon2)) / beta_muon2; 
	torch::Tensor Sy = ((x0t / beta_b) - costheta * Sx) / sintheta;
	return torch::cat({Sx, Sy}, 1);
}

torch::Tensor NuSolutionTensors::Eps2Polar(torch::Tensor mW, torch::Tensor mNu, torch::Tensor mu)
{
	return NuSolutionTensors::Eps2Cartesian(mW, mNu, PhysicsTensors::ToPxPyPzE(mu)); 
}

torch::Tensor NuSolutionTensors::Eps2Cartesian(torch::Tensor mW, torch::Tensor mNu, torch::Tensor mu)
{
	return (mW - mNu) * (1 - PhysicsTensors::Beta2Cartesian(mu)); 
}

torch::Tensor NuSolutionTensors::wCartesian(torch::Tensor _b, torch::Tensor _mu, int factor)
{
	torch::Tensor beta_b = PhysicsTensors::BetaCartesian(_b); 
	torch::Tensor beta_mu = PhysicsTensors::BetaCartesian(_mu);

	torch::Tensor costheta = PhysicsTensors::CosThetaCartesian(_b, _mu); 
	torch::Tensor sintheta = torch::sqrt(1 - costheta.pow(2)); 
	
	return ( factor * (beta_mu / beta_b) - costheta ) / sintheta;
}

torch::Tensor NuSolutionTensors::wPolar(torch::Tensor _b, torch::Tensor _mu, int factor)
{
	return NuSolutionTensors::wCartesian(PhysicsTensors::ToPxPyPzE(_b), PhysicsTensors::ToPxPyPzE(_mu), factor); 
}

torch::Tensor NuSolutionTensors::Omega2Cartesian(torch::Tensor _b, torch::Tensor _mu)
{
	return NuSolutionTensors::wCartesian(_b, _mu, 1).pow(2) + 1 - PhysicsTensors::Beta2Cartesian(_mu);  
}

torch::Tensor NuSolutionTensors::Omega2Polar(torch::Tensor _b, torch::Tensor _mu)
{
	return NuSolutionTensors::Omega2Cartesian(PhysicsTensors::ToPxPyPzE(_b), PhysicsTensors::ToPxPyPzE(_mu)); 
}


torch::Tensor NuSolutionTensors::AnalyticalSolutionsCartesian(
		torch::Tensor _b, torch::Tensor _mu,
		torch::Tensor massTop, torch::Tensor massW, torch::Tensor massNu)
{
	// ====================== Muon =================================== //
	// Slice the given vector into rows 
	torch::Tensor mu_px = PhysicsTensors::Slicer(_mu, 0, 1); 
	torch::Tensor mu_py = PhysicsTensors::Slicer(_mu, 1, 2); 
	torch::Tensor mu_pz = PhysicsTensors::Slicer(_mu, 2, 3); 
	torch::Tensor mu_e  = PhysicsTensors::Slicer(_mu, 3, 4); 
	
	// Square the momentum components
	_mu = _mu.pow(2); 
	torch::Tensor mu_p2x = PhysicsTensors::Slicer(_mu, 0, 1); 
	torch::Tensor mu_p2y = PhysicsTensors::Slicer(_mu, 1, 2); 
	torch::Tensor mu_p2z = PhysicsTensors::Slicer(_mu, 2, 3); 
	torch::Tensor mu_e2  = PhysicsTensors::Slicer(_mu, 3, 4);
	
	// Get additional kinematic variables P2, mass2, beta 
	torch::Tensor mu_P2    = mu_p2x + mu_p2y + mu_p2z;
	torch::Tensor mu_mass2 = mu_e2 - mu_P2; 
	torch::Tensor mu_beta2 = mu_P2 / mu_e2;

	// ====================== b-quark =================================== //
	// Slice the given vector into rows 
	torch::Tensor b_px = PhysicsTensors::Slicer(_b, 0, 1); 
	torch::Tensor b_py = PhysicsTensors::Slicer(_b, 1, 2); 
	torch::Tensor b_pz = PhysicsTensors::Slicer(_b, 2, 3); 
	torch::Tensor b_e  = PhysicsTensors::Slicer(_b, 3, 4); 
	
	// Square the momentum components
	_b = _b.pow(2); 
	torch::Tensor b_p2x = PhysicsTensors::Slicer(_b, 0, 1); 
	torch::Tensor b_p2y = PhysicsTensors::Slicer(_b, 1, 2); 
	torch::Tensor b_p2z = PhysicsTensors::Slicer(_b, 2, 3); 
	torch::Tensor b_e2  = PhysicsTensors::Slicer(_b, 3, 4);
	
	// Get additional kinematic variables P2, mass2, beta 
	torch::Tensor b_P2    = b_p2x + b_p2y + b_p2z;
	torch::Tensor b_mass2 = b_e2 - b_P2; 
	torch::Tensor b_beta = torch::sqrt(b_P2 / b_e2);	
	
	// ===================== costheta ==================== //
	torch::Tensor costheta = (b_px * mu_px + b_py * mu_py + b_pz * mu_pz) / torch::sqrt(mu_P2 * b_P2); 
	torch::Tensor sintheta = torch::sqrt(1 - costheta.pow(2)); 

	// ===================== masses ===================== //
	massTop = massTop.pow(2); 
	massW = massW.pow(2); 
	massNu = massNu.pow(2);
	torch::Tensor _r = torch::sqrt(mu_beta2) / b_beta; 

	// ===================== Algo Variables ============= //
	torch::Tensor x0p = - ( massTop - massW - b_mass2) / (2 * b_e); 
	torch::Tensor x0  = - ( massW - mu_mass2 - massNu) / (2 * mu_e); 
	torch::Tensor Sx = (x0 * torch::sqrt(mu_beta2) - torch::sqrt(mu_P2) * (1 - mu_beta2)) / mu_beta2; 
	torch::Tensor Sy = ((x0p / b_beta) - costheta * Sx) / sintheta; 
	torch::Tensor eps2 = (massW - massNu) * (1 - mu_beta2); 
	torch::Tensor w = ( _r - costheta ) / sintheta;
	torch::Tensor w_ = (-_r - costheta) / sintheta;
	torch::Tensor Omega2 = w.pow(2) + 1 - mu_beta2; 
	_r = Sx + w * Sy; 
	torch::Tensor x = Sx - (_r) / Omega2;
	torch::Tensor y = Sy - (_r) * w / Omega2; 
	torch::Tensor z2 = x.pow(2) * Omega2 - (Sy - w * Sx).pow(2) - (massW - x0.pow(2) - eps2); 
	z2 = torch::sqrt(torch::relu(z2)); 
	
	return torch::cat({costheta, sintheta, x0, x0p, Sx, Sy, w, w_, x, y, z2, Omega2, eps2}, 1); 
}

torch::Tensor NuSolutionTensors::Rotation(torch::Tensor _b, torch::Tensor _mu)
{
	
	torch::Tensor _bC = PhysicsTensors::ToPxPyPz(_b).view({-1, 1, 3});
	torch::Tensor Rz = PhysicsTensors::Rz( -1*PhysicsTensors::Slicer(_mu, 2, 3));

	torch::Tensor _agl = PhysicsTensors::ToThetaPolar(_mu); 
	torch::Tensor Ry = PhysicsTensors::Ry( torch::acos(torch::tensor({0}, PhysicsTensors::Options(_agl))) - _agl); 
	_agl = (Ry * (Rz * _bC).sum({2}).view({-1, 1, 3})).sum({2});	

	torch::Tensor z = PhysicsTensors::Slicer(_agl, 2, 3); 
	torch::Tensor y = PhysicsTensors::Slicer(_agl, 1, 2); 
	torch::Tensor Rx = torch::transpose(PhysicsTensors::Rx( -torch::atan2(z, y) ), 1, 2); 
	Ry = torch::transpose(Ry, 1, 2); 	
	Rz = torch::transpose(Rz, 1, 2);
	
	return torch::matmul(Rz, torch::matmul(Ry, Rx));
}

torch::Tensor NuSolutionTensors::H_Algo(torch::Tensor _b, torch::Tensor _mu, torch::Tensor Sol_)
{
	torch::Tensor x = PhysicsTensors::Slicer(Sol_, 8, 9).view({-1, 1, 1}); 
	torch::Tensor y = PhysicsTensors::Slicer(Sol_, 9, 10).view({-1, 1, 1}); 
	torch::Tensor P = PhysicsTensors::PPolar(_mu).view({-1, 1, 1}); 

	torch::Tensor Z = PhysicsTensors::Slicer(Sol_, 10, 11).view({-1, 1, 1}); 
	torch::Tensor w = PhysicsTensors::Slicer(Sol_, 6, 7).view({-1, 1, 1}); 
	torch::Tensor omega = torch::sqrt(PhysicsTensors::Slicer(Sol_, 11, 12)).view({-1, 1, 1}); 

	torch::Tensor R_ = NuSolutionTensors::Rotation(_b, _mu); 
	torch::Tensor t0 = torch::zeros(w.sizes(), PhysicsTensors::Options(w)); 
	
	torch::Tensor H_Til = torch::cat({
		        		torch::cat({Z/omega   , t0, x - P}, 2), 
		        		torch::cat({w*Z/omega , t0, y    }, 2), 
		        		torch::cat({t0        ,  Z, t0   }, 2)
		        	}, 1);  
	return torch::matmul(R_, H_Til); 
}

torch::Tensor NuSolutionTensors::UnitCircle(torch::Tensor X)
{
	return torch::diag( torch::tensor({1., 1., -1.}, PhysicsTensors::Options(X)) ).view({-1, 3, 3}); 
}

torch::Tensor NuSolutionTensors::Derivative(torch::Tensor X)
{
	torch::Tensor diag = torch::diag( 
				torch::tensor({1., 1., 0.}, PhysicsTensors::Options(X)) 
			).view({-1, 3, 3}); 
	
	
	return X.matmul(
			PhysicsTensors::Rz(
				torch::acos(
					torch::tensor({0}, PhysicsTensors::Options(diag)) 
				)
			).matmul(diag)); 
}

torch::Tensor NuSolutionTensors::Intersections(torch::Tensor A, torch::Tensor B, float cutoff)
{

	torch::Tensor msk = torch::abs(torch::det(A)) < torch::abs(torch::det(B)); 
	torch::Tensor _tmp = B.index({msk}); 
	
	B.index_put_({msk}, A.index({msk})); 
	A.index_put_({msk}, _tmp);
	
	_tmp = torch::linalg::eigvals(torch::inverse(A).matmul(B)); 
	torch::Tensor r_ = torch::real(_tmp); 
	msk = torch::isreal(_tmp)*(r_ != 0);
	msk = torch::argmax(msk*torch::arange(3, 0, -1, PhysicsTensors::Options(A)), -1, true); 
	r_ = torch::gather(r_, 1, msk).view({-1, 1, 1}); 	
	torch::Tensor G = (B - r_*A); 
	
	// ===== Solutions ===== //
	torch::Tensor z0 = torch::zeros_like(G); 
	
	// 1. Case G11 and G22 == 0; horizontal + vertical solutions to line intersection 
	msk = G.index({torch::indexing::Slice(), 0, 0}) + G.index({torch::indexing::Slice(), 1, 1}) == 0; 
	z0.index_put_({msk, 0, 0}, G.index({msk, 0, 1})); 
	z0.index_put_({msk, 0, 2}, G.index({msk, 1, 2})); 
	z0.index_put_({msk, 1, 1}, G.index({msk, 0, 1})); 
	z0.index_put_({msk, 1, 2}, G.index({msk, 0, 2}) - G.index({msk, 1, 2})); 

	// ====== Reduce tensor size by ignoring msk true cases ====== //
	z0.index_put_({msk == false}, G.index({msk == false}));  
	torch::Tensor Q = z0.index({msk == false}); 

	// ====== Check if G00 > G11 and swap for numerical stability ====== //
	torch::Tensor swp = torch::abs(Q.index({torch::indexing::Slice(), 0, 0})) > torch::abs(Q.index({torch::indexing::Slice(), 1, 1})); 

	Q.index_put_({swp}, torch::cat({
				Q.index({swp, 1, torch::indexing::Slice()}).view({-1, 1, 3}), 
				Q.index({swp, 0, torch::indexing::Slice()}).view({-1, 1, 3}), 
				Q.index({swp, 2, torch::indexing::Slice()}).view({-1, 1, 3})}, 1)); 
	Q.index_put_({swp}, torch::cat({
				Q.index({swp, torch::indexing::Slice(), 1}).view({-1, 1, 3}), 
				Q.index({swp, torch::indexing::Slice(), 0}).view({-1, 1, 3}), 
				Q.index({swp, torch::indexing::Slice(), 2}).view({-1, 1, 3})}, 1)); 
	Q = Q/(Q.index({torch::indexing::Slice(), 1, 1}).view({-1, 1, 1})); 
	
	// Calculate the cofactors - this checks if intersection
	torch::Tensor q00 = NuSolutionTensors::cofactor(Q, {1, 2}, {1, 2});
	torch::Tensor q02 = NuSolutionTensors::cofactor(Q, {1, 2}, {0, 1}); 
	torch::Tensor q12 = -1*NuSolutionTensors::cofactor(Q, {0, 2}, {0, 1}); 
	torch::Tensor q22 = NuSolutionTensors::cofactor(Q, {0, 1}, {0, 1}); 
	torch::Tensor _inter = -q22 <= 0;
	torch::Tensor _r00 = (-q00 >= 0)*_inter; 

	// =========== Parallel solutions =========== //
	torch::Tensor _para_n = torch::cat({
					Q.index({_r00, 0, 1}).view({-1, 1}), 
					Q.index({_r00, 1, 1}).view({-1, 1}), 
					(Q.index({_r00, 1, 2}) - torch::sqrt(-q00.index({_r00}))).view({-1, 1})}, 1); 

	torch::Tensor _para_p = torch::cat({
					Q.index({_r00, 0, 1}).view({-1, 1}), 
					Q.index({_r00, 1, 1}).view({-1, 1}), 
					(Q.index({_r00, 1, 2}) + torch::sqrt(-q00.index({_r00}))).view({-1, 1})}, 1); 

	Q.index_put_({_r00, 0, torch::indexing::Slice()}, _para_n); 
	Q.index_put_({_r00, 1, torch::indexing::Slice()}, _para_p); 
	
      // =========== Intersecting solutions ======== //
	_inter = (_inter == false);  
	torch::Tensor _int_n = torch::cat({
					(Q.index({_inter, 0, 1}) - torch::sqrt(-q22.index({_inter}))).view({-1, 1}), 
					Q.index({_inter, 1, 1}).view({-1, 1}),
					(-Q.index({_inter, 1, 1})*(q12.index({_inter}) / q22.index({_inter})) 
					 -Q.index({_inter, 1, 1})*(Q.index({_inter, 0, 1}) 
						 - torch::sqrt(-q22.index({_inter})))*(q02.index({_inter})/q22.index({_inter}))).view({-1, 1})}, 1); 

	torch::Tensor _int_p = torch::cat({
					(Q.index({_inter, 0, 1}) + torch::sqrt(-q22.index({_inter}))).view({-1, 1}), 
					Q.index({_inter, 1, 1}).view({-1, 1}),
					(-Q.index({_inter, 1, 1})*(q12.index({_inter}) / q22.index({_inter})) 
					 -Q.index({_inter, 1, 1})*(Q.index({_inter, 0, 1}) 
						 + torch::sqrt(-q22.index({_inter})))*(q02.index({_inter})/q22.index({_inter}))).view({-1, 1})}, 1); 
	
	Q.index_put_({_inter, 0, torch::indexing::Slice()}, _int_n); 
	Q.index_put_({_inter, 1, torch::indexing::Slice()}, _int_p); 
	
	// Swap the X and Y componets with swp.
	Q.index_put_({swp}, torch::cat({
	      		Q.index({swp, torch::indexing::Slice(), 1}).view({-1, 3, 1}), 
	      		Q.index({swp, torch::indexing::Slice(), 0}).view({-1, 3, 1}), 
	      		Q.index({swp, torch::indexing::Slice(), 2}).view({-1, 3, 1})}, 2)); 

	z0.index_put_({msk == false}, Q);

	z0 = torch::cat({
			z0.index({torch::indexing::Slice(), 0, torch::indexing::Slice()}).view({-1, 1, 3}), 
			z0.index({torch::indexing::Slice(), 1, torch::indexing::Slice()}).view({-1, 1, 3})}, 1); 
	
	// Intersection Ellipse line
	torch::Tensor V = torch::cross(z0.view({-1, 2, 1, 3}), A.view({-1, 1, 3, 3}), 3);
	V = torch::transpose(V, 2, 3); 
	V = std::get<1>(torch::linalg::eig(V));
	V = torch::real(V);
	V = torch::transpose(V, 2, 3); 
	
	torch::Tensor _t = V / (V.index({
			torch::indexing::Slice(), 
			torch::indexing::Slice(), 
			torch::indexing::Slice(), 
			2}).view({-1, 2, 3, 1})); 
	torch::Tensor d1 = torch::sum(((z0.view({-1, 2, 1, 3}))*V), {3}).pow(2);
	torch::Tensor V_ = torch::reshape(V, {-1, 2, 3, 3}); 

	_tmp = torch::matmul(V_, A.view({-1, 1, 3, 3})); 
	_tmp = torch::sum((_tmp * V_), {-1}).pow(2); 
	_tmp = (d1 + _tmp).view({-1, 2, 3});  

	std::tuple<torch::Tensor, torch::Tensor> idx = _tmp.sort(2, true);
	torch::Tensor sel = std::get<0>(idx) >= cutoff;
	torch::Tensor id = std::get<1>(idx); 

	torch::Tensor _t0 = torch::gather(_t.index({
				torch::indexing::Slice(), 
				torch::indexing::Slice(), 
				torch::indexing::Slice(), 
				0}), 2, id); 

	torch::Tensor _t1 = torch::gather(_t.index({
				torch::indexing::Slice(), 
				torch::indexing::Slice(), 
				torch::indexing::Slice(), 
				1}), 2, id); 

	torch::Tensor _t2 = torch::gather(_t.index({
				torch::indexing::Slice(), 
				torch::indexing::Slice(), 
				torch::indexing::Slice(), 
				2}), 2, id); 

	_t = torch::cat({
				_t0.view({-1, 2, 3, 1}), 
				_t1.view({-1, 2, 3, 1}), 
				_t2.view({-1, 2, 3, 1})
			}, -1); 
	
	sel = torch::cat({
				sel.view({-1, 2, 3, 1}), 
				sel.view({-1, 2, 3, 1}), 
				sel.view({-1, 2, 3, 1})
			}, -1); 
	_t.index_put_({sel}, 0);
	return _t; 
}
