#include <operators.h>
#include <physics.h>
#include "nusol.h"

torch::Tensor NuSol::Tensor::BaseMatrix(torch::Tensor pmc_b, torch::Tensor pmc_mu, torch::Tensor masses)
{
    pmc_b  = pmc_b.view( {-1, 4}); 
    pmc_mu = pmc_mu.view({-1, 4}); 
    std::map<std::string, torch::Tensor> mass = Tooling::GetMasses(pmc_b, masses); 
    const torch::TensorOptions op = Tooling::MakeOp(pmc_b); 
    const unsigned int dim_i = pmc_b.size(0); 

    torch::Tensor bB   = Physics::Tensors::Beta(pmc_b); 
    torch::Tensor muB  = Physics::Tensors::Beta(pmc_mu); 
    torch::Tensor muB2 = Physics::Tensors::Beta2(pmc_mu); 
    torch::Tensor muP  = Physics::Tensors::P(pmc_mu); 

    torch::Tensor x0p = Tooling::x0(pmc_b , Physics::Tensors::M2(pmc_b ), mass["T2"], mass["W2"]); 
    torch::Tensor x0  = Tooling::x0(pmc_mu, Physics::Tensors::M2(pmc_mu), mass["W2"], mass["N2"]); 
  
    torch::Tensor pmc_b3  = pmc_b.index( {torch::indexing::Slice(), torch::indexing::Slice(0, 3)}); 
    torch::Tensor pmc_mu3 = pmc_mu.index({torch::indexing::Slice(), torch::indexing::Slice(0, 3)}); 

    torch::Tensor c_ = Operators::Tensors::CosTheta(pmc_b3, pmc_mu3); 
    torch::Tensor s_ = Operators::Tensors::SinTheta(pmc_b3, pmc_mu3);
    
    torch::Tensor tmp_ = muB / bB; 
    torch::Tensor w_ = ( - tmp_ - c_ ) / s_; 
    torch::Tensor w = ( tmp_ - c_ ) / s_; 
    
    torch::Tensor O2 = w.pow(2) + 1 - muB2;
    torch::Tensor e2 = (mass["W2"] - mass["N2"]) * ( 1 - muB2 ); 
    
    torch::Tensor Sx = (x0 * muB - muP * ( 1 - muB2 )) / muB2; 
    torch::Tensor Sy = ( (x0p / bB) - c_ * Sx ) / s_; 
    
    tmp_ = Sx + w*Sy; 
    torch::Tensor x1 = Sx - tmp_ / O2; 
    torch::Tensor y1 = Sy - tmp_ * (w / O2); 
    torch::Tensor Z = torch::sqrt(torch::relu(x1.pow(2) * O2 - ( Sy - w*Sx ).pow(2) - ( mass["W2"] - x0.pow(2) - e2 ))); 

    torch::Tensor O = torch::sqrt(O2);
    torch::Tensor _0 = torch::zeros({dim_i, 1}, op);
    return torch::cat({ Z / O, _0, x1 - muP, (w*Z)/O, _0, y1, _0, Z, _0}, -1).view({dim_i, 3, 3}); 
}

