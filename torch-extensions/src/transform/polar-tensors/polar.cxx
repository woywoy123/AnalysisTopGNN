#include "polar.h"

torch::Tensor Pclip(torch::Tensor inpt, int dim)
{ 
    return inpt.index({torch::indexing::Slice(), dim}); 
}

torch::Tensor Transform::Tensors::Pt(torch::Tensor px, torch::Tensor py)
{
	return torch::sqrt( px.pow(2) + py.pow(2) ).view({-1, 1});
}

torch::Tensor Transform::Tensors::Phi(torch::Tensor px, torch::Tensor py)
{
	return torch::atan2( py, px ).view({-1, 1}); 
}

torch::Tensor Transform::Tensors::PtEta(torch::Tensor pt, torch::Tensor pz)
{
	return torch::asinh( pz / pt ).view({-1, 1}); 
}

torch::Tensor Transform::Tensors::Eta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
	torch::Tensor pt = Transform::Tensors::Pt(px, py); 
	return Transform::Tensors::PtEta(pt, pz); 	
}

torch::Tensor Transform::Tensors::PtEtaPhi(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
	torch::Tensor _pt  = Transform::Tensors::Pt(px, py); 
	torch::Tensor _eta = Transform::Tensors::PtEta(_pt, pz.view({-1, 1})); 
	torch::Tensor _phi = Transform::Tensors::Phi(px, py);
	return torch::cat({_pt, _eta, _phi}, -1);
}

torch::Tensor Transform::Tensors::PtEtaPhiE(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{
    return torch::cat({Transform::Tensors::PtEtaPhi(px, py, pz), e.view({-1, 1})}, -1);
}

torch::Tensor Transform::Tensors::Pt(torch::Tensor pmc)
{
	return Transform::Tensors::Pt(Pclip(pmc, 0), Pclip(pmc, 1));
}

torch::Tensor Transform::Tensors::Eta(torch::Tensor pmc)
{
	return Transform::Tensors::Eta(Pclip(pmc, 0), Pclip(pmc, 1), Pclip(pmc, 2));
}

torch::Tensor Transform::Tensors::Phi(torch::Tensor pmc)
{
    return Transform::Tensors::Phi(Pclip(pmc, 0), Pclip(pmc, 1));
} 

torch::Tensor Transform::Tensors::PtEtaPhi(torch::Tensor pmc)
{
    return Transform::Tensors::PtEtaPhi(Pclip(pmc, 0), Pclip(pmc, 1), Pclip(pmc, 2)); 
}

torch::Tensor Transform::Tensors::PtEtaPhiE(torch::Tensor pmc)
{
    return torch::cat({Transform::Tensors::PtEtaPhi(pmc), Pclip(pmc, 3).view({-1, 1})}, -1);
}
