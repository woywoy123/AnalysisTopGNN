#include <torch/extension.h>
#include "../Headers/FromPolarTensors.h"

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("P2", &PhysicsPolarTensors::P2, "P2"); 
	m.def("P", &PhysicsPolarTensors::P, "P"); 

	m.def("Beta2", &PhysicsPolarTensors::Beta2, "Beta2"); 
	m.def("Beta", &PhysicsPolarTensors::Beta, "Beta"); 

	m.def("M2", &PhysicsPolarTensors::M2, "M2"); 
	m.def("M", &PhysicsPolarTensors::M, "M"); 
	m.def("Mass", &PhysicsPolarTensors::Mass, "Mass");

	m.def("Mt2", &PhysicsPolarTensors::Mt2, "Mt2"); 
	m.def("Mt", &PhysicsPolarTensors::Mt, "Mt"); 

	m.def("Theta", &PhysicsPolarTensors::Theta, "Theta"); 
	m.def("DeltaR", &PhysicsPolarTensors::DeltaR, "DeltaR"); 
}