std::tuple<torch::Tensor, torch::Tensor> NuSol::Tensor::Intersection(torch::Tensor A, torch::Tensor B, const double null)
{
    const torch::TensorOptions op = Tooling::MakeOp(A);
    const unsigned int dim_i = A.size(0);
    std::vector<signed long> dim11 = {-1, 1, 1}; 
    std::vector<signed long> dim13 = {-1, 1, 3}; 
    std::vector<signed long> dim31 = {-1, 3, 1}; 
    std::vector<signed long> dim313 = {-1, 3, 1, 3}; 
    std::vector<signed long> dim133 = {-1, 1, 3, 3}; 
    std::vector<signed long> dim331 = {-1, 3, 3, 1}; 
    std::vector<signed long> dim333 = {-1, 3, 3, 3}; 
    A = A.clone(); 
    B = B.clone(); 

    torch::Tensor detA = torch::abs(torch::det(A)); 
    torch::Tensor detB = torch::abs(torch::det(B)); 

    // Perform the variable swaps 
    torch::Tensor swp = detB > detA;
    torch::Tensor _tmp = B.index({swp}); 
    B.index_put_({swp}, A.index({swp})); 
    A.index_put_({swp}, _tmp);
    
    // Find the non imaginary eigenvalue solutions
    _tmp = torch::linalg::eigvals(torch::inverse(A).matmul(B)); 
    torch::Tensor _r = torch::real(_tmp); 
    torch::Tensor msk = torch::isreal(_tmp)*torch::arange(3, 0, -1, op); 
    msk = torch::argmax(msk, -1, true); 
    _r = torch::gather(_r, 1, msk).view({-1, 1, 1}); 
    torch::Tensor G = B - _r*A;
    
    // Get the diagonals of the matrix
    torch::Tensor G00 = G.index({torch::indexing::Slice(), 0, 0}); 
    torch::Tensor G11 = G.index({torch::indexing::Slice(), 1, 1}); 
    
    // ----- Numerical Stability part ----- // 
swp = torch::abs(G00) > torch::abs(G11); 
    G.index_put_({swp}, torch::cat({
    			G.index({swp, 1, torch::indexing::Slice()}).view(dim13), 
    			G.index({swp, 0, torch::indexing::Slice()}).view(dim13), 
    			G.index({swp, 2, torch::indexing::Slice()}).view(dim13)}, 1)); 

    G.index_put_({swp}, torch::cat({
    			G.index({swp, torch::indexing::Slice(), 1}).view(dim31), 
    			G.index({swp, torch::indexing::Slice(), 0}).view(dim31), 
    			G.index({swp, torch::indexing::Slice(), 2}).view(dim31)}, 2)); 

    G = G/(G.index({torch::indexing::Slice(), 1, 1}).view({-1, 1, 1})); 
    
    torch::Tensor CoF = Operators::Tensors::CoFactors(G);
    torch::Tensor g22 = CoF.index({torch::indexing::Slice(), 2, 2}); 
    torch::Tensor _out = zeros_like(G); 
    
    detA = detA == 0; 
    torch::Tensor G00_G11 = ( G00 == 0 ) * (G11 == 0); 
    torch::Tensor g22__   = (-g22 <= 0.) * (G00_G11 == false); 	
    torch::Tensor g22_    = (-g22 >  0.) * (G00_G11 == false); 

    // 1. ----- Case where the solutions are Horizontal and Vertical ----- //
torch::Tensor SolG_HV = Tooling::HorizontalVertical(G.index({G00_G11}));
    
    // 2. ------ Case where the solutions are parallel 
    torch::Tensor SolG_Para = Tooling::Parallel(G.index({g22__}), CoF.index({g22__})); 
    
    // 3. ------- Case where the solutions are intersecting 
    torch::Tensor SolG_Int = Tooling::Intersecting(G.index({g22_}), g22.index({g22_}), CoF.index({g22_})); 

    _out.index_put_({G00_G11}, SolG_HV); 
    _out.index_put_({g22__  }, SolG_Para);
    _out.index_put_({g22_   }, SolG_Int);
    _out.index_put_({detA   }, 0); 
    
    // Swap the XY if they were swapped previously 	
    _tmp = torch::cat({
    		_out.index({swp, torch::indexing::Slice(), 1}).view(dim31), 
    		_out.index({swp, torch::indexing::Slice(), 0}).view(dim31), 
    		_out.index({swp, torch::indexing::Slice(), 2}).view(dim31)}, 2);
    _out.index_put_({swp}, _tmp);

    // ------ Intersection of line with Ellipse ------ //
    torch::Tensor _t, d1, V, V_, diag; 
    V = torch::cross(_out.view(dim313), A.view(dim133), 3); 
    V = torch::transpose(V, 2, 3); 
    V = std::get<1>(torch::linalg::eig(V));
    V = torch::real(V);
    V = torch::transpose(V, 2, 3); 
    
    _t = V / (V.index({
                torch::indexing::Slice(), 
    		torch::indexing::Slice(), 
    		torch::indexing::Slice(), 2}).view(dim331)); 
    
    d1 = torch::sum(((_out.view(dim313))*V), 3).pow(2);
    V_ = torch::reshape(V, dim333); 
    
    // ------- Neutrino Solution ------ //
    _t = _t.view({dim_i, -1, 3});  
    _t = torch::nan_to_num(_t, 0, 0);

    diag = torch::matmul(V_, A.view(dim133)); 
    diag = torch::sum((diag * V_), {-1}).pow(2); 
    diag = (d1 + diag).view({dim_i, -1});   
    
    // ------- Remove false solutions ------ //
    torch::Tensor t0_, t1_, t2_;  
    t0_ = _t.index({torch::indexing::Slice(), torch::indexing::Slice(), 0}).view({dim_i, -1});  
    t1_ = _t.index({torch::indexing::Slice(), torch::indexing::Slice(), 1}).view({dim_i, -1});     
    t2_ = _t.index({torch::indexing::Slice(), torch::indexing::Slice(), 2}).view({dim_i, -1}); 
    detB = ((t0_.view({dim_i, -1, 1}) == 0) * (t1_.view({dim_i, -1, 1}) == 0)).view({dim_i, -1}); 

    t2_.index_put_({detB}, 0);
    diag.index_put_({detA}, -1); 
    diag.index_put_({detB}, -1); 
    diag.index_put_({diag > null}, -1); 
    
    // ------- Do the Sorting ------ //
    torch::Tensor id = std::get<1>(diag.sort(-1, false)); 
    t0_ = torch::gather(t0_, -1, id).view({dim_i, -1, 1}); 
    t1_ = torch::gather(t1_, -1, id).view({dim_i, -1, 1}); 
    t2_ = torch::gather(t2_, -1, id).view({dim_i, -1, 1}); 
    _t = torch::cat({t0_, t1_, t2_}, -1); 
    diag = torch::gather(diag, 1, id);
   
    int max_len = diag.size(-1) - torch::max((diag != -1).sum(-1)).item<int>(); 
    _t = _t.index({
            torch::indexing::Slice(), 
            torch::indexing::Slice(max_len, torch::indexing::None), 
            torch::indexing::Slice()}); 

    diag = diag.index({
            torch::indexing::Slice(), 
            torch::indexing::Slice(max_len, torch::indexing::None)}); 

    return {_t, diag};  
}

