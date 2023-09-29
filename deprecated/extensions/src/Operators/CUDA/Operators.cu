#include <cuda.h>
#include <cuda_runtime.h>

template <typename scalar_t> 
__device__ __forceinline__ void _v1xv2(scalar_t* _prod, const scalar_t* v1, const scalar_t* v2)
{
	(*_prod) = (*v1) * (*v2); 
}

template <typename scalar_t> 
__device__ __forceinline__ void _costheta(scalar_t* _o, const scalar_t* v12, const scalar_t* v22, const scalar_t* v1v2)
{
	(*_o) = (*v1v2) / sqrt( (*v12) * (*v22) );
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _sin(const scalar_t angle)
{
	return sin(angle); 
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _cos(const scalar_t angle)
{
	return cos(angle); 
}

template <typename scalar_t> 
__device__ __forceinline__ void _recsum(scalar_t* out, const scalar_t inpt)
{
	(*out) = (*out) + inpt;  
}
