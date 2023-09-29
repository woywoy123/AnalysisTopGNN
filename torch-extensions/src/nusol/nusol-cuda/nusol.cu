#include <cuda.h>
#include <cmath>

template <typename scalar_t>
__device__ __forceinline__ scalar_t _x0(const scalar_t &m_hvy2, const scalar_t &m_lght2, const scalar_t &m_p2, const scalar_t &energy)
{
    return (-m_hvy2 + m_lght2 + m_p2) / (2*energy);  
}

template <typename scalar_t> 
__device__ __forceinline__ scalar_t _Sx(const scalar_t &x0, const scalar_t &beta2_mu, const scalar_t &beta_mu, const scalar_t &energy_mu)
{
    return (x0 * sqrt(beta2_mu) - sqrt(beta2_mu)*energy_mu * (1 - beta2_mu))/beta2_mu; 
} 

template <typename scalar_t>
__device__ __forceinline__ scalar_t _Sy(const scalar_t &x0p, const scalar_t &Sx, const scalar_t &beta_b, const scalar_t &cos, const scalar_t &sin)
{
    return ((x0p/beta_b) - cos * Sx) / sin; 
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _w(const scalar_t &beta_mu, const scalar_t &beta_b, const scalar_t &cos, const scalar_t &sin)
{
    return (beta_mu/beta_b - cos) / sin; 
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _omega2(
        const scalar_t &w, const scalar_t &mu_beta2)
{
    return w*w + 1 - mu_beta2; 
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _epsilon2(
        const scalar_t &mass2_W, const scalar_t &mass2_nu, const scalar_t &beta2_mu)
{
    return (mass2_W - mass2_nu)*(1 - beta2_mu); 
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _coef(
        const scalar_t &Sx, const scalar_t &Sy, const scalar_t &w, const scalar_t &Omega2)
{
    return (Sx + w*Sy)/Omega2; 
}

template <typename scalar_t>
__device__ __forceinline__ scalar_t _Z(
        const scalar_t &x1, const scalar_t &Omega2 , const scalar_t &Sy, const scalar_t &Sx, 
        const scalar_t  &w, const scalar_t &mass2_W, const scalar_t &x0, const scalar_t &eps2)
{
    scalar_t tmp = Sy - w * Sx; 
    tmp = (x1 * x1) * Omega2 - tmp * tmp - (mass2_W - x0*x0 - eps2); 
    if (tmp <= 0){ return 0; }
    return sqrt(tmp); 
}

template <typename scalar_t>
__device__ __forceinline__ void _pihalf(scalar_t &theta)
{
    theta = 0.5*M_PI - theta; 
}

template <typename scalar_t>
__device__ __forceinline__ void _swapAB(
        scalar_t &A, scalar_t &B, const scalar_t &DetA, const scalar_t &DetB)
{
    scalar_t a = A; 
    scalar_t b = B; 
    if ( abs(DetB) > abs(DetA) )
    {
        A = b; 
        B = a; 
    }
}

__device__ __forceinline__ void _imageG(
        double &G, const double &A, const double &B, 
        const double &rel, const double &img)
{
    if (img != 0){ return; }
    G = B - rel*A; 
}

__device__ __forceinline__ double _det( 
        const double &a, const double &b, const double &c, const double &d)
{
    return a*d - c*b; 
}

__device__ __forceinline__ double _qsub(
        const double &q12, const double &coef00, const unsigned int &lim)
{
    if ( coef00 == 0 ){ return q12; }
    if (lim == 0){ return q12 - sqrt(-coef00); }
    return q12 + sqrt(-coef00); 
}

__device__ __forceinline__ double _qsub(
        const double &q01, const double &q11,
        const double &coef02, const double &coef12, const double &coef22,
        const unsigned int &lim)
{
    return - (q11 * coef12 + _qsub(q01, coef22, lim) * coef02)/coef22; 
}

__device__ __forceinline__ double _mul_ij(const double &line_i, const double &rel)
{
    return rel*line_i;  
}

