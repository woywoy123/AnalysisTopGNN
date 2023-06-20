#include <torch/extension.h>
//#include <pybind11/pybind11.h>
//#include "polar-cuda/polar.h"
#include "cartesian-cuda/cartesian.h"

PYBIND11_MODULE(cuda, m)
{
	m.def("Px", &TransformCUDA::Px, "Px"); 
	m.def("Py", &TransformCUDA::Py, "Py"); 
	m.def("Pz", &TransformCUDA::Pz, "Pz"); 
	m.def("PxPyPz", &TransformCUDA::PxPyPz, "PxPyPz");

	//m.def("PT",  &TransformCUDA::PT, "PT");
	//m.def("Phi", &TransformCUDA::Phi, "Phi");
	//m.def("Eta", &TransformCUDA::Eta, "Eta");
	//m.def("PtEtaPhi", &TransformCUDA::PtEtaPhi, "PtEtaPhi"); 
}