std::map<std::string, torch::Tensor> NuSol::Tensor::Nu(
        torch::Tensor pmc_b, torch::Tensor pmc_mu, 
        torch::Tensor met_xy, torch::Tensor masses, torch::Tensor sigma)
{
    
    // Base matrix - the Analytical solutions and constants
    torch::Tensor base = NuSol::Tensor::BaseMatrix(pmc_b, pmc_mu, masses); 
    const torch::Tensor H_base = Tooling::Rotation(pmc_b, pmc_mu, base);
    const torch::Tensor Pi2 = Tooling::Pi_2(base); 
    torch::Tensor Derivative = Operators::Tensors::Rz(Pi2); 
    Derivative = Derivative.matmul(Tooling::Shape(Pi2, {1, 1, 0})); 

    // Invert the input sigma matrix 
    sigma = Tooling::Sigma(met_xy, sigma); 
   
    // ------- Convert missing energy matrix into tensor ----- //
    met_xy = Tooling::MET(met_xy); 

    // ------- create ellipse ------- //
    torch::Tensor dNu, X_, M_; 
    dNu = met_xy - H_base; 
    X_ = torch::matmul(torch::transpose(dNu, 1, 2), sigma); 
    X_ = torch::matmul(X_, dNu).view({-1, 3, 3}); 
    M_ = X_.matmul(Derivative); 
    M_ = M_ + torch::transpose(M_, 1, 2);  
    
    std::map<std::string, torch::Tensor> output; 
    output["M"] = M_;
    output["H"] = H_base; 
    output["X"] = X_; 
    return output; 
}

