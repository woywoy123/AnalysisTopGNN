#include "../Headers/PhysicsTensors.h"

torch::Tensor PhysicsTensors::ToThetaPolar(torch::Tensor Vector)
{
	return PhysicsTensors::ToThetaCartesian(PhysicsTensors::ToPxPyPz(Vector)); 
}

torch::Tensor PhysicsTensors::Mass2Polar(torch::Tensor Polar )
{
	torch::Tensor Pmu = PhysicsTensors::ToPxPyPzE(Polar); 
	return PhysicsTensors::Mass2Cartesian(Pmu); 
}

torch::Tensor PhysicsTensors::MassPolar(torch::Tensor Polar)
{
	return PhysicsTensors::Mass2Polar(Polar).sqrt(); 
}

torch::Tensor PhysicsTensors::BetaPolar(torch::Tensor Vector)
{
	return PhysicsTensors::BetaCartesian(PhysicsTensors::ToPxPyPzE(Vector));
}

torch::Tensor PhysicsTensors::Beta2Polar(torch::Tensor Vector)
{
	return PhysicsTensors::Beta2Cartesian(PhysicsTensors::ToPxPyPzE(Vector));
}

torch::Tensor PhysicsTensors::P2Polar(torch::Tensor Vector)
{
	return PhysicsTensors::P2Cartesian(PhysicsTensors::ToPxPyPz(Vector)); 
}

torch::Tensor PhysicsTensors::PPolar(torch::Tensor Vector)
{
	return PhysicsTensors::PCartesian(PhysicsTensors::ToPxPyPz(Vector)); 
}
