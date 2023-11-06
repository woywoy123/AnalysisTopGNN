#include <torch/torch.h>
#include <cmath>
#include "nusol.cu"
#include "operators.cu"

template <typename scalar_t>
__global__ void _ShapeKernel(
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> out, 
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> inpt, 
        const unsigned int len_i, 
        const unsigned int len_k, 
        const unsigned int len_j, 
        const bool assign)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 

    if (idx >= len_i || idy >= len_k || idz >= len_j){ return; }
    if (assign){ out[idx][idy][idz] = inpt[(idx >= inpt.size(0)) ? 0 : idx][idy][idz]; return; }
    if (idy == idz){ out[idx][idy][idz] = inpt[0][0][idz]; }
}

template <typename scalar_t>
__global__ void _H_Base(
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> out, 
        const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> beta2_b, 
        const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> mass2_b, 
        const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pmc_b, 

        const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> beta2_mu, 
        const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> mass2_mu, 
        const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pmc_mu, 
 
        const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> cos, 
        const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> mass2, 
        const unsigned int dim_i, const unsigned int dim_m)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if (idx >= dim_i || idy >= 3 || idz >= 3){ return; }    
    if (idy <= 1 && idz == 1){ return; }
    if (idy == 2 && (idz == 0 || idz == 2)){ return; }
    
    scalar_t   mass2_W   = mass2[(idx >= dim_m) ? 0 : idx][0]; 
    scalar_t   mass2_top = mass2[(idx >= dim_m) ? 0 : idx][1]; 
    scalar_t   mass2_nu  = mass2[(idx >= dim_m) ? 0 : idx][2];     
    mass2_W   *= mass2_W;  
    mass2_top *= mass2_top; 
    mass2_nu  *= mass2_nu;  

    scalar_t beta_mu   = sqrt(beta2_mu[idx][0]);
    scalar_t beta_b    = sqrt(beta2_b[idx][0]); 
    scalar_t sin       = sqrt(1 - cos[idx][0]*cos[idx][0]);   
 
    scalar_t x0p  = _x0(mass2_top, mass2_W, mass2_b[idx][0], pmc_b[idx][3]); 
    scalar_t x0   = _x0(mass2_W, mass2_mu[idx][0], mass2_nu, pmc_mu[idx][3]);

    scalar_t Sx   = _Sx(x0, beta2_mu[idx][0], beta_mu, pmc_mu[idx][3]); 
    scalar_t Sy   = _Sy(x0p, Sx, beta_b, cos[idx][0], sin); 

    scalar_t w    = _w(beta_mu , beta_b, cos[idx][0], sin); 
    scalar_t Om2  = _omega2(w, beta2_mu[idx][0]); 

    scalar_t coef = _coef(Sx, Sy, w, Om2); 
    scalar_t x1   = Sx - coef; 
    if (idy == 0 && idz == 2){ out[idx][idy][idz] = x1 - beta_mu * pmc_mu[idx][3]; return; }

    scalar_t y1   = Sy - w*coef; 
    if (idy == 1 && idz == 2){ out[idx][idy][idz] = y1; }

    scalar_t eps2 = _epsilon2(mass2_W, mass2_nu, beta2_mu[idx][0]); 
    scalar_t Z    = _Z(x1, Om2, Sy, Sx, w, mass2_W, x0, eps2); 
    if (idy == 2 && idz == 1){ out[idx][idy][idz] = Z; return; }
    if (idy == 1 && idz == 0){ out[idx][idy][idz] = w*Z/sqrt(Om2); return; }
    if (idy == 0 && idz == 0){ out[idx][idy][idz] = Z/sqrt(Om2); return; }
}

template <typename scalar_t>
__global__ void _Base_Matrix_H_Kernel(
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> Ry, 
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> Rz, 

        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> RyT, 
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> RzT, 

        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> phi, 
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> theta, 
        const unsigned int dim_x)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if (idx >= dim_x || idy >= 6 || idz  >= 3){return;}
    const unsigned int idy3m = idy%3; 

    if (idy < 3)
    { 
        _rz(Rz[idx][idy][idz], -phi[idx][0], idy, idz); 
        RzT[idx][idz][idy] = Rz[idx][idy][idz]; 
    }
    else
    {
        _pihalf(theta[idx][0]); 
        _ry(Ry[idx][idy3m][idz], theta[idx][0], idy3m, idz); 
        RyT[idx][idz][idy3m] = Ry[idx][idy3m][idz]; 
    }
}