std::map<std::string, torch::Tensor> NuSol::Tensor::Nu(
        torch::Tensor pmc_b, torch::Tensor pmc_mu, torch::Tensor met_xy, 
        torch::Tensor masses, torch::Tensor sigma, const double null)
{
    torch::Tensor v, chi2; 
    std::map<std::string, torch::Tensor> _Nu, output; 
    std::tuple<torch::Tensor, torch::Tensor> sols; 
    const unsigned int dim_i = met_xy.size(0); 

    _Nu = NuSol::Tensor::Nu(pmc_b, pmc_mu, met_xy, masses, sigma); 
    torch::Tensor M = _Nu["M"]; 
    torch::Tensor H = _Nu["H"]; 
    torch::Tensor X = _Nu["X"]; 

    sols = NuSol::Tensor::Intersection(M, Tooling::Shape(met_xy, {1, 1, -1}), null); 
    v = std::get<0>(sols).view({dim_i, -1, 1, 3}); 

    torch::Tensor diag = std::get<1>(sols); 
    chi2 = (v * X.view({dim_i, 1, 3, 3})).sum({-1}); 
    chi2 = chi2.view({dim_i, -1, 3})*v.view({dim_i, -1, 3}); 
    chi2 = chi2.sum(-1); 

    v = (H.view({dim_i, 1, 3, 3})*v).sum(-1);
    
    torch::Tensor t0_, t1_, t2_;  
    t0_ = v.index({torch::indexing::Slice(), torch::indexing::Slice(), 0}).view({dim_i, -1});  
    t1_ = v.index({torch::indexing::Slice(), torch::indexing::Slice(), 1}).view({dim_i, -1});     
    t2_ = v.index({torch::indexing::Slice(), torch::indexing::Slice(), 2}).view({dim_i, -1}); 

    // ------- Do the Sorting ------ //
    torch::Tensor id = std::get<1>(chi2.sort(-1, false)); 
    t0_ = torch::gather(t0_, -1, id).view({dim_i, -1, 1}); 
    t1_ = torch::gather(t1_, -1, id).view({dim_i, -1, 1}); 
    t2_ = torch::gather(t2_, -1, id).view({dim_i, -1, 1}); 
    v = torch::cat({t0_, t1_, t2_}, -1); 
    chi2 = torch::gather(diag, 1, id);

    output["NuVec"] = v; 
    output["chi2"] = chi2;

    return output; 
}

std::map<std::string, torch::Tensor> NuSol::Tensor::NuNu(
        torch::Tensor pmc_b1, torch::Tensor pmc_b2, 
        torch::Tensor pmc_l1, torch::Tensor pmc_l2, 
        torch::Tensor met_xy, torch::Tensor masses, const double null)
{
    torch::Tensor H1, H2, H1_perp, H2_perp, N1, N2, S, n_, none;
    torch::Tensor zero, _v, __v, _d; 
    const torch::TensorOptions op = Tooling::MakeOp(met_xy); 

    std::map<std::string, torch::Tensor> output; 
    std::tuple<torch::Tensor, torch::Tensor> sols; 

    // ---------------- Prepare all needed matrices ----------------- //
    H1 = NuSol::Tensor::BaseMatrix(pmc_b1, pmc_l1, masses); 
    H2 = NuSol::Tensor::BaseMatrix(pmc_b2, pmc_l2, masses);

    // --- protection against non-invertible matrices --- //
    none =  (torch::det(H1) == 0);  
    none += (torch::det(H2) == 0);
    none = none == 0; 
    output["NoSols"] = none; 
    const unsigned int dim_i = met_xy.index({none}).size(0); 

    if (dim_i == 0)
    { 
        output["n_"]      = torch::zeros({1, 3}, op); 
        output["NuVec_1"] = torch::zeros({1, 3}, op); 
        output["NuVec_2"] = torch::zeros({1, 3}, op);        
        output["H_perp_1"] = H1; 
        output["H_perp_2"] = H2;
        return output; 
    }
    
    H1 = Tooling::Rotation(pmc_b1.index({none}), pmc_l1.index({none}), H1.index({none})); 
    H2 = Tooling::Rotation(pmc_b2.index({none}), pmc_l2.index({none}), H2.index({none})); 
 
    H1_perp = Tooling::H_perp(H1); 
    H2_perp = Tooling::H_perp(H2); 
      
    N1 = Tooling::N(H1_perp); 
    N2 = Tooling::N(H2_perp); 

    S = Tooling::MET(met_xy.index({none})) - Tooling::Shape(met_xy.index({none}), {1, 1, -1});  
    n_ = torch::matmul(torch::matmul(S.transpose(1, 2), N2), S); 
    
    // ---------------- Start Algorithm ----------------- //
    sols = NuSol::Tensor::Intersection(N1, n_, null); 
    torch::Tensor d = std::get<1>(sols); 
    torch::Tensor v = std::get<0>(sols).view({dim_i, -1, 1, 3}); 
    torch::Tensor v_ = torch::sum(S.view({dim_i, 1, 3, 3}) * v, -1).view({dim_i, -1, 1, 3}); 

    torch::Tensor K1 = torch::matmul(H1, torch::inverse(H1_perp)).view({dim_i, 1, 3, 3});
    torch::Tensor K2 = torch::matmul(H2, torch::inverse(H2_perp)).view({dim_i, 1, 3, 3});

    v  = (K1 * v).sum(-1);
    v_ = (K2 * v_).sum(-1);

    unsigned int dim_j  = v.size(1); 
    unsigned int dim_k  = v.size(2); 
    unsigned int dim_i_ = none.size(0); 
    
    zero = torch::zeros({dim_i_, dim_j, dim_k}, op); 
    _d = torch::zeros({dim_i_, dim_j}, op); 
    _d.index_put_({none}, d); 
    
    _v = zero.clone(); 
    _v.index_put_({none}, v); 

    __v = zero.clone(); 
    __v.index_put_({none}, v_); 
    
    output["NuVec_1"] = _v;  
    output["NuVec_2"] = __v; 
    output["diagonal"] = _d; 

    output["n_"] = n_; 
    output["H_perp_1"] = H1_perp; 
    output["H_perp_2"] = H2_perp; 

    return output; 
}

