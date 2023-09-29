#include "cartesian.h"

torch::Tensor Cclip(torch::Tensor inpt, int dim)
{ 
    return inpt.index({torch::indexing::Slice(), dim}); 
}

torch::Tensor Transform::Tensors::Px(torch::Tensor pt, torch::Tensor phi)
{
        pt = pt.view({-1, 1});
        phi = phi.view({-1, 1}); 
        return pt * torch::cos(phi);
}

torch::Tensor Transform::Tensors::Py(torch::Tensor pt, torch::Tensor phi)
{
    pt = pt.view({-1, 1}); 
    phi = phi.view({-1, 1}); 
	return pt * torch::sin(phi);
}

torch::Tensor Transform::Tensors::Pz(torch::Tensor pt, torch::Tensor eta)
{
    pt = pt.view({-1, 1}); 
    eta = eta.view({-1, 1}); 
	return pt * torch::sinh(eta);
}

torch::Tensor Transform::Tensors::PxPyPz(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
{
	torch::Tensor _px = Transform::Tensors::Px(pt, phi);
	torch::Tensor _py = Transform::Tensors::Py(pt, phi); 
	torch::Tensor _pz = Transform::Tensors::Pz(pt, eta); 
	return torch::cat({_px, _py, _pz}, -1);
}

torch::Tensor Transform::Tensors::PxPyPzE(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
{
    return torch::cat({Transform::Tensors::PxPyPz(pt, eta, phi), e.view({-1, 1})}, -1);
}

torch::Tensor Transform::Tensors::Px(torch::Tensor pmu)
{
    torch::Tensor pt  = Cclip(pmu, 0);
    torch::Tensor phi = Cclip(pmu, 2);
    return Transform::Tensors::Px(pt, phi);  
}

torch::Tensor Transform::Tensors::Py(torch::Tensor pmu)
{
    torch::Tensor pt  = Cclip(pmu, 0); 
    torch::Tensor phi = Cclip(pmu, 2); 
    return Transform::Tensors::Py(pt, phi);
} 

torch::Tensor Transform::Tensors::Pz(torch::Tensor pmu)
{
    torch::Tensor pt  = Cclip(pmu, 0); 
    torch::Tensor eta = Cclip(pmu, 1); 
    return Transform::Tensors::Pz(pt, eta);
}

torch::Tensor Transform::Tensors::PxPyPz(torch::Tensor pmu)
{
    torch::Tensor pt  = Cclip(pmu, 0); 
    torch::Tensor eta = Cclip(pmu, 1); 
    torch::Tensor phi = Cclip(pmu, 2);  
    return Transform::Tensors::PxPyPz(pt, eta, phi);
}

torch::Tensor Transform::Tensors::PxPyPzE(torch::Tensor pmu)
{
    pmu = pmu.view({-1, 4}); 
    torch::Tensor pt  = Cclip(pmu, 0); 
    torch::Tensor eta = Cclip(pmu, 1); 
    torch::Tensor phi = Cclip(pmu, 2); 
    torch::Tensor e   = Cclip(pmu, 3).view({-1, 1}); 

    torch::Tensor _px = Transform::Tensors::Px(pt, phi);
	torch::Tensor _py = Transform::Tensors::Py(pt, phi); 
	torch::Tensor _pz = Transform::Tensors::Pz(pt, eta); 

	return torch::cat({_px, _py, _pz, e}, -1);
}
