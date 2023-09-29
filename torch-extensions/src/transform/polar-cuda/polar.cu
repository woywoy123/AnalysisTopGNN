#include <cuda.h>
#include <torch/torch.h>

template <typename scalar_t>
__device__ __forceinline__ void pt_(scalar_t* _pt, const scalar_t* _px, const scalar_t* _py)
{
    (*_pt) = sqrt( pow( *_px, 2 ) + pow( *_py, 2 ) ); 
}

template <typename scalar_t>
__device__ __forceinline__ void eta_(scalar_t* _eta, const scalar_t* _px, const scalar_t* _py, const scalar_t* _pz)
{
    (*_eta) = pow(*_px, 2) + pow(*_py, 2);
    if ( *_eta != 0 ){ *_eta = asinh( *_pz / sqrt( *_eta ) ); }
    else { *_eta = -1; }
}

template <typename scalar_t>
__device__ __forceinline__ void etapt_(scalar_t* _eta, const scalar_t* _pt, const scalar_t* _pz)
{
    if ( *_pt != 0 ){ *_eta = asinh( *_pz / *_pt  ); }
    else { *_eta = -1; }
}

template <typename scalar_t>
__device__ __forceinline__ void phi_(scalar_t* _phi, const scalar_t* _px, const scalar_t* _py)
{   
    if (*_px == 0){ return; }
    *_phi = atan2( *_py, *_px ); 
}


