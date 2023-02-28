#include "../Headers/FromPolarCUDA.h"

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("P2", &PhysicsPolarCUDA::P2, "P2");
	m.def("P", &PhysicsPolarCUDA::P, "P"); 
	m.def("Beta2", &PhysicsPolarCUDA::Beta2, "Beta2"); 
	m.def("Beta", &PhysicsPolarCUDA::Beta, "Beta");

	m.def("M2", &PhysicsPolarCUDA::M2, "M2");
	m.def("M", &PhysicsPolarCUDA::M, "M");
	m.def("Mass", &PhysicsPolarCUDA::Mass, "Mass");
	
	m.def("Mt2", &PhysicsPolarCUDA::Mt2, "Mt2");
	m.def("Mt", &PhysicsPolarCUDA::Mt, "Mt");

	m.def("Theta", &PhysicsPolarCUDA::Theta, "Theta");
	m.def("DeltaR", &PhysicsPolarCUDA::DeltaR, "DeltaR");
}
