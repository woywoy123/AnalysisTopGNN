#include <torch/extension.h>
#include "../Headers/NuSolFloats.h"

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("x0Polar", &NuSolutionFloats::x0Polar, "x0Polar"); 
	m.def("x0Cartesian", &NuSolutionFloats::x0Cartesian, "x0Cartesian");

	m.def("SxPolar", &NuSolutionFloats::SxPolar, "SxPolar");
	m.def("SyPolar", &NuSolutionFloats::SyPolar, "SyPolar");

	m.def("Eps2Cartesian", &NuSolutionFloats::Eps2Cartesian, "Eps2Cartesian"); 
	m.def("Eps2Polar", &NuSolutionFloats::Eps2Polar, "Eps2Polar"); 

	m.def("wCartesian", &NuSolutionFloats::wCartesian, "wCartesian"); 
	m.def("wPolar", &NuSolutionFloats::wPolar, "wPolar"); 

	m.def("Omega2Cartesian", &NuSolutionFloats::Omega2Cartesian, "Omega2Cartesian"); 
	m.def("Omega2Polar", &NuSolutionFloats::Omega2Polar, "Omega2Polar"); 

	m.def("AnalyticalSolutionsCartesian", &NuSolutionFloats::AnalyticalSolutionsCartesian, "Intersecting Solutions"); 
	m.def("AnalyticalSolutionsPolar", &NuSolutionFloats::AnalyticalSolutionsPolar, "Intersecting Solutions"); 

}
