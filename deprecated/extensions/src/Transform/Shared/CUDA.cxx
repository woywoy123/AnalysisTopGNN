#include "../Headers/ToCartesianCUDA.h"
#include "../Headers/ToPolarCUDA.h"

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("Px", &TransformCUDA::Px, "Px"); 
	m.def("Py", &TransformCUDA::Py, "Py"); 
	m.def("Pz", &TransformCUDA::Pz, "Pz"); 
	m.def("PxPyPz", &TransformCUDA::PxPyPz, "PxPyPz");

	m.def("PT",  &TransformCUDA::PT, "PT");
	m.def("Phi", &TransformCUDA::Phi, "Phi");
	m.def("Eta", &TransformCUDA::Eta, "Eta");
	m.def("PtEtaPhi", &TransformCUDA::PtEtaPhi, "PtEtaPhi"); 

}
