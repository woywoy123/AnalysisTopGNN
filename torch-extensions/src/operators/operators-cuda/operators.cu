#include <cuda.h>

template <typename scalar_t>
__device__ __forceinline__ void dot_ij(scalar_t &p2, const scalar_t &p)
{
    p2 *= (p);     
}

template <typename scalar_t>
__device__ __forceinline__ void dot_ij(scalar_t &o, const scalar_t &v1, const scalar_t &v2)
{
    o = v1*v2;     
}

template <typename scalar_t>
__device__ __forceinline__ void sum(scalar_t &p, const scalar_t &p_1)
{
    p += p_1; 
}

template <typename scalar_t>
__device__ __forceinline__ void costheta(
        scalar_t &o, const scalar_t &v1, 
        const scalar_t &v2, const scalar_t &v1v2)
{
    o = v1 * v2; 
    if (o <= 0){o = 0; return;} 
    o = v1v2/sqrt(o);  
}

template <typename scalar_t>
__device__ __forceinline__ void sintheta(
        scalar_t &o, const scalar_t &v1, 
        const scalar_t &v2, const scalar_t &v1v2)
{
    o = v1 * v2; 
    if (o == 0){o = 0; return;} 
    o = 1 - (v1v2*v1v2)/o;  
    if (o <= 0){ o = 0; return; }
    o = sqrt(o); 
}

template <typename scalar_t>
__device__ __forceinline__ void _rx(
        scalar_t &o, const scalar_t &theta, 
        const unsigned int idy, const unsigned int idz)
{
    if (idz == 0 && idy == 0){ o = 1; return; }
    if (idz == idy){ o = cos(theta); return; } 
    if (idz == 2 && idy == 1){o = -sin(theta); return; }
    if (idz == 1 && idy == 2){o = sin(theta); return; }
}

template <typename scalar_t>
__device__ __forceinline__ void _ry(
        scalar_t &o, const scalar_t &theta, 
        const unsigned int idy, const unsigned int idz)
{
    if (idz == 1 && idy == 1){ o = 1; return; }
    if (idz == idy){ o = cos(theta); return; }
    if (idz == 0 && idy == 2){ o = -sin(theta); return; }
    if (idz == 2 && idy == 0){ o = sin(theta); return; }
}

template <typename scalar_t>
__device__ __forceinline__ void _rz(
        scalar_t &o, const scalar_t &theta, 
        const unsigned int idy, const unsigned int idz)
{
    if (idz == 2 && idy == 2){ o = 1; return; }
    if (idz == idy){ o = cos(theta); return; }
    if (idz == 1 && idy == 0){ o = -sin(theta); return; }
    if (idz == 0 && idy == 1){ o = sin(theta); return; }
}

template <typename scalar_t>
__device__ __forceinline__ void _det(scalar_t &o, 
        const scalar_t &a, const scalar_t &b, 
        const scalar_t &c, const scalar_t &d)
{
    o = a*d - c*b; 
}
