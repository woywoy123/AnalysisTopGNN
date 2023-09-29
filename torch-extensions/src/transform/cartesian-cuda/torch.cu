#define CHECK_CUDA(x) TORCH_CHECK(x.device().is_cuda(), "#x must be on CUDA")
#define CHECK_CONTIGUOUS(x) TORCH_CHECK(x.is_contiguous(), "#x must be contiguous")
#define CHECK_INPUT(x) CHECK_CUDA(x); CHECK_CONTIGUOUS(x)

#include <torch/torch.h>
#include "kernel.cu"

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

torch::Tensor _Px(torch::Tensor pt, torch::Tensor phi)
{
    pt = pt.view({-1, 1}).contiguous(); 
    phi = phi.view({-1, 1}).contiguous();
    CHECK_INPUT(pt); CHECK_INPUT(phi);  
    
    torch::Tensor px = torch::zeros_like(pt);
    const unsigned int threads = 1024;   
    const unsigned int len = pt.size(0); 
    const dim3 blk = BLOCKS(threads, len); 
    
    AT_DISPATCH_FLOATING_TYPES(pt.scalar_type(), "PxK", ([&]
    {
        PxK<scalar_t><<<blk, threads>>>(
            pt.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
           phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            len
        );
    })); 
    return px;  
}

torch::Tensor _Py(torch::Tensor pt, torch::Tensor phi)
{
    pt = pt.view({-1, 1}).contiguous(); 
    phi = phi.view({-1, 1}).contiguous(); 
    CHECK_INPUT(pt); CHECK_INPUT(phi);  

    torch::Tensor py = torch::zeros_like(pt);
    const unsigned int threads = 1024;   
    const unsigned int len = pt.size(0); 
    const dim3 blk = BLOCKS(threads, len); 
    
    AT_DISPATCH_FLOATING_TYPES(pt.scalar_type(), "PyK", ([&]
    {
        PyK<scalar_t><<<blk, threads>>>(
            pt.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
           phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            len
        );
    })); 
    return py;  
}

torch::Tensor _Pz(torch::Tensor pt, torch::Tensor eta)
{
    pt = pt.view({-1, 1}).contiguous(); 
    eta = eta.view({-1, 1}).contiguous(); 
    CHECK_INPUT(pt); CHECK_INPUT(eta);  

    torch::Tensor pz = torch::zeros_like(pt);
    const unsigned int threads = 1024;   
    const unsigned int len = pt.size(0); 
    const dim3 blk = BLOCKS(threads, len); 
    
    AT_DISPATCH_FLOATING_TYPES(pt.scalar_type(), "PzK", ([&]
    {
        PzK<scalar_t><<<blk, threads>>>(
            pt.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
           eta.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            len
        );
    })); 
    return pz;  
}

torch::Tensor _PxPyPz(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
{
    pt  = pt.view({-1, 1}).contiguous(); 
    eta = eta.view({-1, 1}).contiguous(); 
    phi = phi.view({-1, 1}).contiguous();     

    torch::Tensor out = torch::zeros_like(pt);
    out = torch::cat({out, out, out}, -1).contiguous(); 
    CHECK_INPUT(pt); CHECK_INPUT(eta); CHECK_INPUT(phi); CHECK_INPUT(out); 

    const unsigned int len = pt.size(0); 
    const unsigned int threads = 1024;   
    const dim3 blk = BLOCKS(threads, len, 3, 1); 
    
    AT_DISPATCH_FLOATING_TYPES(pt.scalar_type(), "PxPyPzK", ([&]
    {
        PxPyPzK<scalar_t><<<blk, threads>>>(
            pt.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
           eta.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
           phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
           out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            len
        );
    })); 
    return out;  
}

torch::Tensor _PxPyPzE(torch::Tensor Pmu)
{
    torch::Tensor out = torch::zeros_like(Pmu);
    CHECK_INPUT(out); CHECK_INPUT(Pmu); 

    const unsigned int len = out.size(0); 
    const unsigned int threads = 1024;   
    const dim3 blk = BLOCKS(threads, len, 4, 1); 
    
    AT_DISPATCH_FLOATING_TYPES(out.scalar_type(), "PxPyPz3K", ([&]
    {
        PxPyPzEK<scalar_t><<<blk, threads>>>(
            Pmu.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            len
        );
    })); 
    return out;  
}