template <typename scalar_t>
__global__ void _Rz_Rx_Ry_dot_K(
        torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> Rx, 
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _Rx, 
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _Ry, 
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _Rz, 
        const unsigned int dim_i, const unsigned int dim_j, const unsigned int dim_k)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if (idx >= dim_i || idy >= dim_j*dim_j || idz >= dim_k){ return; }
    const unsigned int idy3 = idy/dim_j; 
    const unsigned int idy3m = idy%dim_j; 

    scalar_t* val = &Rx[idx][idz][idy3][idy3m]; 
    *val = 0; 
    for (unsigned int x(0); x < dim_k; ++x){
        *val += _Rz[idx][idy3m][x]*_Rx[idx][x][idy3]; 
    }
    *val = _Ry[idx][idz][idy3m]*(*val); 
}

template <typename scalar_t>
__global__ void _dot_K(
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> base_out, 
        const torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> _Rx, 
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> base, 
        const unsigned int dim_i, const unsigned int dim_j, const unsigned int dim_k)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if (idx >= dim_i || idy >= dim_j || idz >= dim_k){ return; }

    scalar_t* val = &base_out[idx][idy][idz]; 
    *val = 0; 
    for (unsigned int x(0); x < dim_k; ++x)
    {
        scalar_t _r = 0; 
        for (unsigned int y(0); y < dim_k; ++y){
            _r += _Rx[idx][idy][x][y]; 
        }
        *val += _r * base[idx][x][idz];  
    }
}

template <typename scalar_t>
__global__ void _Base_Matrix_H_Kernel(
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> RxT, 
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> Rx, 
        const unsigned int dim_x)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if (idx >= dim_x || idy >= 3 || idz  >= 3){return;}
    _rx(RxT[idx][idz][idy], -atan2(Rx[idx][2][0], Rx[idx][1][0]), idy, idz); 
}

template <typename scalar_t>
__global__ void _V0_deltaK(
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> X, 
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> dNu, 
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> met_xy, 
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> shape,  
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> H, 
        const unsigned int dim_i)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if (idx >= dim_i || idy >= 3 || idz >= 3){ return; } 

    dNu[idx][idy][idz] = met_xy[idx][idy][2 - idz] - H[idx][idy][idz]; 
    scalar_t dot_ji = 0; 
    for (unsigned int i(0); i < 3; ++i){
        dot_ji += (met_xy[idx][i][2 - idz] - H[idx][i][idz])*shape[idx][idy][i]; 
    }
    X[idx][idz][idy] = dot_ji; 
} 

template <typename scalar_t>
__global__ void _DerivativeK(
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> out, 
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> X, 
        const unsigned int dim_i)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if ( idx >= dim_i || idy >= 3 || idz >= 3 ){ return; }
    out[idx][idy][idz] = 0; 
    if (idy == 2 || idz == 2){ return; }
    _pihalf(out[idx][idy][idz]);  
    _rz(out[idx][idy][idz], out[idx][idy][idz], idy, idz); 
}

template <typename scalar_t>
__global__ void _transSumK(
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> out, 
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> in, 
        const unsigned int dim_i)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if ( idx >= dim_i || idy >= 3 || idz >= 3 ){ return; }
    out[idx][idy][idz] = in[idx][idy][idz] + in[idx][idz][idy]; 
}

template <typename scalar_t>
__global__ void _SwapAB_K(
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> DetA, 
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> DetB,
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> A, 
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> B,
        const unsigned int dim_i)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if (idx >= dim_i || idy >= 3 || idz >= 3){ return; }
    _swapAB(A[idx][idy][idz], B[idx][idy][idz], DetA[idx][0], DetB[idx][0]); 
} 

template <typename scalar_t>
__global__ void _imagineK(
        torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> G,
        const torch::PackedTensorAccessor64<double, 3, torch::RestrictPtrTraits> A,
        const torch::PackedTensorAccessor64<double, 3, torch::RestrictPtrTraits> B,
        const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> eigs, 
        const unsigned int dim_eig, const unsigned int dim_i)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y%3; 
    const unsigned int idz = blockIdx.y/3; 
    const unsigned int id_eig = blockIdx.z; 
    if ( idx >= dim_i || idy >= 3 || idz >= 3 || id_eig >= dim_eig ){ return; }
    const c10::complex<double> cmplx = eigs[idx][id_eig];
    _imageG(G[idx][id_eig][idy][idz], A[idx][idy][idz], B[idx][idy][idz], cmplx.real(), cmplx.imag()); 
}

