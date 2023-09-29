#include <cuda.h>
#include <torch/torch.h>

template <typename scalar_t>
__device__ __forceinline__ void px_(scalar_t* _px, const scalar_t* _pt, const scalar_t* _phi)
{
    (*_px) = (*_pt) * cos( (*_phi) ); 
}

template <typename scalar_t>
__device__ __forceinline__ void py_(scalar_t* _py, const scalar_t* _pt, const scalar_t* _phi)
{
    (*_py) = (*_pt) * sin( (*_phi) ); 
}

template <typename scalar_t>
__device__ __forceinline__ void pz_(scalar_t* _pz, const scalar_t* _pt, const scalar_t* _eta)
{
    (*_pz) = (*_pt) * sinh( (*_eta) ); 
}
