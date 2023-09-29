#include <cuda.h>
#include <cmath>

template <typename scalar_t>
__device__ __forceinline__ void p2(scalar_t &p2, const scalar_t &p)
{
    p2 = (p) * (p);     
}

template <typename scalar_t>
__device__ __forceinline__ void sum(scalar_t &p, const scalar_t &p_1, const scalar_t &p_2)
{
   p += p_1 + p_2;  
}

template <typename scalar_t>
__device__ __forceinline__ void sum(scalar_t &p, const scalar_t &p_)
{
    p+=p_; 
}

template <typename scalar_t> 
__device__ __forceinline__ void minus(scalar_t &p, const scalar_t &p1)
{
    p -= p1; 
}

template <typename scalar_t> 
__device__ __forceinline__ void minus_mod(scalar_t &p, const scalar_t &p1)
{
   	p = M_PI - fabs(fmod(fabs(p - p1),  2*M_PI) - M_PI); 
}

template <typename scalar_t>
__device__ __forceinline__ void _sqrt(scalar_t &p, const scalar_t &p2)
{
	p = (p2 < 0) ? 0 : sqrt(p2);
}

template <typename scalar_t>
__device__ __forceinline__ void _div_ij(scalar_t &pi, const scalar_t &p_i, const scalar_t &p_j)
{
    pi = (p_j == 0) ? 0 : p_i / p_j; 
}

template <typename scalar_t>
__device__ __forceinline__ void acos_ij(scalar_t &o, const scalar_t &inpt)
{
    o = acos(inpt); 
}