// -------------------- Interfaces ------------------------- //
std::map<std::string, torch::Tensor> NuSol::Tensor::Polar::Nu(
        torch::Tensor pmu_b, torch::Tensor pmu_mu, 
        torch::Tensor met_phi, torch::Tensor masses, 
        torch::Tensor sigma, const double null)
{
    std::map<std::string, torch::Tensor> met = Tooling::_convert(met_phi); 
    std::map<std::string, torch::Tensor> pmc = Tooling::_convert(pmu_b, pmu_mu); 

    return NuSol::Tensor::Nu(pmc["pmc1"], pmc["pmc2"], met["met_xy"], masses, sigma, null);
}

std::map<std::string, torch::Tensor> NuSol::Tensor::Polar::Nu(
        torch::Tensor pt_b, torch::Tensor eta_b, torch::Tensor phi_b, torch::Tensor e_b, 
        torch::Tensor pt_mu, torch::Tensor eta_mu, torch::Tensor phi_mu, torch::Tensor e_mu, 
        torch::Tensor met, torch::Tensor phi, torch::Tensor masses, 
        torch::Tensor sigma, const double null)
{
    torch::Tensor pmu_b  = Tooling::_format({pt_b, eta_b, phi_b, e_b}); 
    torch::Tensor pmu_mu = Tooling::_format({pt_mu, eta_mu, phi_mu, e_mu}); 
    torch::Tensor met_   = Tooling::_format({met, phi}); 
    
    std::map<std::string, torch::Tensor> pmc  = Tooling::_convert(pmu_b, pmu_mu); 
    std::map<std::string, torch::Tensor> _met = Tooling::_convert(met_);
    return NuSol::Tensor::Nu(pmc["pmc1"], pmc["pmc2"], _met["met_xy"], masses, sigma, null);
}

std::map<std::string, torch::Tensor> NuSol::Tensor::Cartesian::Nu(
        torch::Tensor pmc_b, torch::Tensor pmc_mu, 
        torch::Tensor met_xy, torch::Tensor masses, 
        torch::Tensor sigma, const double null)
{
    return NuSol::Tensor::Nu(pmc_b, pmc_mu, met_xy, masses, sigma, null);
}

std::map<std::string, torch::Tensor> NuSol::Tensor::Cartesian::Nu(
        torch::Tensor px_b, torch::Tensor py_b, torch::Tensor pz_b, torch::Tensor e_b, 
        torch::Tensor px_mu, torch::Tensor py_mu, torch::Tensor pz_mu, torch::Tensor e_mu, 
        torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, 
        torch::Tensor sigma, const double null)
{
    torch::Tensor pmc_b  = Tooling::_format({px_b, py_b, pz_b, e_b}); 
    torch::Tensor pmc_mu = Tooling::_format({px_mu, py_mu, pz_mu, e_mu}); 
    torch::Tensor met_   = Tooling::_format({metx, mety}); 
    
    return NuSol::Tensor::Nu(pmc_b, pmc_mu, met_, masses, sigma, null);
}

