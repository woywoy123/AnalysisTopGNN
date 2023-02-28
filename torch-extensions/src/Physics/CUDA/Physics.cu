#include <torch/extension.h>
#include <cuda.h>
#include <cuda_runtime.h>

template <typename scalar_t>
__device__ __forceinline__ scalar_t _pow(const scalar_t p)
{
	return p*p;
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _sqrt(const scalar_t p)
{
	return (p < 0) ? 0 : sqrt(p);
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _div_e2(const scalar_t p2, const scalar_t e)
{
	return p2 / _pow(e);
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _div_v1_v2(const scalar_t v1, const scalar_t v2)
{
	return ( v2 == 0 ) ? 0 : v1 / v2;
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _sub_v1pow2_v2(const scalar_t v1, const scalar_t v2)
{
	return _pow(v1) - v2;
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _acos_v1_v2(const scalar_t v1, const scalar_t v2)
{
	return acos(_div_v1_v2(v1, v2)); 
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _diff_pow2_v1_v2(const scalar_t v1, const scalar_t v2)
{
	return _pow(v2 - v1);
}


