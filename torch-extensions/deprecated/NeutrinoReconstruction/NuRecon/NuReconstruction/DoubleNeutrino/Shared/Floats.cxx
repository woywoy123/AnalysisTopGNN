#include "../Headers/Floats.h"

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
	m.def("SolT", &DoubleNu::Tensors::Init, "Solution Init Function."); 
}
