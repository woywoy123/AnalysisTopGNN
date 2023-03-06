#include "../Headers/NuSolTensor.h"

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("NuPtEtaPhiE", &NuTensor::PtEtaPhiE, "Nu");
	m.def("NuPxPyPzE", &NuTensor::PxPyPzE, "Nu");

	m.def("NuDoublePtEtaPhiE", &NuTensor::PtEtaPhiE_Double, "Nu");
	m.def("NuDoublePxPyPzE", &NuTensor::PxPyPzE_Double, "Nu");

	m.def("NuListPtEtaPhiE", &NuTensor::PtEtaPhiE_DoubleList, "Nu");
	m.def("NuListPxPyPzE", &NuTensor::PxPyPzE_DoubleList, "Nu");

	m.def("NuNuPtEtaPhiE", &NuNuTensor::PtEtaPhiE, "NuNu");
	m.def("NuNuPxPyPzE", &NuNuTensor::PxPyPzE, "NuNu");

	m.def("NuNuDoublePtEtaPhiE", &NuNuTensor::PtEtaPhiE_Double, "NuNu");
	m.def("NuNuDoublePxPyPzE", &NuNuTensor::PxPyPzE_Double, "NuNu");
	
	m.def("NuNuListPtEtaPhiE", &NuNuTensor::PtEtaPhiE_DoubleList, "NuNu");
	m.def("NuNuListPxPyPzE", &NuNuTensor::PxPyPzE_DoubleList, "NuNu");
}
