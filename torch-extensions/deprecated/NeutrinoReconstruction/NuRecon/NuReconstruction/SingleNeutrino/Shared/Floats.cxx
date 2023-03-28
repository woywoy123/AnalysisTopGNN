#include "../Headers/Floats.h"

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("Sigma2_F", &SingleNu::Floats::Sigma2, "Uncertainty in MET"); 
	m.def("Sigma2_T", &SingleNu::Tensors::Sigma2, "Uncertainty in MET");

	m.def("V0_F", &SingleNu::Floats::V0, "Missing MET"); 
	m.def("V0_T", &SingleNu::Tensors::V0, "Missing MET");
	m.def("V0Polar_T", &SingleNu::Tensors::V0Polar, "Missing MET");

	m.def("R_F", &SingleNu::Floats::Rotation, "Rotation");
	m.def("R_T", &SingleNu::Tensors::Rotation, "Rotation");

	m.def("H_F", &SingleNu::Floats::H, "H"); 
	m.def("H_T", &SingleNu::Tensors::H, "H");

	m.def("SolT", &SingleNu::Tensors::Init, "Solution Init Function."); 
}