template <typename scalar_t>
__global__ void _degenerateK(
        torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> L,
        torch::PackedTensorAccessor32<bool, 2, torch::RestrictPtrTraits> swps,
        const torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> G,
        const unsigned int dim_eig, const unsigned int dim_i, 
        unsigned int* sy, unsigned int* sz)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y%3; 
    const unsigned int idz = blockIdx.y/3; 
    const unsigned int id_eig = blockIdx.z; 

    if ( idx >= dim_i || blockIdx.y >= 9 || id_eig >= dim_eig ){ return; }

    const bool _dg = G[idx][id_eig][0][0] == 0 && G[idx][id_eig][1][1] == 0; 
    if (_dg && idy == 2){ return; }
    if (_dg && idy == 0)
    {
        if (idz == 0){ L[idx][id_eig][idy][idz] = G[idx][id_eig][0][1]; }
        else if (idz == 1){ L[idx][id_eig][idy][idz] = 0; }
        else if (idz == 2){ L[idx][id_eig][idy][idz] = G[idx][id_eig][1][2]; }
        return; 
    }
    
    if (_dg && idy == 1)
    {
        if (idz == 0){ L[idx][id_eig][idy][idz] = 0; }
        else if (idz == 1){ L[idx][id_eig][idy][idz] = G[idx][id_eig][0][1]; }
        else if (idz == 2){ L[idx][id_eig][idy][idz] = G[idx][id_eig][0][2] - G[idx][id_eig][1][2]; }
        return; 
    }

    bool _swp = abs(G[idx][id_eig][0][0]) > abs(G[idx][id_eig][1][1]); 
    if (idy == 0 && idz == 0){ swps[idx][id_eig] = _swp; }
    const unsigned int _o = (_swp) ? 0 : 9; 
    double _l   = G[idx][id_eig][sy[blockIdx.y + _o]][sz[blockIdx.y + _o]]; 
    double _l11 = G[idx][id_eig][sy[_o + 4]][sz[_o + 4]]; 
    L[idx][id_eig][idy][idz] =  _l / _l11; 
}

template <typename scalar_t>
__global__ void _CoFactorK(
        torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> G, 
        torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> L, 
        const unsigned int dim_eig, const unsigned int dim_i,
        unsigned int* dy, unsigned int* dz)
{

    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy3m = blockIdx.y%3; 
    
    const unsigned int idy = idy3m*4; 
    const unsigned int idy3 = blockIdx.y/3; 
    
    const unsigned int idz = idy3*4; 
    const unsigned int id_eig = blockIdx.z; 
    if ( idx >= dim_i || blockIdx.y >= 9 || id_eig >= dim_eig ){ return; }
    
    G[idx][id_eig][idy3m][idy3] = _det(
            L[idx][id_eig][dy[idy  ]][dz[idz  ]], L[idx][id_eig][dy[idy+1]][dz[idz+1]], 
            L[idx][id_eig][dy[idy+2]][dz[idz+2]], L[idx][id_eig][dy[idy+3]][dz[idz+3]]);
    if ((idy3m+idy3)%2 == 1){ G[idx][id_eig][idy3m][idy3] *= -1; }
}

