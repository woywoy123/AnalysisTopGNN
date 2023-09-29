#include "../Headers/Tensors.h"

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("Dot", &OperatorsTensors::Dot, "Dot Product");
	m.def("CosTheta", &OperatorsTensors::CosTheta, "CosTheta");
	m.def("SinTheta", &OperatorsTensors::SinTheta, "SinTheta");
	m.def("Rx", &OperatorsTensors::Rx, "Rx");
	m.def("Ry", &OperatorsTensors::Ry, "Ry");
	m.def("Rz", &OperatorsTensors::Rz, "Rz");
}
