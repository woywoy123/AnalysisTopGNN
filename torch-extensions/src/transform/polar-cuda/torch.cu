#ifndef TRANSFORM_CUDA_POLAR_KERNEL_H
#define TRANSFORM_CUDA_POLAR_KERNEL_H
#include <torch/torch.h>
#include "kernel.cu"

#define CHECK_CUDA(x) TORCH_CHECK(x.device().is_cuda(), "#x must be on CUDA")
#define CHECK_CONTIGUOUS(x) TORCH_CHECK(x.is_contiguous(), "#x must be contiguous")
#define CHECK_INPUT(x) CHECK_CUDA(x); CHECK_CONTIGUOUS(x)

static const dim3 BLOCKS(const unsigned int threads, const unsigned int len)
{
    const dim3 blocks( (len + threads -1) / threads ); 
    return blocks; 
}

static const dim3 BLOCKS(
    const unsigned int threads, const unsigned int len, 
    const unsigned int dy,      const unsigned int dz 
)
{
    const dim3 blocks( (len + threads -1) / threads, dy, dz); 
    return blocks; 
}

static const torch::Tensor clip(torch::Tensor inpt, int dim)
{
    return inpt.index({torch::indexing::Slice(), dim}); 
}

torch::Tensor _Pt(torch::Tensor px, torch::Tensor py)
{
    px = px.view({-1, 1}).contiguous(); 
    py = py.view({-1, 1}).contiguous(); 
    CHECK_INPUT(px); CHECK_INPUT(py); 
    
    torch::Tensor pt = torch::zeros_like(px);
    const unsigned int len = pt.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len); 

    AT_DISPATCH_FLOATING_TYPES(pt.scalar_type(), "PtK", ([&]
    {
        PtK<scalar_t><<<blk, threads>>>(
            px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            pt.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            len
        ); 
    })); 
    return pt; 
}

torch::Tensor _Eta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
    px = px.view({-1, 1}).contiguous(); 
    py = py.view({-1, 1}).contiguous(); 
    pz = pz.view({-1, 1}).contiguous();
    CHECK_INPUT(px); CHECK_INPUT(py); CHECK_INPUT(pz);
    
    torch::Tensor eta = torch::zeros_like(px);
    const unsigned int len = eta.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len); 

    AT_DISPATCH_FLOATING_TYPES(eta.scalar_type(), "EtaK", ([&]
    {
        EtaK<scalar_t><<<blk, threads>>>(
            px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
           eta.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            len
        ); 
    })); 
    return eta; 
}

torch::Tensor _Phi(torch::Tensor px, torch::Tensor py)
{
    px = px.view({-1, 1}).contiguous(); 
    py = py.view({-1, 1}).contiguous(); 
    CHECK_INPUT(px); CHECK_INPUT(py);
    
    torch::Tensor phi = torch::zeros_like(px);
    const unsigned int len = phi.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len); 

    AT_DISPATCH_FLOATING_TYPES(phi.scalar_type(), "PhiK", ([&]
    {
        PhiK<scalar_t><<<blk, threads>>>(
            px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
           phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            len
        ); 
    })); 
    return phi; 
}

torch::Tensor _PtEtaPhi(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
    px = px.view({-1, 1}).contiguous(); 
    py = py.view({-1, 1}).contiguous();    
    pz = pz.view({-1, 1}).contiguous(); 

    torch::Tensor out = torch::zeros_like(px);
    out = torch::cat({out, out, out}, -1).contiguous(); 
    CHECK_INPUT(px); CHECK_INPUT(py); CHECK_INPUT(pz); CHECK_INPUT(out); 

    const unsigned int len = px.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 2, 1);  

    AT_DISPATCH_FLOATING_TYPES(px.scalar_type(), "PtEtaPhiK", ([&]
    {
        PtEtaPhiK<scalar_t><<<blk, threads>>>(
            px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
           out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            len
        );
    })); 
    return out; 
}

torch::Tensor _PtEtaPhiE(torch::Tensor Pmc)
{
    torch::Tensor out = torch::zeros_like(Pmc); 
    CHECK_INPUT(out); CHECK_INPUT(Pmc); 

    const unsigned int len = Pmc.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 3, 1);  

    AT_DISPATCH_FLOATING_TYPES(out.scalar_type(), "PtEtaPhiEK", ([&]
    {
        PtEtaPhiEK<scalar_t><<<blk, threads>>>(
            Pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            len
        );
    })); 
    return out; 
}

#endif
