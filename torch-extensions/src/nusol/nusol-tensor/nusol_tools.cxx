#include <transform/cartesian-tensors/cartesian.h>
#include <transform/polar-tensors/polar.h>
#include <physics.h>
#include <operators.h>
#include "nusol_tools.h" 

torch::TensorOptions Tooling::MakeOp(torch::Tensor x)
{
    torch::TensorOptions op = torch::TensorOptions().device(x.device()).dtype(x.dtype()); 
    return op; 
}

torch::Tensor Tooling::Pi_2(torch::Tensor x)
{
    torch::TensorOptions op = MakeOp(x); 
    const unsigned int dim_i = x.size(0); 
    torch::Tensor z = torch::zeros({dim_i, 1}, op); 
    return torch::acos(z); 
}

torch::Tensor Tooling::x0(torch::Tensor pmc, torch::Tensor _pm2, torch::Tensor mH2, torch::Tensor mL2)
{
    torch::Tensor e = pmc.index({torch::indexing::Slice(), 3}).view({-1, 1}); 
    return -(mH2 - mL2 - _pm2)/(2*e); 
}

torch::Tensor Tooling::Sigma(torch::Tensor x, torch::Tensor sigma)
{
    sigma = sigma.view({-1, 2, 2}); 
    const unsigned int dim_i = x.size(0);
    const unsigned int dim_i_ = sigma.size(0); 
    const torch::TensorOptions op = Tooling::MakeOp(x); 
    if (dim_i != dim_i_)
    {
        torch::Tensor tmp = torch::ones({dim_i, 2, 2}, op); 
        sigma = tmp * sigma[0]; 
    }
    sigma = torch::inverse(sigma); 
    sigma = torch::pad(sigma, {0, 1, 0, 1}, "constant", 0);
    sigma = torch::transpose(sigma, 1, 2);
    return sigma; 
}

torch::Tensor Tooling::MET(torch::Tensor met_xy)
{
    torch::Tensor matrix = met_xy.view({-1, 2});
    matrix = torch::pad(matrix, {0, 1, 0, 0}, "constant", 0).view({-1, 3, 1}); 
    torch::Tensor t0 = torch::zeros_like(matrix); 
    return torch::cat({t0, t0, matrix}, -1); 
}

std::map<std::string, torch::Tensor> Tooling::GetMasses(torch::Tensor L, torch::Tensor masses)
{
    const unsigned int dim_i = L.size(0);
    masses = masses.view({-1, 3}); 
    const unsigned int dim_i_ = masses.size(0); 
    if (dim_i != dim_i_)
    {
        torch::Tensor tmp = torch::ones({dim_i, 3}, MakeOp(masses)); 
        masses = tmp*(masses[0]); 
    }
    std::map<std::string, torch::Tensor> out; 
    out["W2"] = torch::pow(masses.index({torch::indexing::Slice(), 0}), 2).view({dim_i, 1});  
    out["T2"] = torch::pow(masses.index({torch::indexing::Slice(), 1}), 2).view({dim_i, 1});  
    out["N2"] = torch::pow(masses.index({torch::indexing::Slice(), 2}), 2).view({dim_i, 1});  
    return out; 
}

torch::Tensor Tooling::Rotation(torch::Tensor pmc_b, torch::Tensor pmc_mu, torch::Tensor base)
{
    torch::Tensor pmc_b3  = pmc_b.index( {torch::indexing::Slice(), torch::indexing::Slice(0, 3)}); 
    torch::Tensor pmc_mu3 = pmc_mu.index({torch::indexing::Slice(), torch::indexing::Slice(0, 3)}); 

    torch::Tensor muphi = Transform::Tensors::Phi(pmc_mu); 
    torch::Tensor theta = Physics::Tensors::Theta(pmc_mu); 

    torch::Tensor Rz = Operators::Tensors::Rz(-muphi); 
    torch::Tensor Ry = Operators::Tensors::Ry(Tooling::Pi_2(theta) - theta); 

    torch::Tensor Rx = torch::matmul(Rz, pmc_b3.view({-1, 3, 1}));
    Rx = torch::matmul(Ry, Rx.view({-1, 3, 1})); 
    Rx = -torch::atan2(
            Rx.index({torch::indexing::Slice(), 2}), 
            Rx.index({torch::indexing::Slice(), 1})
    ).view({-1, 1}); 

    Rx = Operators::Tensors::Rx(Rx); 
    Rx = torch::transpose(Rx, 1, 2); 
    Ry = torch::transpose(Ry, 1, 2); 
    Rz = torch::transpose(Rz, 1, 2); 

    return torch::matmul(torch::matmul(Rz, torch::matmul(Ry, Rx)), base); 
}

