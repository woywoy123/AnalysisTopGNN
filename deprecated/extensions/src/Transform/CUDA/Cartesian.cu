#include <cuda.h>
#include <cuda_runtime.h>

template <typename scalar_t>
__device__ __forceinline__ void _ptphi_to_px(scalar_t* _px, const scalar_t* _pt, const scalar_t* _phi)
{
	(*_px) = (*_pt) * cos((*_phi)); 
}

template <typename scalar_t>
__device__ __forceinline__ void _ptphi_to_py(scalar_t* _py, const scalar_t* _pt, const scalar_t* _phi)
{
	(*_py) = (*_pt) * sin((*_phi)); 
}

template <typename scalar_t>
__device__ __forceinline__ void _pteta_to_pz(scalar_t* _pz, const scalar_t* _pt, const scalar_t* _eta)
{
	(*_pz) = (*_pt) * sinh((*_eta)); 
}
