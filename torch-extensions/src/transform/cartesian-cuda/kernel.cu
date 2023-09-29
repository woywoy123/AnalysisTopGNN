#include "cartesian.cu"

template <typename scalar_t>
__global__ void PxK(
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pt, 
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> phi, 
    torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> px,
    const unsigned int length)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    if (idx >= length){ return; }
    px_(&px[idx][0], &pt[idx][0], &phi[idx][0]); 
}

template <typename scalar_t>
__global__ void PyK(
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pt, 
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> phi, 
    torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> py,
    const unsigned int length)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    if (idx >= length){ return; }
    py_(&py[idx][0], &pt[idx][0], &phi[idx][0]); 
}

template <typename scalar_t>
__global__ void PzK(
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pt, 
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> eta, 
    torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pz,
    const unsigned int length)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    if (idx >= length){ return; }
    pz_(&pz[idx][0], &pt[idx][0], &eta[idx][0]); 
} 

template <typename scalar_t>
__global__ void PxPyPzK(
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pt, 
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> eta, 
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> phi, 
    torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> out,
    const unsigned int length)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 

    if (idx >= length || idy >= 3){ return; }
    if (idy == 0){ px_(&out[idx][idy], &pt[idx][0], &phi[idx][0]); return; }
    if (idy == 1){ py_(&out[idx][idy], &pt[idx][0], &phi[idx][0]); return; }
    pz_(&out[idx][idy], &pt[idx][0], &eta[idx][0]);
} 

template <typename scalar_t>
__global__ void PxPyPzEK(
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> Pmu, 
    torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> out,
    const unsigned int length)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 

    if (idx >= length || idy >= 4){ return; }
    if (idy == 0){ px_(&out[idx][idy], &Pmu[idx][0], &Pmu[idx][2]); return; }
    if (idy == 1){ py_(&out[idx][idy], &Pmu[idx][0], &Pmu[idx][2]); return; }
    if (idy == 2){ pz_(&out[idx][idy], &Pmu[idx][0], &Pmu[idx][1]); return; }
    out[idx][idy] = Pmu[idx][idy];
} 
