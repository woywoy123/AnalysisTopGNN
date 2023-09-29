#include "../Headers/Tensors.h"
#include <cmath>

torch::Tensor PhysicsTensors::P2(torch::Tensor px, torch::Tensor py, torch:: Tensor pz)
{
	return (px.pow(2) + py.pow(2) + pz.pow(2)); 	
}

torch::Tensor PhysicsTensors::P(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
	return torch::sqrt(P2(px, py, pz)); 
}

torch::Tensor PhysicsTensors::Beta2(
		torch::Tensor px, torch::Tensor py, 
		torch::Tensor pz, torch::Tensor e)
{
	return P2(px, py, pz)/e.pow(2); 
}

torch::Tensor PhysicsTensors::Beta(
		torch::Tensor px, torch::Tensor py, 
		torch::Tensor pz, torch::Tensor e)
{
	return torch::sqrt(Beta2(px, py, pz, e)); 
}

torch::Tensor PhysicsTensors::M2(
		torch::Tensor px, torch::Tensor py, 
		torch::Tensor pz, torch::Tensor e)
{
	return e.pow(2) - P2(px, py, pz);
}

torch::Tensor PhysicsTensors::M(
		torch::Tensor px, torch::Tensor py, 
		torch::Tensor pz, torch::Tensor e)
{
	return torch::sqrt(torch::relu(M2(px, py, pz, e))); 	
}

torch::Tensor PhysicsTensors::Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{	
	return torch::acos(pz/P(px, py, pz)); 
}

torch::Tensor PhysicsTensors::Theta_(torch::Tensor P_, torch::Tensor pz)
{	
	return torch::acos(pz/P_); 
}

torch::Tensor PhysicsTensors::Mt2(torch::Tensor pz, torch::Tensor e)
{
	return e.pow(2) - pz.pow(2); 
}

torch::Tensor PhysicsTensors::Mt(torch::Tensor pz, torch::Tensor e)
{
	return torch::sqrt(torch::relu(Mt2(pz, e))); 
}

torch::Tensor PhysicsTensors::DeltaR(
		torch::Tensor eta1, torch::Tensor eta2, 
		torch::Tensor phi1, torch::Tensor phi2)
{
    torch::Tensor dphi = (phi1 - phi2); 
    torch::Tensor pi = torch::ones_like(phi1)*M_PI; 
    dphi = torch::fmod(torch::abs(dphi), 2*pi); 
    dphi = pi - torch::abs(dphi - pi); 
	return torch::sqrt((eta1 - eta2).pow(2) + dphi.pow(2)); 
}
