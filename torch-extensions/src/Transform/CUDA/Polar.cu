#include <torch/extension.h>
#include <cuda.h>
#include <cuda_runtime.h>

template <typename scalar_t>
__device__ __forceinline__ void _pxpy_pt(scalar_t* _pt, const scalar_t* _px, const scalar_t* _py)
{
	(*_pt) = sqrt( pow((*_px), 2) + pow(*_py, 2) );  
}

template <typename scalar_t>
__device__ __forceinline__ void _pxpy_phi(scalar_t* _phi, const scalar_t* _px, const scalar_t* _py)
{
	(*_phi) = atan2(*_py, *_px);  
}

template <typename scalar_t>
__device__ __forceinline__ void _pxpypz_eta(scalar_t* _eta, const scalar_t* _px, const scalar_t* _py, const scalar_t* _pz)
{
	_pxpy_pt(_eta, _px, _py); 
	(*_eta) = asinh(*_pz / *_eta); 
}

template <typename scalar_t>
__device__ __forceinline__ void _pxpypz_pteta(scalar_t* _pt, scalar_t* _eta, const scalar_t* _px, const scalar_t* _py, const scalar_t* _pz)
{
	_pxpy_pt(_pt, _px, _py); 
	(*_eta) = asinh(*_pz / *_pt); 
}
