#include "../../Tensors/Headers/PhysicsTensors.h"
#include "../Headers/PhysicsFloats.h"
#include <type_traits>

torch::Tensor PhysicsFloats::ToThetaPolar(double pt, double eta, double phi, std::string device)
{
	return PhysicsTensors::ToThetaPolar(PhysicsFloats::ToTensor(pt, eta, phi, device));	
}

torch::Tensor PhysicsFloats::Mass2Polar(double pt, double eta, double phi, double e, std::string device)
{
	torch::Tensor Pmu = PhysicsFloats::ToPxPyPzE(pt, eta, phi, e, device); 
	return PhysicsTensors::Mass2Cartesian(Pmu); 	
}

torch::Tensor PhysicsFloats::MassPolar(double pt, double eta, double phi, double e, std::string device)
{
	torch::Tensor Pmu = PhysicsFloats::ToPxPyPzE(pt, eta, phi, e, device); 
	return PhysicsTensors::MassCartesian(Pmu); 	
}

torch::Tensor PhysicsFloats::P2Polar(double pt, double eta, double phi, std::string device)
{
	return PhysicsFloats::ToPx(pt, phi, device).pow(2) + 
		PhysicsFloats::ToPy(pt, phi, device).pow(2) + 
		PhysicsFloats::ToPz(pt, eta, device).pow(2);
}

torch::Tensor PhysicsFloats::PPolar(double pt, double eta, double phi, std::string device)
{
	return torch::sqrt(PhysicsFloats::P2Polar(pt, eta, phi, device)); 
}

torch::Tensor PhysicsFloats::BetaPolar(double pt, double eta, double phi, double e, std::string device)
{
	return torch::sqrt(PhysicsTensors::P2Cartesian(PhysicsFloats::ToPxPyPzE(pt, eta, phi, e, device)))/e; 
}

torch::Tensor PhysicsFloats::Beta2Polar(double pt, double eta, double phi, double e, std::string device)
{
	torch::Tensor _P2 = PhysicsTensors::P2Cartesian(PhysicsFloats::ToPxPyPzE(pt, eta, phi, e, device)); 
	return _P2/(PhysicsFloats::ToTensor(e, device)).pow(2); 
}

torch::Tensor PhysicsFloats::Rx(double angle, std::string device)
{
	return PhysicsTensors::Rx(PhysicsFloats::ToTensor(angle, device)); 
}

torch::Tensor PhysicsFloats::Ry(double angle, std::string device)
{
	return PhysicsTensors::Ry(PhysicsFloats::ToTensor(angle, device)); 
}

torch::Tensor PhysicsFloats::Rz(double angle, std::string device)
{
	return PhysicsTensors::Rz(PhysicsFloats::ToTensor(angle, device)); 
}

