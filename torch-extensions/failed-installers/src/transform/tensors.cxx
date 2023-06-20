#include <torch/extension.h>
#include <pybind11/pybind11.h>
#include "polar-tensors/tensors.h"
#include "cartesian-tensors/tensors.h"

PYBIND11_MODULE(Tensors, m)
{
	m.def("Px", &TransformTensors::Px, "Px"); 
	m.def("Py", &TransformTensors::Py, "Py"); 
	m.def("Pz", &TransformTensors::Pz, "Pz"); 
	m.def("PxPyPz", &TransformTensors::PxPyPz, "PxPyPz");

	m.def("PT",  &TransformTensors::PT, "PT");
	m.def("Phi", &TransformTensors::Phi, "Phi");
	m.def("Eta", &TransformTensors::Eta, "Eta");
	m.def("PtEtaPhi", &TransformTensors::PtEtaPhi, "PtEtaPhi"); 
}
