#include "../Headers/PhysicsTensors.h"
#include <torch/extension.h>

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("ToPx", &PhysicsTensors::ToPx, "ToPx"); 
	m.def("ToPy", &PhysicsTensors::ToPy, "ToPy"); 
	m.def("ToPz", &PhysicsTensors::ToPz, "ToPz"); 

	m.def("ToPxPyPzE", &PhysicsTensors::ToPxPyPzE, "ToPxPyPzE");
	m.def("ToPxPyPz", &PhysicsTensors::ToPxPyPz, "ToPxPyPz");

	m.def("Rx", &PhysicsTensors::Rx, "Rx");
	m.def("Ry", &PhysicsTensors::Ry, "Ry");
	m.def("Rz", &PhysicsTensors::Rz, "Rz");

	m.def("ThetaPolar", &PhysicsTensors::ToThetaPolar, "Theta");
	m.def("ThetaCartesian", &PhysicsTensors::ToThetaCartesian, "Theta");

	m.def("Mass2Polar", &PhysicsTensors::Mass2Polar, "Mass2Polar");
	m.def("MassPolar", &PhysicsTensors::MassPolar, "MassPolar"); 

	m.def("Mass2Cartesian", &PhysicsTensors::Mass2Cartesian, "Mass2Cartesian"); 
	m.def("MassCartesian", &PhysicsTensors::MassCartesian, "MassCartesian"); 

	m.def("BetaPolar", &PhysicsTensors::BetaPolar, "BetaPolar"); 
	m.def("BetaCartesian", &PhysicsTensors::BetaCartesian, "BetaCartesian");

	m.def("Beta2Polar", &PhysicsTensors::Beta2Polar, "Beta2Polar"); 
	m.def("Beta2Cartesian", &PhysicsTensors::Beta2Cartesian, "Beta2Cartesian");

	m.def("CosThetaCartesian", &PhysicsTensors::CosThetaCartesian, "CosThetaCartesian"); 
	m.def("SinThetaCartesian", &PhysicsTensors::SinThetaCartesian, "SinThetaCartesian");
}