std::map<std::string, torch::Tensor> NuSol::Tensor::Polar::NuNu(
        torch::Tensor pmu_b1 , torch::Tensor pmu_b2, 
        torch::Tensor pmu_mu1, torch::Tensor pmu_mu2, 
        torch::Tensor met_phi, torch::Tensor masses, 
        const double null)
{
    std::map<std::string, torch::Tensor> met    = Tooling::_convert(met_phi); 
    std::map<std::string, torch::Tensor> pmc_b  = Tooling::_convert(pmu_b1, pmu_b2); 
    std::map<std::string, torch::Tensor> pmc_mu = Tooling::_convert(pmu_mu1, pmu_mu2); 

    return NuSol::Tensor::NuNu(pmc_b["pmc1"], pmc_b["pmc2"], pmc_mu["pmc1"], pmc_mu["pmc2"], met["met_xy"], masses, null);
}

std::map<std::string, torch::Tensor> NuSol::Tensor::Polar::NuNu(
        torch::Tensor pt_b1, torch::Tensor eta_b1, torch::Tensor phi_b1, torch::Tensor e_b1, 
        torch::Tensor pt_b2, torch::Tensor eta_b2, torch::Tensor phi_b2, torch::Tensor e_b2, 

        torch::Tensor pt_mu1, torch::Tensor eta_mu1, torch::Tensor phi_mu1, torch::Tensor e_mu1, 
        torch::Tensor pt_mu2, torch::Tensor eta_mu2, torch::Tensor phi_mu2, torch::Tensor e_mu2, 

        torch::Tensor met, torch::Tensor phi, 
        torch::Tensor masses, const double null)
{
    torch::Tensor pmu_b1 = Tooling::_format({pt_b1, eta_b1, phi_b1, e_b1});
    torch::Tensor pmu_b2 = Tooling::_format({pt_b2, eta_b2, phi_b2, e_b2});

    torch::Tensor pmu_mu1 = Tooling::_format({pt_mu1, eta_mu1, phi_mu1, e_mu1});
    torch::Tensor pmu_mu2 = Tooling::_format({pt_mu2, eta_mu2, phi_mu2, e_mu2});

    std::map<std::string, torch::Tensor> _met   = Tooling::_convert(Tooling::_format({met, phi}));  
    std::map<std::string, torch::Tensor> pmc_b  = Tooling::_convert(pmu_b1 , pmu_b2); 
    std::map<std::string, torch::Tensor> pmc_mu = Tooling::_convert(pmu_mu1, pmu_mu2); 

    return NuSol::Tensor::NuNu(pmc_b["pmc1"], pmc_b["pmc2"], pmc_mu["pmc1"], pmc_mu["pmc2"], _met["met_xy"], masses, null);
}

std::map<std::string, torch::Tensor> NuSol::Tensor::Cartesian::NuNu(
        torch::Tensor pmc_b1, torch::Tensor pmc_b2, 
        torch::Tensor pmc_mu1, torch::Tensor pmc_mu2,
        torch::Tensor met_xy, torch::Tensor masses, const double null)
{
    return NuSol::Tensor::NuNu(pmc_b1, pmc_b2, pmc_mu1, pmc_mu2, met_xy, masses, null);
}

std::map<std::string, torch::Tensor> NuSol::Tensor::Cartesian::NuNu(
        torch::Tensor px_b1, torch::Tensor py_b1, torch::Tensor pz_b1, torch::Tensor e_b1, 
        torch::Tensor px_b2, torch::Tensor py_b2, torch::Tensor pz_b2, torch::Tensor e_b2, 

        torch::Tensor px_mu1, torch::Tensor py_mu1, torch::Tensor pz_mu1, torch::Tensor e_mu1, 
        torch::Tensor px_mu2, torch::Tensor py_mu2, torch::Tensor pz_mu2, torch::Tensor e_mu2, 

        torch::Tensor metx, torch::Tensor mety, torch::Tensor masses, const double null)
{
    torch::Tensor pmc_b1  = Tooling::_format({px_b1, py_b1, pz_b1, e_b1}); 
    torch::Tensor pmc_b2  = Tooling::_format({px_b2, py_b2, pz_b2, e_b2}); 
    torch::Tensor pmc_mu1 = Tooling::_format({px_mu1, py_mu1, pz_mu1, e_mu1}); 
    torch::Tensor pmc_mu2 = Tooling::_format({px_mu2, py_mu2, pz_mu2, e_mu2}); 
    torch::Tensor met_    = Tooling::_format({metx, mety}); 
    
    return NuSol::Tensor::NuNu(pmc_b1, pmc_b2, pmc_mu1, pmc_mu2, met_, masses, null);
}
