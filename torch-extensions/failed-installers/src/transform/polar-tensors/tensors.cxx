#include "tensors.h"

torch::Tensor TransformTensors::PT(torch::Tensor px, torch::Tensor py)
{
	return torch::sqrt( px.pow(2) + py.pow(2) );
}

torch::Tensor TransformTensors::Phi(torch::Tensor px, torch::Tensor py)
{
	return torch::atan2( py, px ); 
}

torch::Tensor TransformTensors::_Eta(torch::Tensor pt, torch::Tensor pz)
{
	return torch::asinh( pz / pt ); 
}

torch::Tensor TransformTensors::Eta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
	torch::Tensor pt = PT(px, py); 
	return _Eta(pt, pz); 	
}

torch::Tensor TransformTensors::PtEtaPhi(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
	torch::Tensor _pt = PT(px, py).view({-1, 1}); 
	torch::Tensor _eta = _Eta(_pt, pz.view({-1, 1})).view({-1, 1}); 
	torch::Tensor _phi = Phi(px, py).view({-1, 1});
	return torch::cat({_pt, _eta, _phi}, -1);
}
