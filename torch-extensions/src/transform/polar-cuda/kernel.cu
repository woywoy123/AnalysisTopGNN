#include "polar.cu"

template <typename scalar_t> 
__global__ void PtK(
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> px, 
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> py, 
    torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pt, 
    const unsigned int length)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    if (idx >= length){ return; }
    pt_(&pt[idx][0], &px[idx][0], &py[idx][0]); 
}

template <typename scalar_t> 
__global__ void EtaK(
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> px, 
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> py, 
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pz, 
    torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> eta, 
    const unsigned int length)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    if (idx >= length){ return; }
    eta_(&eta[idx][0], &px[idx][0], &py[idx][0], &pz[idx][0]); 
}

template <typename scalar_t> 
__global__ void PhiK(
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> px, 
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> py, 
    torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> phi, 
    const unsigned int length)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    if (idx >= length){ return; }
    phi_(&phi[idx][0], &px[idx][0], &py[idx][0]); 
}        

template <typename scalar_t>
__global__ void PtEtaPhiK(
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> px, 
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> py, 
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pz, 
    torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> out,
    const unsigned int length)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 

    if (idx >= length || idy >= 2){ return; }
    if (idy == 0)
    { 
            pt_(&out[idx][0], &px[idx][0], &py[idx][0]); 
            etapt_(&out[idx][1], &out[idx][0], &pz[idx][0]); 
            return; 
    }
    phi_(&out[idx][2], &px[idx][0], &py[idx][0]);
} 

template <typename scalar_t>
__global__ void PtEtaPhiEK(
    const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> Pmc, 
    torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> out,
    const unsigned int length)
{
    const unsigned int idx = blockIdx.x * blockDim.x + threadIdx.x; 
    const unsigned int idy = blockIdx.y; 

    if (idx >= length || idy >= 3){ return; }
    if (idy == 0)
    { 
            pt_(&out[idx][0], &Pmc[idx][0], &Pmc[idx][1]); 
            etapt_(&out[idx][1], &out[idx][0], &Pmc[idx][2]); 
            return; 
    }
    if (idy == 1){ phi_(&out[idx][2], &Pmc[idx][0], &Pmc[idx][1]); return; }
    out[idx][3] = Pmc[idx][3];
}

