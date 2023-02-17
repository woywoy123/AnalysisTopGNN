#include "../Headers/NuSolCUDA.h"

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("Nu", &SingleNuCUDA::Nu, "Nu");
	m.def("NuNu", &DoubleNuCUDA::NuNu, "NuNu");
}
