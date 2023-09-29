#ifndef PHYSICS_CUDA_KERNEL_H
#define PHYSICS_CUDA_KERNEL_H
#include <torch/torch.h>
#include "kernel.cu"
#include <vector>

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
    const unsigned int dy,      const unsigned int dz)
{
    const dim3 blocks( (len + threads -1) / threads, dy, dz); 
    return blocks; 
}

static const torch::Tensor format(std::vector<torch::Tensor> i1)
{
    std::vector<torch::Tensor> ipt; 
    for (unsigned int i(0); i < i1.size(); ++i){ ipt.push_back(i1[i].view({-1, 1})); }
    return torch::cat(ipt, -1).contiguous();  
}


torch::Tensor _P2(torch::Tensor Pmc)
{
    Pmc = Pmc.contiguous().clone(); 
    CHECK_INPUT(Pmc); 
    const unsigned int len = Pmc.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk_ = BLOCKS(threads, len, 3, 1); 
    const dim3 blk  = BLOCKS(threads, len); 
    AT_DISPATCH_FLOATING_TYPES(Pmc.scalar_type(), "P2", ([&]
    { 
        Sq_ij_K<scalar_t><<< blk_, threads >>>(
            Pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            len, 0, 2); 
        SumK<scalar_t><<< blk, threads >>>(
            Pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
            len, 2); 
    })); 
    return Pmc.index({torch::indexing::Slice(), 0}).view({-1, 1}); 
}

torch::Tensor _P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
    torch::Tensor Pmc = format({px, py, pz}); 
    return _P2(Pmc); 
}

torch::Tensor _P(torch::Tensor Pmc)
{
    Pmc = Pmc.contiguous().clone(); 
    CHECK_INPUT(Pmc); 
    const unsigned int len = Pmc.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk_ = BLOCKS(threads, len, 3, 1); 
    const dim3 blk  = BLOCKS(threads, len); 
    const dim3 blk_s = BLOCKS(threads, len, 1, 1); 
    AT_DISPATCH_FLOATING_TYPES(Pmc.scalar_type(), "P", ([&]
    { 
        Sq_ij_K<scalar_t><<< blk_, threads >>>(
            Pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
            len, 0, 2); 

        SumK<scalar_t><<< blk, threads >>>(
            Pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
            len, 2); 

        SqrtK<scalar_t><<< blk_s, threads >>>(
            Pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
            len, 0, 0);  
    })); 
    return Pmc.index({torch::indexing::Slice(), 0}).view({-1, 1}); 
}

torch::Tensor _P(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
    torch::Tensor pmc = format({px, py, pz}); 
    return _P(pmc); 
}

torch::Tensor _Beta2(torch::Tensor pmc)
{
    pmc = pmc.contiguous().clone(); 
    CHECK_INPUT(pmc); 
    const unsigned int len = pmc.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 4, 1); 
    const dim3 blk_ = BLOCKS(threads, len);  
    
    AT_DISPATCH_FLOATING_TYPES(pmc.scalar_type(), "_Beta2", ([&]
    {
        Sq_ij_K<scalar_t><<< blk, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 3); 

        SumK<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 2); 

        Div_ij_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 3);
    })); 
    return pmc.index({torch::indexing::Slice(), 0}).view({-1, 1}); 
}

torch::Tensor _Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{
    torch::Tensor pmc = format({px, py, pz, e}); 
    return _Beta2(pmc);
}

torch::Tensor _Beta(torch::Tensor pmc)
{
    pmc = pmc.contiguous().clone(); 
    CHECK_INPUT(pmc); 
    const unsigned int len = pmc.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 3, 1); 
    const dim3 blk_ = BLOCKS(threads, len);  
    
    AT_DISPATCH_FLOATING_TYPES(pmc.scalar_type(), "_Beta", ([&]
    {
        Sq_ij_K<scalar_t><<< blk, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 3); 

        SumK<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 2);

        SqrtK<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 0); 

        Div_ij_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 3);
    })); 
    return pmc.index({torch::indexing::Slice(), 0}).view({-1, 1}); 
}

