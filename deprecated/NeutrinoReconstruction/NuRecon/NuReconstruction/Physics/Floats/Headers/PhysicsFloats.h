#ifndef H_PHYSICS_FLOATS
#define H_PHYSICS_FLOATS

#include <cmath>
#include <torch/extension.h>
#include <iostream>

namespace PhysicsFloats
{
	static torch::TensorOptions Options( std::string device )
	{
		torch::TensorOptions options = torch::TensorOptions();
		if (device == "cuda"){ options = options.device(torch::kCUDA); }
		return options;
	}

	static torch::Tensor ToTensor(double var, std::string device)
	{
		return torch::tensor({var}, Options(device)).view({-1, 1}); 	
	}

	static torch::Tensor ToTensor(double px, double py, double pz, double e, std::string device)
	{
	 	return torch::tensor({px, py, pz, e}, Options(device)).view({-1, 4});
	}

	static torch::Tensor ToTensor(double px, double py, double pz, std::string device)
	{
		return torch::tensor({px, py, pz}, Options(device)).view({-1, 3}); 
	}

	torch::Tensor ToPx(double pt, double phi, std::string device); 
	torch::Tensor ToPy(double pt, double phi, std::string device); 
	torch::Tensor ToPz(double pt, double eta, std::string device); 

	torch::Tensor ToPxPyPzE(double pt, double eta, double phi, double e, std::string device); 
	torch::Tensor ToPxPyPz(double pt, double eta, double phi, std::string device); 

	torch::Tensor Rx(double angle, std::string device);
	torch::Tensor Ry(double angle, std::string device);
	torch::Tensor Rz(double angle, std::string device);

	torch::Tensor ToThetaCartesian(double Px, double Py, double Pz, std::string device);
	torch::Tensor ToThetaPolar(double pt, double eta, double phi, std::string device); 
	
	torch::Tensor Mass2Polar(double pt, double eta, double phi, double e, std::string device); 
	torch::Tensor MassPolar(double pt, double eta, double phi, double e, std::string device);

	torch::Tensor Mass2Cartesian(double px, double py, double pz, double e, std::string device);
	torch::Tensor MassCartesian(double px, double py, double pz, double e, std::string device);
	
	torch::Tensor P2Cartesian(double px, double py, double pz, std::string device);
	torch::Tensor P2Polar(double pt, double eta, double phi, std::string device); 

	torch::Tensor PCartesian(double px, double py, double pz, std::string device);
	torch::Tensor PPolar(double pt, double eta, double phi, std::string device); 

	torch::Tensor BetaPolar(double pt, double eta, double phi, double e, std::string device);
	torch::Tensor BetaCartesian(double px, double py, double pz, double e, std::string device);

	torch::Tensor Beta2Polar(double pt, double eta, double phi, double e, std::string device);
	torch::Tensor Beta2Cartesian(double px, double py, double pz, double e, std::string device);
	

	torch::Tensor CosThetaCartesian(double px1, double px2, 
			double py1, double py2, double pz1, double pz2, std::string device); 
	torch::Tensor SinThetaCartesian(double px1, double px2, 
			double py1, double py2, double pz1, double pz2, std::string device);
}
#endif