template <typename scalar_t>
__global__ void _FactorizeK(
        torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> O, 
        const torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> Q, 
        const torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> QCoef, 
        const unsigned int dim_eig, const unsigned int dim_i, const double null)
{

    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = (blockIdx.y%3); 
    const unsigned int idz = (blockIdx.y/3); 
    const unsigned int id_eig = blockIdx.z; 
    if ( idx >= dim_i || blockIdx.y >= 9 || id_eig >= dim_eig ){ return; }

    double cq22 = QCoef[idx][id_eig][2][2];
    double q01 = Q[idx][id_eig][0][1]; 
    double q11 = Q[idx][id_eig][1][1]; 

    if ( -cq22 <= null){
        double cq00 = QCoef[idx][id_eig][0][0]; 
        if (-cq00 < 0 ){ return; } 
        
        const unsigned int l = (cq00 == 0) ? 0 : 1; 
        if (idy <= l && idz == 0){ O[idx][id_eig][idy][idz] = q01; return; }
        if (idy <= l && idz == 1){ O[idx][id_eig][idy][idz] = q11; return; }
        if (idy <= l && idz == 2){ 
            O[idx][id_eig][idy][idz] = _qsub(Q[idx][id_eig][1][2], cq00, idy);
            return; 
        }
        return; 
    } 
    if ( -cq22 < 0 ){ return; }
    const unsigned int l = (cq22 == 0) ? 0 : 1;  
    if (idy <= l && idz == 0){
        O[idx][id_eig][idy][idz] = _qsub(q01, cq22, idy); 
        return; 
    }

    if (idy <= l && idz == 1){
        O[idx][id_eig][idy][idz] = q11; 
        return; 
    }

    if (idy <= l && idz == 2){
        double cq02 = QCoef[idx][id_eig][0][2]; 
        double cq12 = QCoef[idx][id_eig][1][2]; 
        O[idx][id_eig][idy][idz] = _qsub(q01, q11, cq02, cq12, cq22, idy); 
        return; 
    }
}

template <typename scalar_t>
__global__ void _SwapXY_K(
        torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> G, 
        torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> O, 
        torch::PackedTensorAccessor32<bool, 2, torch::RestrictPtrTraits> swps, 
        const unsigned int dim_eig, const unsigned int dim_i)
{

    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y/3; 
    const unsigned int idz = blockIdx.y%3; 
    const unsigned int id_eig = blockIdx.z; 
    if ( idx >= dim_i || idy >= 3 || idz >= 3 || id_eig >= dim_eig ){ return; }
    if ( idz == 2 )
    { 
        G[idx][id_eig][idy][2] = O[idx][id_eig][idy][2]; 
        return; 
    }
    const bool swp = swps[idx][id_eig]; 
    if (swp)
    {
        G[idx][id_eig][idy][1 - idz] = O[idx][id_eig][idy][idz]; 
        return; 
    }
    G[idx][id_eig][idy][idz] = O[idx][id_eig][idy][idz];   
}

template <typename scalar_t>
__global__ void _intersectionK(
        torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> eig_line,
        torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> eig_ellipse,
        torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> r, 

        const torch::PackedTensorAccessor64<double, 3, torch::RestrictPtrTraits> A,
        const torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> line,
        const torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> V, 
        const unsigned int dim_i, const unsigned int dim_j)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if ( idx >= dim_i || idz >= 3 || idy >= dim_j*3){ return; }
    
    const unsigned int idy3 = idy/3; 
    const unsigned int idy3m = idy%3; 
    const unsigned int idy_ = idy3 + (blockIdx.y/dim_j); 
   
    const c10::complex<double> v_ = V[idx][idy_][idy3m][idz];
    const c10::complex<double> vy = V[idx][idy_][idy3m][2]; 
    if (vy.real() * v_.real() == 0)
    {
        eig_ellipse[idx][idy3][idy3m][idz] = 10e6; 
        eig_line[idx][idy3][idy3m][idz] = 10e6; 
        return; 
    }

    for (unsigned int x(0); x < 3; ++x)
    {
        const c10::complex<double> v = V[idx][idy_][idy3m][x];
        eig_ellipse[idx][idy3][idy3m][idz] += _mul_ij(A[idx][idz][x], v.real()); 
    }
    eig_line[idx][idy3][idy3m][idz] = _mul_ij(line[idx][idy/dim_j][ (idy3)%2 ][idz], v_.real());
    eig_ellipse[idx][idy3][idy3m][idz] = _mul_ij(eig_ellipse[idx][idy3][ idy3m ][idz], v_.real());  
    r[idx][idy3][idy3m][idz] = v_.real() / vy.real();
}