torch::Tensor _Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{
    torch::Tensor pmc = format({px, py, pz, e}); 
    return _Beta(pmc);
}

torch::Tensor _M2(torch::Tensor pmc)
{
    pmc = pmc.contiguous().clone(); 
    CHECK_INPUT(pmc); 
    const unsigned int len = pmc.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 4, 1);
    const dim3 blk_ = BLOCKS(threads, len); 
    AT_DISPATCH_FLOATING_TYPES(pmc.scalar_type(), "M2", ([&]
    {
        Sq_ij_K<scalar_t><<< blk, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 3); 
        SumK<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 2); 
        Sub_ij_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 3, 0);
    }));  
    return pmc.index({torch::indexing::Slice(), 3}).view({-1, 1}); 
}

torch::Tensor _M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{
    torch::Tensor pmc = format({px, py, pz, e}); 
    return _M2(pmc);  
}

torch::Tensor _M(torch::Tensor pmc)
{
    pmc = pmc.contiguous().clone(); 
    CHECK_INPUT(pmc); 
    const unsigned int len = pmc.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 4, 1);
    const dim3 blk_ = BLOCKS(threads, len); 
    AT_DISPATCH_FLOATING_TYPES(pmc.scalar_type(), "M", ([&]
    {
        Sq_ij_K<scalar_t><<< blk, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 3); 
        SumK<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 2); 
        Sub_ij_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 3, 0);
        Sqrt_i_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 3); 
    }));  
    return pmc.index({torch::indexing::Slice(), 3}).view({-1, 1}); 
}

torch::Tensor _M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{
    torch::Tensor pmc = format({px, py, pz, e}); 
    return _M(pmc);  
}

torch::Tensor _Mt2(torch::Tensor pmc)
{
    pmc = pmc.contiguous().clone(); 
    CHECK_INPUT(pmc); 
    const unsigned int len = pmc.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 2, 1);
    const dim3 blk_ = BLOCKS(threads, len); 
    AT_DISPATCH_FLOATING_TYPES(pmc.scalar_type(), "Mt2", ([&]
    {
        Sq_ij_K<scalar_t><<< blk, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 2, 3); 
        Sub_ij_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 3, 2);
    }));  
    return pmc.index({torch::indexing::Slice(), 3}).view({-1, 1}); 
}

torch::Tensor _Mt2(torch::Tensor pz, torch::Tensor e)
{
    torch::Tensor pmc = format({pz, e}); 
    pmc = pmc.contiguous(); 
    CHECK_INPUT(pmc); 
    const unsigned int len = pmc.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 2, 1);
    const dim3 blk_ = BLOCKS(threads, len); 
    AT_DISPATCH_FLOATING_TYPES(pmc.scalar_type(), "Mt2", ([&]
    {
        Sq_ij_K<scalar_t><<< blk, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 1); 
        Sub_ij_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 1, 0);
    }));  
    return pmc.index({torch::indexing::Slice(), 1}).view({-1, 1});            
}

torch::Tensor _Mt(torch::Tensor pmc)
{
    pmc = pmc.contiguous().clone(); 
    CHECK_INPUT(pmc); 
    const unsigned int len = pmc.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 2, 1);
    const dim3 blk_ = BLOCKS(threads, len); 
    AT_DISPATCH_FLOATING_TYPES(pmc.scalar_type(), "Mt", ([&]
    {
        Sq_ij_K<scalar_t><<< blk, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 2, 3); 
        Sub_ij_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 3, 2);
        Sqrt_i_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 3);
    }));  
    return pmc.index({torch::indexing::Slice(), 3}).view({-1, 1}); 
}

torch::Tensor _Mt(torch::Tensor pz, torch::Tensor e)
{
    torch::Tensor pmc = format({pz, e}); 

    pmc = pmc.contiguous(); 
    CHECK_INPUT(pmc); 
    const unsigned int len = pmc.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 2, 1);
    const dim3 blk_ = BLOCKS(threads, len); 
    AT_DISPATCH_FLOATING_TYPES(pmc.scalar_type(), "Mt", ([&]
    {
        Sq_ij_K<scalar_t><<< blk, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 1); 
        Sub_ij_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 1, 0);
        Sqrt_i_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 1); 
    }));  
    return pmc.index({torch::indexing::Slice(), 1}).view({-1, 1});            
}

