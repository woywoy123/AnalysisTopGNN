#include <torch/extension.h>
#include "../Headers/FromCartesianTensors.h"

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("P2", &PhysicsCartesianTensors::P2, "P2"); 
	m.def("P", &PhysicsCartesianTensors::P, "P"); 

	m.def("Beta2", &PhysicsCartesianTensors::Beta2, "Beta2"); 
	m.def("Beta", &PhysicsCartesianTensors::Beta, "Beta"); 

	m.def("M2", &PhysicsCartesianTensors::M2, "M2"); 
	m.def("M", &PhysicsCartesianTensors::M, "M");
	m.def("Mass", &PhysicsCartesianTensors::Mass, "Mass");

	m.def("Mt2", &PhysicsCartesianTensors::Mt2, "Mt2"); 
	m.def("Mt", &PhysicsCartesianTensors::Mt, "Mt"); 

	m.def("Theta", &PhysicsCartesianTensors::Theta, "Theta"); 
	m.def("DeltaR", &PhysicsCartesianTensors::DeltaR, "DeltaR"); 
}