template <typename scalar_t>
__global__ void _SolsK(
        torch::PackedTensorAccessor64<double, 3, torch::RestrictPtrTraits> diag_i,
        torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> sols_vec, 

        const torch::PackedTensorAccessor32<long, 3, torch::RestrictPtrTraits> id, 
        const torch::PackedTensorAccessor64<double, 3, torch::RestrictPtrTraits> diag, 
        const torch::PackedTensorAccessor64<double, 4, torch::RestrictPtrTraits> vecs, 
        const torch::PackedTensorAccessor64<bool, 2, torch::RestrictPtrTraits> ignore, 
        const unsigned int dim_i, const unsigned int dim_j, const double null)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if ( idx >= dim_i || idy >= dim_j*2 || idz >= 9 ){ return; }
    if (ignore[idx][0]){ return; }
    const unsigned int idz3 = idz/3; 
    const unsigned int idz3m = idz%3;   

    const unsigned int trgt = id[idx][idy][idz3]; 
    if (idz3m == 0)
    {
        diag_i[idx][idy][idz3] = diag[idx][idy][trgt]; 
    }
    if (diag[idx][idy][trgt] >= null){ return; }
    sols_vec[idx][idy][idz3][idz3m] = vecs[idx][idy][trgt][idz3m]; 
}

template <typename scalar_t> 
__global__ void _Y_dot_X_dot_Y(
    torch::PackedTensorAccessor64<double, 3, torch::RestrictPtrTraits> s_out, 
    torch::PackedTensorAccessor64<double, 3, torch::RestrictPtrTraits> s_vec, 
    const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> X, 
    const torch::PackedTensorAccessor64<double  , 4, torch::RestrictPtrTraits> sols_vec, 
    const unsigned int dim_i, const unsigned int dim_eig, const unsigned int dim_j)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z;
    
    if (idx >= dim_i || idy >= dim_eig || idz >= dim_j*dim_j){ return; }
    const unsigned int idz3 = idz/3; 
    const unsigned int idz3m = idz%3;
    const unsigned int idy_ = 3*idy + idz3; 

    if (sols_vec[idx][idy][idz3][idz3m] == 0)
    {
        s_out[idx][idy_][idz3m] = -1; 
        return; 
    }

    double coef = 0; 
    for (unsigned int x(0); x < 3; ++x)
    {
        coef += _mul_ij(sols_vec[idx][idy][idz3][x], X[idx][x][idz3m]);
    }
    s_out[idx][idy_][idz3m] = _mul_ij(coef, sols_vec[idx][idy][idz3][idz3m]);
    s_vec[idx][idy_][idz3m] = sols_vec[idx][idy][idz3][idz3m];
}


template <typename scalar_t> 
__global__ void _YT_dot_X_dot_Y(
    torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> O1, 
    torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> O2, 

    const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> Y1, 
    const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> X1, 

    const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> Y2, 
    const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> X2, 
    const unsigned int dim_i, const unsigned int dim_j, const unsigned int dim_k)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z;
    
    if (idx >= dim_i || idy >= dim_j*dim_j*dim_j || idz >= dim_k){ return; }
    const unsigned int idy3  = (idy/(dim_j*dim_j)); 

    const unsigned int idy_  = idy%dim_j; 
    const unsigned int idy3m = (idy/3)%dim_j;

    scalar_t* val; 
    const bool swp = idz == 0;
    if (swp){ val = &O1[idx][idy3][idy3m][idy_]; }
    else    { val = &O2[idx][idy3][idy3m][idy_]; }
    
    for (unsigned int x(0); x < dim_j; ++x)
    {
        if (swp){ *val += _mul_ij(Y1[idx][x][idy3m], X1[idx][x][idy_]); }
        else    { *val += _mul_ij(Y2[idx][x][idy3m], X2[idx][x][idy_]); }   
    }
    if (swp){ *val = _mul_ij(*val, Y1[idx][idy_][idy3]); }
    else    { *val = _mul_ij(*val, Y2[idx][idy_][idy3]); }   
}

