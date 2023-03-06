#include "../Headers/NuSolCUDA.h"

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("NuPtEtaPhiE", &NuCUDA::PtEtaPhiE, "Nu");
	m.def("NuPxPyPzE", &NuCUDA::PxPyPzE, "Nu");

	m.def("NuDoublePtEtaPhiE", &NuCUDA::PtEtaPhiE_Double, "Nu");
	m.def("NuDoublePxPyPzE", &NuCUDA::PxPyPzE_Double, "Nu");

	m.def("NuListPtEtaPhiE", &NuCUDA::PtEtaPhiE_DoubleList, "Nu");
	m.def("NuListPxPyPzE", &NuCUDA::PxPyPzE_DoubleList, "Nu");

	m.def("NuNuPtEtaPhiE", &NuNuCUDA::PtEtaPhiE, "NuNu");
	m.def("NuNuPxPyPzE", &NuNuCUDA::PxPyPzE, "NuNu");

	m.def("NuNuDoublePtEtaPhiE", &NuNuCUDA::PtEtaPhiE_Double, "NuNu");
	m.def("NuNuDoublePxPyPzE", &NuNuCUDA::PxPyPzE_Double, "NuNu");
	
	m.def("NuNuListPtEtaPhiE", &NuNuCUDA::PtEtaPhiE_DoubleList, "NuNu");
	m.def("NuNuListPxPyPzE", &NuNuCUDA::PxPyPzE_DoubleList, "NuNu");
}
