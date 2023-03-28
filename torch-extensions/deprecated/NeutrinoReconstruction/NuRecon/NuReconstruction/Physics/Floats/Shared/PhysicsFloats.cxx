#include "../Headers/PhysicsFloats.h"
#include <torch/extension.h>

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("ToPx", &PhysicsFloats::ToPx, "ToPx"); 
	m.def("ToPy", &PhysicsFloats::ToPy, "ToPy"); 
	m.def("ToPz", &PhysicsFloats::ToPz, "ToPz"); 

	m.def("ToPxPyPzE", &PhysicsFloats::ToPxPyPzE, "ToPxPyPzE"); 
	m.def("ToPxPyPz", &PhysicsFloats::ToPxPyPz, "ToPxPyPz"); 

	m.def("Rx", &PhysicsFloats::Rx, "Rx");
	m.def("Ry", &PhysicsFloats::Ry, "Ry");
	m.def("Rz", &PhysicsFloats::Rz, "Rz");

	m.def("ThetaPolar", &PhysicsFloats::ToThetaPolar, "Theta"); 
	m.def("ThetaCartesian", &PhysicsFloats::ToThetaCartesian, "Theta"); 
	
	m.def("Mass2Polar", &PhysicsFloats::Mass2Polar, "Mass2Polar");
	m.def("MassPolar", &PhysicsFloats::MassPolar, "MassPolar"); 

	m.def("Mass2Cartesian", &PhysicsFloats::Mass2Cartesian, "Mass2Cartesian"); 
	m.def("MassCartesian", &PhysicsFloats::MassCartesian, "MassCartesian"); 

	m.def("P2Cartesian", &PhysicsFloats::P2Cartesian, "P2Cartesian"); 
	m.def("PCartesian", &PhysicsFloats::PCartesian, "PCartesian"); 

	m.def("P2Polar", &PhysicsFloats::P2Polar, "P2Polar"); 
	m.def("PPolar", &PhysicsFloats::PPolar, "PPolar"); 

	m.def("BetaPolar", &PhysicsFloats::BetaPolar, "BetaPolar"); 
	m.def("BetaCartesian", &PhysicsFloats::BetaCartesian, "BetaCartesian");

	m.def("Beta2Polar", &PhysicsFloats::Beta2Polar, "Beta2Polar"); 
	m.def("Beta2Cartesian", &PhysicsFloats::Beta2Cartesian, "Beta2Cartesian");

	m.def("CosThetaCartesian", &PhysicsFloats::CosThetaCartesian, "CosThetaCartesian"); 
	m.def("SinThetaCartesian", &PhysicsFloats::SinThetaCartesian, "SinThetaCartesian"); 
}