template <typename scalar_t>
__global__ void _NuK(
        torch::PackedTensorAccessor64<double, 3, torch::RestrictPtrTraits> O_sol_vec, 
        torch::PackedTensorAccessor64<double, 2, torch::RestrictPtrTraits> O_sol_chi2,

        const torch::PackedTensorAccessor32<long    , 2, torch::RestrictPtrTraits> id,
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> H, 

        const torch::PackedTensorAccessor64<double  , 3, torch::RestrictPtrTraits> sol_vec, 
        const torch::PackedTensorAccessor64<double  , 2, torch::RestrictPtrTraits> sol_chi2, 
        const unsigned int dim_i, const unsigned int dim_eig, const unsigned int dim_j)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idz = blockIdx.z; 
    if ( idx >= dim_i || blockIdx.y >= dim_eig || idz >= dim_j ){ return; }

    const unsigned int idz3 = idz/3; 
    const unsigned int idz3m = idz%3; 
    const unsigned int idy = blockIdx.y*3 + idz3; 
    const unsigned int trgt = id[idx][idy];

    double chi2 = sol_chi2[idx][trgt]; 
    if (chi2 == -3)
    { 
        O_sol_chi2[idx][idy] = -1; 
        return; 
    }

    if (idz3m == 0){O_sol_chi2[idx][idy] = chi2;}
    for (unsigned int x(0); x < 3; ++x)
    {
        O_sol_vec[idx][idy][idz3m] += _mul_ij(H[idx][idz3m][x], sol_vec[idx][trgt][x]); 
    }
}

template <typename scalar_t>
__global__ void _H_perp_K(
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> H1, 
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> H2,
        const unsigned int dim_i, const unsigned int dim_j, const unsigned int dim_k)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if ( idx >= dim_i || idy >= dim_j || idz >= dim_k){ return; }
    if ( idz == 0 ){ H1[idx][2][idy] = 1*(idy == 2); return; }
    if ( idz == 1 ){ H2[idx][2][idy] = 1*(idy == 2); return; }
}

template <typename scalar_t>
__global__ void _DotK(
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> v, 
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> v_,

        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> S, 
        const torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> sol, 
        const unsigned int dim_i, const unsigned int dim_j, const unsigned int dim_k)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if ( idx >= dim_i || idy >= dim_j || idz >= dim_k){ return; }
    const unsigned int idy3  = idy/3; 
    const unsigned int idy3m = idy%3;
  
    if (idz < 3){ v[idx][idy][idz] = sol[idx][idy3][idy3m][idz]; return; }

    scalar_t* val = &v_[idx][idy][idz-3]; 
    for (unsigned int x(0); x < 3; ++x)
    {
         *val += _mul_ij(S[idx][idz-3][x], sol[idx][idy3][idy3m][x]); 
    }
}

template <typename scalar_t>
__global__ void _K_Kern(
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> K1, 
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> K2,

        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> H1, 
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> H_inv1, 

        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> H2, 
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> H_inv2, 

        const unsigned int dim_i, const unsigned int dim_j, const unsigned int dim_k)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if ( idx >= dim_i || idy >= dim_j || idz >= dim_k){ return; }
    const unsigned int idy3  = idy/3; 
    const unsigned int idy3m = idy%3;

    const bool swp = idz == 0; 
    scalar_t* val = (swp) ? &K1[idx][idy3][idy3m] : &K2[idx][idy3][idy3m];   
    for (unsigned int x(0); x < 3; ++x)
    { 
        if (swp){ *val += _mul_ij(H1[idx][idy3][x], H_inv1[idx][x][idy3m]); }
        else    { *val += _mul_ij(H2[idx][idy3][x], H_inv2[idx][x][idy3m]); }
    } 
}

template <typename scalar_t>
__global__ void _NuNuK(
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> nu, 
        torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> nu_,
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> dig, 

        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> K1, 
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> K2, 

        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> v, 
        const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> v_, 

        const torch::PackedTensorAccessor32<long    , 2, torch::RestrictPtrTraits> id, 
        const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> diag, 
        const unsigned int dim_i, const unsigned int dim_j, const unsigned int dim_k)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    const unsigned int idz = blockIdx.z; 
    if ( idx >= dim_i || idy >= dim_j || idz >= dim_k){ return; }
    const unsigned int idz3m = idz%3; 
    const unsigned int idz3  = idz/3; 
    const unsigned int tid = id[idx][idy];  
    const bool swp = idz3 == 0; 
    if (swp){ dig[idx][idy] = diag[idx][tid]; }

    for (unsigned int x(0); x < 3; ++x)
    {  
        if (swp){ nu[idx][idy][idz3m] += _mul_ij(K1[idx][idz3m][x],  v[idx][tid][x]); }
        else   { nu_[idx][idy][idz3m] += _mul_ij(K2[idx][idz3m][x], v_[idx][tid][x]); }
    }

}



