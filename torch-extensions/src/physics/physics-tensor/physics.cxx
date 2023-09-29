#include "physics.h"
#include <cmath>
#include <vector>

torch::Tensor format_(std::vector<torch::Tensor> inpt)
{
    std::vector<torch::Tensor> tmp; 
    for (unsigned int i(0); i < inpt.size(); ++i)
    {
        tmp.push_back(inpt[i].view({-1, 1})); 
    }
    return torch::cat(tmp, -1); 
}

torch::Tensor Physics::Tensors::P2(torch::Tensor pmc)
{
    torch::Tensor pmc_ = pmc.index({torch::indexing::Slice(), torch::indexing::Slice(0, 3)}).clone(); 
    pmc_ = pmc_.pow(2);
    pmc_ = pmc_.sum({-1}); 
    return pmc_.view({-1, 1}); 
}

torch::Tensor Physics::Tensors::P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
    return Physics::Tensors::P2(format_({px, py, pz})); 
}

torch::Tensor Physics::Tensors::P(torch::Tensor pmc)
{
    return torch::sqrt(Physics::Tensors::P2(pmc));
}

torch::Tensor Physics::Tensors::P(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
    return Physics::Tensors::P(format_({px, py, pz})); 
}

torch::Tensor Physics::Tensors::Beta2(torch::Tensor pmc)
{
    torch::Tensor e = pmc.index({torch::indexing::Slice(), torch::indexing::Slice(3, 4)}).clone();
    return Physics::Tensors::P2(pmc)/(e.pow(2)); 
}

torch::Tensor Physics::Tensors::Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{
    return Physics::Tensors::Beta2(format_({px, py, pz, e}));  
}

torch::Tensor Physics::Tensors::Beta(torch::Tensor pmc)
{
    torch::Tensor e = pmc.index({torch::indexing::Slice(), torch::indexing::Slice(3, 4)}).clone();
    return Physics::Tensors::P(pmc)/e; 
}

torch::Tensor Physics::Tensors::Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{
    return Physics::Tensors::Beta(format_({px, py, pz, e})); 
}

torch::Tensor Physics::Tensors::M2(torch::Tensor pmc)
{
    torch::Tensor mass = pmc.index({torch::indexing::Slice(), torch::indexing::Slice(3, 4)}).clone(); 
    mass = mass.pow(2); 
    mass -= Physics::Tensors::P2(pmc); 
    return torch::relu(mass);
}

torch::Tensor Physics::Tensors::M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{
    return Physics::Tensors::M2(format_({px, py, pz, e}));     
}    

torch::Tensor Physics::Tensors::M(torch::Tensor pmc)
{
    return torch::sqrt(Physics::Tensors::M2(pmc));
}

torch::Tensor Physics::Tensors::M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{
    return Physics::Tensors::M(format_({px, py, pz, e}));     
}    

torch::Tensor Physics::Tensors::Mt2(torch::Tensor pmc)
{
    torch::Tensor pz = pmc.index({torch::indexing::Slice(), torch::indexing::Slice(2, 3)}); 
    torch::Tensor e = pmc.index({torch::indexing::Slice(), torch::indexing::Slice(3, 4)}); 
    return (torch::relu(e.pow(2) - pz.pow(2))).view({-1, 1}); 
}

torch::Tensor Physics::Tensors::Mt2(torch::Tensor pz, torch::Tensor e)
{
    return  (torch::relu(e.pow(2) - pz.pow(2))).view({-1, 1});    
}    

torch::Tensor Physics::Tensors::Mt(torch::Tensor pmc)
{
    return torch::sqrt(Physics::Tensors::Mt2(pmc)); 
}

torch::Tensor Physics::Tensors::Mt(torch::Tensor pz, torch::Tensor e)
{
    return torch::sqrt(Physics::Tensors::Mt2(pz, e));     
}

torch::Tensor Physics::Tensors::Theta(torch::Tensor pmc)
{
    torch::Tensor pz = pmc.index({torch::indexing::Slice(), torch::indexing::Slice(2, 3)}); 
    return torch::acos( pz / Physics::Tensors::P(pmc)); 
}

torch::Tensor Physics::Tensors::Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
    return torch::acos( pz.view({-1, 1}) / Physics::Tensors::P( format_({px, py, pz}) ) );  
}

torch::Tensor Physics::Tensors::DeltaR(torch::Tensor pmu1, torch::Tensor pmu2)
{
    torch::Tensor d_eta = pmu1.index({torch::indexing::Slice(), torch::indexing::Slice(1, 3)}).clone(); 
    d_eta -= pmu2.index({torch::indexing::Slice(), torch::indexing::Slice(1, 3)});    
    
    torch::Tensor d_phi = d_eta.index({torch::indexing::Slice(), torch::indexing::Slice(1, 2)}).clone(); 
    d_eta = d_eta.index({torch::indexing::Slice(), torch::indexing::Slice(0, 1)}); 

    torch::Tensor pi = M_PI*torch::ones_like(d_eta); 
    d_phi = pi - torch::abs(torch::fmod(torch::abs(d_phi), 2*pi) - pi);   
    return torch::sqrt(d_eta.pow(2) + d_phi.pow(2)); 
}

torch::Tensor Physics::Tensors::DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2)
{
    torch::Tensor d_eta = eta1 - eta2; 
    torch::Tensor d_phi = phi1 - phi2; 
    
    torch::Tensor pi = M_PI*torch::ones_like(d_eta); 
    d_phi = pi - torch::abs(torch::fmod(torch::abs(d_phi), 2*pi) - pi);   
    return torch::sqrt(d_eta.pow(2) + d_phi.pow(2)); 
}