torch::Tensor _Theta(torch::Tensor pmc_)
{
    torch::Tensor pmc = pmc_.contiguous().clone(); 
    CHECK_INPUT(pmc); CHECK_INPUT(pmc_); 
    const unsigned int len = pmc.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 3, 1);
    const dim3 blk_ = BLOCKS(threads, len); 
    AT_DISPATCH_FLOATING_TYPES(pmc.scalar_type(), "Theta", ([&]
    {
        Sq_ij_K<scalar_t><<< blk, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 2);
        SumK<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 2); 
        Sqrt_i_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0); 
        ArcCos_ij_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                pmc_.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 2); 
    })); 
    return pmc.index({torch::indexing::Slice(), 0}).view({-1, 1}); 
}

torch::Tensor _Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
    pz = pz.view({-1, 1}).contiguous(); 
    torch::Tensor pmc = format({px, py, pz}); 

    CHECK_INPUT(pmc); CHECK_INPUT(pz); 
    const unsigned int len = pmc.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 3, 1);
    const dim3 blk_ = BLOCKS(threads, len); 
    AT_DISPATCH_FLOATING_TYPES(pmc.scalar_type(), "Theta", ([&]
    {
        Sq_ij_K<scalar_t><<< blk, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 2);
        SumK<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 2); 
        Sqrt_i_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0); 
        ArcCos_ij_K<scalar_t><<< blk_, threads >>>(
                pmc.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 0); 
    })); 
    return pmc.index({torch::indexing::Slice(), 0}).view({-1, 1}); 
}

torch::Tensor _DeltaR(torch::Tensor pmu1, torch::Tensor pmu2)
{
    torch::Tensor eta_phi = torch::cat({
            pmu1.index({torch::indexing::Slice(), torch::indexing::Slice(1, 2)}), 
            pmu2.index({torch::indexing::Slice(), torch::indexing::Slice(1, 2)}), 
            pmu1.index({torch::indexing::Slice(), torch::indexing::Slice(2, 3)}), 
            pmu2.index({torch::indexing::Slice(), torch::indexing::Slice(2, 3)})
            }, -1).contiguous(); 

    CHECK_INPUT(eta_phi); 
    const unsigned int len = eta_phi.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 2, 1); 
    const dim3 blk_ = BLOCKS(threads, len); 
    
    AT_DISPATCH_FLOATING_TYPES(eta_phi.scalar_type(), "dR", ([&]
    {
        delta_K<scalar_t><<< blk, threads >>>(
                eta_phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len); 
        Sum_ij_K<scalar_t><<< blk_, threads >>>(
                eta_phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 2); 
        Sqrt_i_K<scalar_t><<< blk_, threads >>>(
                eta_phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0); 
    }));
    return eta_phi.index({torch::indexing::Slice(), 0}).view({-1, 1}); 
}

torch::Tensor _DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2)
{
    torch::Tensor eta_phi = format({eta1, eta2, phi1, phi2}).contiguous(); 
    CHECK_INPUT(eta_phi); 
    const unsigned int len = eta_phi.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, len, 2, 1); 
    const dim3 blk_ = BLOCKS(threads, len); 
    
    AT_DISPATCH_FLOATING_TYPES(eta_phi.scalar_type(), "dR", ([&]
    {
        delta_K<scalar_t><<< blk, threads >>>(
                eta_phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len); 
        Sum_ij_K<scalar_t><<< blk_, threads >>>(
                eta_phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0, 2); 
        Sqrt_i_K<scalar_t><<< blk_, threads >>>(
                eta_phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len, 0); 
    }));
    return eta_phi.index({torch::indexing::Slice(), 0}).view({-1, 1}); 
}
#endif
