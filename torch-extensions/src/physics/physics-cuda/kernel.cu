#include <torch/torch.h>
#include "physics.cu"

template <typename scalar_t> 
__global__ void Sq_ij_K(
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pmc, 
        const unsigned int length, 
        const unsigned int i, 
        const unsigned int j)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y + i; 
    if (idx >= length || idy > j){ return; }
    p2(pmc[idx][idy], pmc[idx][idy]);  
}

template <typename scalar_t> 
__global__ void SumK(
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pmc,
        const unsigned int length, 
        const unsigned int dim_len)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    if (idx >= length){ return; }
    for (unsigned int x(0); x < dim_len; ++x)
    { 
        if (x + 2 > dim_len){sum(pmc[idx][0], pmc[idx][x+1]); return; }
        sum(pmc[idx][0], pmc[idx][x+1], pmc[idx][x+2]); 
        ++x; 
    }
}

template <typename scalar_t>
__global__ void Sum_ij_K(
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pmc, 
        const unsigned int length, 
        const unsigned int i, 
        const unsigned int j)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    if (idx >= length){ return; }
    sum(pmc[idx][i], pmc[idx][j]);  
}

template <typename scalar_t>
__global__ void Sub_ij_K(
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pmc, 
        const unsigned int length, 
        const unsigned int i, 
        const unsigned int j)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    if (idx >= length){ return; }
    minus(pmc[idx][i], pmc[idx][j]);  
}

template <typename scalar_t>
__global__ void delta_K(
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pmu, 
        const unsigned int length)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 
    
    if(idx >= length || idy > 1){ return; }
    if (idy == 1){minus_mod(pmu[idx][idy*2], pmu[idx][idy*2+1]);}
    else {minus(pmu[idx][idy*2], pmu[idx][idy*2+1]);}
    p2(pmu[idx][idy*2], pmu[idx][idy*2]); 
}

template <typename scalar_t>
__global__ void Div_ij_K(
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pmc, 
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> div, 
        const unsigned int length, 
        const unsigned int i, 
        const unsigned int j)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    if (idx >= length){ return; }
    _div_ij(pmc[idx][i], pmc[idx][i], div[idx][j]);  
}

template <typename scalar_t>
__global__ void SqrtK(
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pmc,
        const unsigned int length,
        const unsigned int dim_min,
        const unsigned int dim_max)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x;
    const unsigned int idy = blockIdx.y + dim_min;
    if (idx >= length || dim_max < idy){ return; }   
    _sqrt(pmc[idx][idy], pmc[idx][idy]);  
}

template <typename scalar_t> 
__global__ void Sqrt_i_K(
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pmc, 
        const unsigned int length, 
        const unsigned int dim_i)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    if (idx >= length){ return; }
    _sqrt(pmc[idx][dim_i], pmc[idx][dim_i]); 
}

template <typename scalar_t> 
__global__ void ArcCos_ij_K(
        torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> ten1, 
        const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> ten2, 
        const unsigned int length, 
        const unsigned int dim_i,
        const unsigned int dim_j)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    if (idx >= length){ return; }
    _div_ij(ten1[idx][dim_i], ten2[idx][dim_j], ten1[idx][dim_i]); 
    acos_ij(ten1[idx][dim_i], ten1[idx][dim_i]); 
}