torch::Tensor Tooling::Shape(torch::Tensor x, std::vector<int> diag)
{
    const torch::TensorOptions op = Tooling::MakeOp(x);
    torch::Tensor shape = torch::diag(torch::tensor(diag, op)).view({-1, 3, 3}); 
    torch::Tensor ones = torch::ones({x.size(0), 3, 3}, op); 
    shape = (ones*shape).view({-1, 3, 3}); 
    return shape; 
}

torch::Tensor Tooling::H_perp(torch::Tensor base)
{
    torch::Tensor H = base.clone(); 
    H.index_put_({torch::indexing::Slice(), 2, torch::indexing::Slice()}, 0); 
    H.index_put_({torch::indexing::Slice(), 2, 2}, 1);  
    return H; 
}

torch::Tensor Tooling::N(torch::Tensor hperp)
{
    torch::Tensor H = torch::inverse(hperp.clone()); 
    torch::Tensor H_T = torch::transpose(H, 1, 2);    
    H_T = torch::matmul(H_T, Tooling::Shape(H_T, {1, 1, -1})); 
    return torch::matmul(H_T, H); 
}

torch::Tensor Tooling::HorizontalVertical(torch::Tensor G)
{
    torch::Tensor G01 = G.index({torch::indexing::Slice(), 0, 1}).view({-1, 1, 1}); 
    torch::Tensor G02 = G.index({torch::indexing::Slice(), 0, 2}).view({-1, 1, 1}); 
    torch::Tensor G12 = G.index({torch::indexing::Slice(), 1, 2}).view({-1, 1, 1}); 
    torch::Tensor t0 = zeros_like(G01); 
    return torch::cat({ G01, t0, G12, t0, G01, G02 - G12, t0, t0, t0}, -1).view({-1, 3, 3}); 
}

torch::Tensor Tooling::Parallel(torch::Tensor G, torch::Tensor CoF)
{
    torch::Tensor g00 = -CoF.index({torch::indexing::Slice(), 0, 0}); 
    torch::Tensor G00 = G.index({torch::indexing::Slice(), 0, 0}); 
    torch::Tensor G01 = G.index({torch::indexing::Slice(), 0, 1}); 
    torch::Tensor G11 = G.index({torch::indexing::Slice(), 1, 1});
    torch::Tensor G12 = G.index({torch::indexing::Slice(), 1, 2});
    torch::Tensor t0 = torch::zeros_like(G12); 
    torch::Tensor G_ = torch::zeros_like(G); 
    std::vector<signed long> dims = {-1, 1, 1};  

    // ----- Populate cases where g00 is 0
    torch::Tensor y0 = g00 == 0.; 	
    G_.index_put_({y0}, torch::cat({
                G01.index({y0}).view(dims), G11.index({y0}).view(dims), G12.index({y0}).view(dims), 
                 t0.index({y0}).view(dims),  t0.index({y0}).view(dims),  t0.index({y0}).view(dims), 
                 t0.index({y0}).view(dims),  t0.index({y0}).view(dims),  t0.index({y0}).view(dims)
    }, -1).view({-1, 3, 3})); 
    
    // ----- Populate cases where -g00 > 0
    torch::Tensor yr = g00 > 0.; 
    G_.index_put_({yr}, torch::cat({
                G01.index({yr}).view(dims), 
                G11.index({yr}).view(dims), 
                (G12.index({yr}) - torch::sqrt(g00.index({yr}))).view(dims),
                
                G01.index({yr}).view(dims), 
                G11.index({yr}).view(dims), 
                (G12.index({yr}) + torch::sqrt(g00.index({yr}))).view(dims),
                
                torch::cat({t0.index({yr}), t0.index({yr}), t0.index({yr})}, -1).view({-1, 1, 3})
    }, -1).view({-1, 3, 3})); 
    return G_; 
}

