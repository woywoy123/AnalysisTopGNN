#include <torch/extension.h>
#include <cuda.h>
#include <cuda_runtime.h>

template <typename scalar_t>
__device__ __forceinline__ scalar_t _x0(
		const scalar_t H2, const scalar_t L2, 
		const scalar_t p2, const scalar_t e)
{
	return - (H2 - L2 - e*e + p2)/(2*e); 
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _w(
		const scalar_t muP2, const scalar_t bP2, const scalar_t mu_e, 
		const scalar_t b_e,  const scalar_t c_,  const scalar_t s_, 
		const int sign)
{
	return ( sign * sqrt(muP2/bP2)*(b_e/mu_e) - c_ ) / s_; 
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _beta2(const scalar_t p2, const scalar_t e)
{
	return p2/(e*e); 

}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _sqrt(const scalar_t v)
{
	return (v < 0) ? 0 : sqrt(v); 
}
