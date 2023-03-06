#include "../Headers/Tensors.h"

torch::Tensor OperatorsTensors::Dot(torch::Tensor v1, torch::Tensor v2)
{
	return (v1*v2).sum({-1}, true); 
}

torch::Tensor OperatorsTensors::CosTheta(torch::Tensor v1, torch::Tensor v2)
{
	torch::Tensor v1_2 = Dot(v1, v1);
	torch::Tensor v2_2 = Dot(v2, v2);
	torch::Tensor dot = Dot(v1, v2); 
	return dot/( torch::sqrt(v1_2 * v2_2) ); 
}

torch::Tensor OperatorsTensors::_SinTheta(torch::Tensor cos)
{
	return torch::sqrt( 1 - cos.pow(2)); 
}


torch::Tensor OperatorsTensors::SinTheta(torch::Tensor v1, torch::Tensor v2)
{
	return _SinTheta(CosTheta(v1, v2)); 
}

torch::Tensor OperatorsTensors::Rx(torch::Tensor angle)
{	
	angle = angle.view({-1, 1});
	torch::Tensor cos = torch::cos(angle); 
	torch::Tensor sin = torch::sin(angle); 
	
	torch::Tensor t0 = torch::zeros_like(angle); 
	torch::Tensor t1 = torch::ones_like(angle);

	return torch::cat({t1,  t0,   t0, 
			   t0, cos, -sin, 
			   t0, sin,  cos}, -1).view({-1, 3, 3}); 
}

torch::Tensor OperatorsTensors::Ry(torch::Tensor angle)
{
	angle = angle.view({-1, 1});
	torch::Tensor cos = torch::cos(angle); 
	torch::Tensor sin = torch::sin(angle); 
	
	torch::Tensor t0 = torch::zeros_like(angle); 
	torch::Tensor t1 = torch::ones_like(angle);

	return torch::cat({cos, t0, sin, 
			    t0, t1,  t0, 
			  -sin, t0, cos}, -1).view({-1, 3, 3});
}

torch::Tensor OperatorsTensors::Rz(torch::Tensor angle)
{
	angle = angle.view({-1, 1});
	torch::Tensor cos = torch::cos(angle); 
	torch::Tensor sin = torch::sin(angle); 
	
	torch::Tensor t0 = torch::zeros_like(angle); 
	torch::Tensor t1 = torch::ones_like(angle);

	return torch::cat({cos, -sin, t0, 
			   sin,  cos, t0, 
			    t0,   t0, t1}, -1).view({-1, 3, 3}); 
}

torch::Tensor Constants::Pi_2(torch::Tensor v)
{ 
	return torch::acos( torch::zeros(v.size(0), 
				torch::TensorOptions().dtype(v.dtype()).device(v.device())).view({-1, 1})
			);
}
