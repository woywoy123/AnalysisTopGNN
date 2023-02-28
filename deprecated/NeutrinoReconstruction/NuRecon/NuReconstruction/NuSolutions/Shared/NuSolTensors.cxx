#include <torch/extension.h>
#include "../Headers/NuSolTensors.h"

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("x0Polar", &NuSolutionTensors::x0Polar, "x0Polar"); 
	m.def("x0Cartesian", &NuSolutionTensors::x0Cartesian, "x0Cartesian");
	
	m.def("SxCartesian", &NuSolutionTensors::SxCartesian, "SxCartesian");
	m.def("SyCartesian", &NuSolutionTensors::SyCartesian, "SyCartesian");
	m.def("SxSyCartesian", &NuSolutionTensors::SxSyCartesian, "SxSyCartesian");

	m.def("Eps2Cartesian", &NuSolutionTensors::Eps2Cartesian, "Eps2Cartesian"); 
	m.def("Eps2Polar", &NuSolutionTensors::Eps2Polar, "Eps2Polar"); 

	m.def("wCartesian", &NuSolutionTensors::wCartesian, "wCartesian"); 
	m.def("wPolar", &NuSolutionTensors::wPolar, "wPolar"); 

	m.def("Omega2Cartesian", &NuSolutionTensors::Omega2Cartesian, "Omega2Cartesian"); 
	m.def("Omega2Polar", &NuSolutionTensors::Omega2Polar, "Omega2Polar");

	m.def("AnalyticalSolutionsCartesian", &NuSolutionTensors::AnalyticalSolutionsCartesian, "Intersecting Solutions"); 
	m.def("AnalyticalSolutionsPolar", &NuSolutionTensors::AnalyticalSolutionsPolar, "Intersecting Solutions");

	m.def("Intersections", &NuSolutionTensors::Intersections, "Intersection of Ellipese");
	m.def("Circle", &NuSolutionTensors::UnitCircle, "Unit Circle"); 
}
