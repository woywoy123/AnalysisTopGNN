#include "../Headers/FromCartesianCUDA.h"

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("P2", &PhysicsCartesianCUDA::P2, "P2");
	m.def("P", &PhysicsCartesianCUDA::P, "P"); 
	m.def("Beta2", &PhysicsCartesianCUDA::Beta2, "Beta2"); 
	m.def("Beta", &PhysicsCartesianCUDA::Beta, "Beta");

	m.def("M2", &PhysicsCartesianCUDA::M2, "M2");
	m.def("M", &PhysicsCartesianCUDA::M, "M");
	m.def("Mass", &PhysicsCartesianCUDA::Mass, "Mass");
	
	m.def("Mt2", &PhysicsCartesianCUDA::Mt2, "Mt2");
	m.def("Mt", &PhysicsCartesianCUDA::Mt, "Mt");

	m.def("Theta", &PhysicsCartesianCUDA::Theta, "Theta");
	m.def("DeltaR", &PhysicsCartesianCUDA::DeltaR, "DeltaR");
}
