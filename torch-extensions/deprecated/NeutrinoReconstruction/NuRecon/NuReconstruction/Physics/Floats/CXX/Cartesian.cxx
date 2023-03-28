#include "../../Tensors/Headers/PhysicsTensors.h"
#include "../Headers/PhysicsFloats.h"

torch::Tensor PhysicsFloats::ToPx(double pt, double phi, std::string device)
{
	return PhysicsFloats::ToTensor(pt*std::cos(phi), device); 
}

torch::Tensor PhysicsFloats::ToPy(double pt, double phi, std::string device)
{
	return PhysicsFloats::ToTensor(pt*std::sin(phi), device); 
}

torch::Tensor PhysicsFloats::ToPz(double pt, double eta, std::string device)
{
	return PhysicsFloats::ToTensor(pt*std::sinh(eta), device); 
}

torch::Tensor PhysicsFloats::ToPxPyPzE(double pt, double eta, double phi, double E, std::string device)
{
	return torch::cat({
				ToPx(pt, phi, device), 
				ToPy(pt, phi, device), 
				ToPz(pt, eta, device), 
				PhysicsFloats::ToTensor(E, device)
			}).view({-1, 4}); 
}

torch::Tensor PhysicsFloats::ToPxPyPz(double pt, double eta, double phi, std::string device)
{
	return torch::cat({
				ToPx(pt, phi, device), 
				ToPy(pt, phi, device), 
				ToPz(pt, eta, device)
			}).view({-1, 3}); 
}

torch::Tensor PhysicsFloats::ToThetaCartesian(double Px, double Py, double Pz, std::string device)
{
	return PhysicsTensors::ToThetaCartesian(PhysicsFloats::ToTensor(Px, Py, Pz, device));  
}

torch::Tensor PhysicsFloats::Mass2Cartesian(double px, double py, double pz, double e, std::string device)
{
	torch::Tensor Pmu = torch::tensor({px, py, pz, e}, PhysicsFloats::Options(device)).view({-1, 4}); 
	return PhysicsTensors::Mass2Cartesian(Pmu); 	
}

torch::Tensor PhysicsFloats::MassCartesian(double pt, double eta, double phi, double e, std::string device)
{
	return PhysicsFloats::Mass2Polar(pt, eta, phi, e, device).sqrt(); 	
}

torch::Tensor PhysicsFloats::P2Cartesian(double px, double py, double pz, std::string device)
{
	return torch::tensor({px, py, pz}, PhysicsFloats::Options(device)).pow(2).sum({-1}).view({-1, 1});
}

torch::Tensor PhysicsFloats::PCartesian(double px, double py, double pz, std::string device)
{
	return torch::sqrt(PhysicsFloats::P2Cartesian(px, py, pz, device));
}

torch::Tensor PhysicsFloats::BetaCartesian(double px, double py, double pz, double e, std::string device)
{
	return torch::sqrt(PhysicsFloats::P2Cartesian(px, py, pz, device))/PhysicsFloats::ToTensor(e, device);  
}

torch::Tensor PhysicsFloats::Beta2Cartesian(double px, double py, double pz, double e, std::string device)
{
	return PhysicsFloats::P2Cartesian(px, py, pz, device)/(PhysicsFloats::ToTensor(e, device)).pow(2);  
}

torch::Tensor PhysicsFloats::CosThetaCartesian(double px1, double px2, double py1, double py2, 
					       double pz1, double pz2, std::string device)
{
	torch::Tensor vec1 = torch::tensor({px1, py1, pz1}, PhysicsFloats::Options(device)).view({-1, 3});
	torch::Tensor vec2 = torch::tensor({px2, py2, pz2}, PhysicsFloats::Options(device)).view({-1, 3});
	return PhysicsTensors::CosThetaCartesian(vec1, vec2);
}

torch::Tensor PhysicsFloats::SinThetaCartesian(double px1, double px2, double py1, double py2, 
		                               double pz1, double pz2, std::string device)
{
	torch::Tensor vec1 = torch::tensor({px1, py1, pz1}, PhysicsFloats::Options(device)).view({-1, 3});
	torch::Tensor vec2 = torch::tensor({px2, py2, pz2}, PhysicsFloats::Options(device)).view({-1, 3});
	return PhysicsTensors::SinThetaCartesian(vec1, vec2);
}