torch::Tensor Tooling::Intersecting(torch::Tensor G, torch::Tensor g22, torch::Tensor CoF)
{
    std::vector<signed long> dim11 = {-1, 1, 1}; 
    std::vector<signed long> dim13 = {-1, 1, 3};

    torch::Tensor g02 = CoF.index({torch::indexing::Slice(), 0, 2}); 
    torch::Tensor g12 = CoF.index({torch::indexing::Slice(), 1, 2}); 
    
    torch::Tensor x0 = (g02 / g22); 
    torch::Tensor y0 = (g12 / g22); 
    torch::Tensor G11 = G.index({torch::indexing::Slice(), 1, 1}); 
    torch::Tensor G01 = G.index({torch::indexing::Slice(), 0, 1}); 
    torch::Tensor t0 = torch::zeros_like(G01); 

    // Case 1: -g22 < 0 - No Solution  - ignore
    torch::Tensor G_ = torch::zeros_like(G);

    // Case 2: -g22 == 0 - One Solution 
    torch::Tensor _s1 = -g22 == 0.; 
    torch::Tensor _s1_s = _s1.sum(-1);  
    
    // Case 3; -g22 > 0 - Two Solutions 
    torch::Tensor _s2 = -g22 > 0.;  
    torch::Tensor _s2_s = _s2.sum(-1);

    if (_s1_s.item<int>() > 0)
    {
        // ---------- Case 2 ----------- //   
        G_.index_put_({_s1}, torch::cat({
                G01.index({_s1}).view(dim11), 
                G11.index({_s1}).view(dim11), 
                ((-G11.index({_s1}) * y0.index({_s1})) - (G01.index({_s1}) * x0.index({_s1}))).view(dim11), 

                torch::cat({t0.index({_s1}), t0.index({_s1}), t0.index({_s1})}, -1).view(dim13), 
                torch::cat({t0.index({_s1}), t0.index({_s1}), t0.index({_s1})}, -1).view(dim13)
        }, -1).view({-1, 3, 3})); 
    }
    if (_s2_s.item<int>() > 0)
    {
        // ---------- Case 3 ----------- //   
        torch::Tensor _s = torch::sqrt(-g22.index({_s2})); 
        G_.index_put_({_s2}, torch::cat({
                // Solution 1
                (G01.index({_s2}) - _s).view(dim11), 
                (G11.index({_s2})).view(dim11), 
                (-G11.index({_s2}) * y0.index({_s2}) - (G01.index({_s2}) - _s) * x0.index({_s2})).view(dim11), 

                // Solution 2
                (G01.index({_s2}) + _s).view(dim11), 
                (G11.index({_s2})).view(dim11), 
                (-G11.index({_s2}) * y0.index({_s2}) - (G01.index({_s2}) + _s) * x0.index({_s2})).view(dim11), 
                torch::cat({t0.index({_s2}), t0.index({_s2}), t0.index({_s2})}, -1).view(dim13) // Zeros 
        }, -1).view({-1, 3, 3})); 
    }
    return G_; 
}

std::map<std::string, torch::Tensor> Tooling::_convert(torch::Tensor met_phi)
{   
    torch::Tensor met = met_phi.index({torch::indexing::Slice(), 0}); 
    torch::Tensor phi = met_phi.index({torch::indexing::Slice(), 1}); 
    torch::Tensor met_x = Transform::Tensors::Px(met, phi);
    torch::Tensor met_y = Transform::Tensors::Py(met, phi);

    std::map<std::string, torch::Tensor> out;
    out["met_xy"] = torch::cat({met_x, met_y}, -1); 
    return out; 
}

std::map<std::string, torch::Tensor> Tooling::_convert(torch::Tensor pmu1, torch::Tensor pmu2)
{  
    const unsigned int dim_i = pmu1.size(0); 
    torch::Tensor com = torch::cat({pmu1, pmu2}, 0); 
    com = Transform::Tensors::PxPyPzE(com);

    std::map<std::string, torch::Tensor> out;
    out["pmc1"] = com.index({torch::indexing::Slice(0, dim_i)}); 
    out["pmc2"] = com.index({torch::indexing::Slice(dim_i, dim_i*2)}); 
    return out; 
}

torch::Tensor Tooling::_format(std::vector<torch::Tensor> v)
{  
    std::vector<torch::Tensor> out; 
    for (torch::Tensor i : v)
    {
        out.push_back(i.view({-1, 1})); 
    }
    return torch::cat(out, -1); 
}



