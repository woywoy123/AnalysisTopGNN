#ifndef OPERATORS_CUDA_KERNEL_H
#define OPERATORS_CUDA_KERNEL_H
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
    const unsigned int threads, const unsigned int len, const unsigned int dy)
{
    const dim3 blocks( (len + threads -1) / threads, dy); 
    return blocks; 
}

static const dim3 BLOCKS(
    const unsigned int threads, const unsigned int len, 
    const unsigned int dy, const unsigned int dz)
{
    const dim3 blocks( (len + threads -1) / threads, dy, dz); 
    return blocks; 
}

torch::TensorOptions _MakeOp(torch::Tensor v1)
{
	return torch::TensorOptions().dtype(v1.scalar_type()).device(v1.device()); 
}

torch::Tensor _Dot(torch::Tensor v1, torch::Tensor v2)
{
    torch::Tensor out = v1.contiguous().clone();
    CHECK_INPUT(out); CHECK_INPUT(v2);  
    const unsigned int len_i = v1.size(0); 
    const unsigned int len_j = v1.size(1); 
    const unsigned int threads = 1024; 
    const dim3 blk  = BLOCKS(threads, len_i, len_j); 
    const dim3 blk_ = BLOCKS(threads, len_i); 
    AT_DISPATCH_FLOATING_TYPES(v1.scalar_type(), "DOT", ([&]
    {
        _DotK<scalar_t><<< blk, threads >>>( 
                out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                 v2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len_i, len_j); 
        _SumK<scalar_t><<< blk_, threads >>>(
                out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                len_i, len_j); 
    })); 
    return out.index({torch::indexing::Slice(), 0}).view({-1, 1}); 
}

torch::Tensor _Mul(torch::Tensor v1, torch::Tensor v2)
{
    const torch::TensorOptions op = _MakeOp(v1); 
    const unsigned int  n_ten = v1.size(0); 
    const unsigned int threads = 1024; 

    // these need to be the same for contraction
    const unsigned int len_k1 = v1.size(2); 
    const unsigned int len_j2 = v2.size(1); 
    const unsigned int len_dim = (len_k1 > len_j2) ? len_j2 : len_k1; 

    const unsigned int len_j1 = v1.size(1); 
    const unsigned int len_k2 = v2.size(2); 

    torch::Tensor out  = torch::zeros({n_ten, len_j1, len_k2, len_dim}, op); 
    torch::Tensor out_ = torch::zeros({n_ten, len_j1, len_k2}, op); 
  
    const dim3 blk = BLOCKS(threads, n_ten, len_k2*len_j1, len_dim); 
    const dim3 blks = BLOCKS(threads, n_ten, len_j1, len_k2); 
    AT_DISPATCH_FLOATING_TYPES(out.scalar_type(), "MUL", ([&]
    {
        _DotK<scalar_t><<< blk, threads >>>(
                out.packed_accessor64<scalar_t, 4, torch::RestrictPtrTraits>(), 
                v1.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                v2.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                n_ten, len_j1, len_k2, len_dim); 
        
        _SumK<scalar_t><<< blks, threads >>>(
                out_.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(),
                out.packed_accessor64<scalar_t, 4, torch::RestrictPtrTraits>(),
                n_ten, len_j1, len_k2, len_dim);
    })); 
    return out_;
}

torch::Tensor _CosTheta(torch::Tensor v1, torch::Tensor v2, signed int limit)
{
    const unsigned int x = v1.size(0); 
    const unsigned int y = (limit < 0) ? v1.size(1) : limit; 
    const unsigned int threads = 1024; 

    v2 = v2.contiguous(); 
    v1 = v1.contiguous(); 
    torch::Tensor tmp = torch::zeros({x, y, 3}, _MakeOp(v1));
    torch::Tensor out = torch::zeros({x, 3}, _MakeOp(v1));  
    CHECK_INPUT(v1); CHECK_INPUT(v2); 
    const dim3 blk   = BLOCKS(threads, x, y, 3); 
    const dim3 blk_  = BLOCKS(threads, x, 3); 
    const dim3 blk__ = BLOCKS(threads, x); 
    AT_DISPATCH_FLOATING_TYPES(v1.scalar_type(), "COSTHETA", ([&]
    {
        _DotK<scalar_t><<< blk, threads >>>(
                tmp.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                v1.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                v2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                x, y);
        _SumK<scalar_t><<< blk_, threads >>>(
                out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                tmp.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(),
                x, y); 
        _CosThetaK<scalar_t><<< blk__, threads >>>(
                out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                x); 
    })); 
    return out.index({torch::indexing::Slice(), 0}).view({-1, 1}); 
}

torch::Tensor _SinTheta(torch::Tensor v1, torch::Tensor v2, signed int limit)
{
    const unsigned int x = v1.size(0); 
    const unsigned int y = (limit < 0) ? v1.size(1) : limit; 
    const unsigned int threads = 1024; 

    v2 = v2.contiguous(); 
    v1 = v1.contiguous(); 
    torch::Tensor tmp = torch::zeros({x, y, 3}, _MakeOp(v1));
    torch::Tensor out = torch::zeros({x, 3}, _MakeOp(v1));  
    CHECK_INPUT(v1); CHECK_INPUT(v2); 
    const dim3 blk = BLOCKS(threads, x, y, 3); 
    const dim3 blk_ = BLOCKS(threads, x, 3); 
    const dim3 blk__ = BLOCKS(threads, x); 
    AT_DISPATCH_FLOATING_TYPES(v1.scalar_type(), "SINTHETA", ([&]
    {
        _DotK<scalar_t><<< blk, threads >>>(
                tmp.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                v1.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                v2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                x, y);
        _SumK<scalar_t><<< blk_, threads >>>(
                out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                tmp.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(),
                x, y); 
        _SinThetaK<scalar_t><<< blk__, threads >>>(
                out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                x); 
    })); 
    return out.index({torch::indexing::Slice(), 0}).view({-1, 1}); 
}

torch::Tensor _Rot(torch::Tensor angle, const unsigned int dim)
{
    const unsigned int x = angle.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, x, 3, 3); 
    angle = angle.view({-1, 1}).contiguous(); 
    CHECK_INPUT(angle); 

    torch::Tensor out = torch::zeros({x, 3, 3}, _MakeOp(angle));
    AT_DISPATCH_FLOATING_TYPES(angle.scalar_type(), "Rot", ([&]
    {
        _RotK<scalar_t><<< blk, threads >>>(
                out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                angle.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                x, dim); 
    })); 
    return out; 
}

torch::Tensor _CoFactors(torch::Tensor matrix)
{
    const unsigned int x = matrix.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, x, 3, 3);  
    torch::Tensor out = torch::zeros_like(matrix);
    CHECK_INPUT(matrix);  


    unsigned int size = sizeof(unsigned int)*12; 
    unsigned int *dy, *dz; 

    unsigned int _dy[12] = {
        1, 1, 2, 2, 
        0, 0, 2, 2, 
        0, 0, 1, 1
    }; 

    unsigned int _dz[12] = {
        1, 2, 1, 2, 
        0, 2, 0, 2, 
        0, 1, 0, 1
    }; 

    cudaMalloc(&dy, size); 
    cudaMalloc(&dz, size); 
    cudaMemcpy(dy, &_dy, size, cudaMemcpyHostToDevice); 
    cudaMemcpy(dz, &_dz, size, cudaMemcpyHostToDevice); 

    AT_DISPATCH_FLOATING_TYPES(matrix.scalar_type(), "Cofactor", ([&]
    {
        _CoFactorK<scalar_t><<< blk, threads >>>(
                out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                matrix.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                x, 3, dy, dz); 
    })); 

    cudaFree(dy); 
    cudaFree(dz); 
    return out; 
}

torch::Tensor _Det(torch::Tensor matrix)
{
    const unsigned int x = matrix.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, x, 1, 3);
    const dim3 blk_ = BLOCKS(threads, x);
    torch::Tensor tmp = torch::zeros({x, 1, 3}, _MakeOp(matrix));
    torch::Tensor out = torch::zeros({x, 1}, _MakeOp(matrix));

    unsigned int size = sizeof(unsigned int)*12; 
    unsigned int *dy, *dz; 

    unsigned int _dy[12] = {
        1, 1, 2, 2, 
        0, 0, 2, 2, 
        0, 0, 1, 1
    }; 

    unsigned int _dz[12] = {
        1, 2, 1, 2, 
        0, 2, 0, 2, 
        0, 1, 0, 1
    }; 

    cudaMalloc(&dy, size); 
    cudaMalloc(&dz, size); 
    cudaMemcpy(dy, &_dy, size, cudaMemcpyHostToDevice); 
    cudaMemcpy(dz, &_dz, size, cudaMemcpyHostToDevice); 

    AT_DISPATCH_FLOATING_TYPES(matrix.scalar_type(), "Determinant", ([&]
    {
        _CoFactorK<scalar_t><<< blk, threads >>>(
                tmp.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                matrix.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                x, 1, dy, dz); 

        _DetDotK<scalar_t><<< blk, threads >>>(
                tmp.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                tmp.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                matrix.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                x);

        _DetSumK<scalar_t><<< blk_, threads >>>(
                out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                tmp.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                x);
    })); 
    
    cudaFree(dy); 
    cudaFree(dz); 
    return out; 
}

std::tuple<torch::Tensor, torch::Tensor> _Inv(torch::Tensor matrix)
{
    const unsigned int x = matrix.size(0); 
    const unsigned int threads = 1024; 
    const dim3 blk_ = BLOCKS(threads, x);
    const dim3 blk__ = BLOCKS(threads, x, 1, 3);
    const dim3 blk = BLOCKS(threads, x, 3, 3);
    torch::Tensor coef = torch::zeros({x, 3, 3}, _MakeOp(matrix));
    torch::Tensor det = torch::zeros({x, 1}, _MakeOp(matrix));
    torch::Tensor out = torch::zeros({x, 3, 3}, _MakeOp(matrix));

    unsigned int size = sizeof(unsigned int)*12; 
    unsigned int *dy, *dz; 

    unsigned int _dy[12] = {
        1, 1, 2, 2, 
        0, 0, 2, 2, 
        0, 0, 1, 1
    }; 

    unsigned int _dz[12] = {
        1, 2, 1, 2, 
        0, 2, 0, 2, 
        0, 1, 0, 1
    }; 

    cudaMalloc(&dy, size); 
    cudaMalloc(&dz, size); 
    cudaMemcpy(dy, &_dy, size, cudaMemcpyHostToDevice); 
    cudaMemcpy(dz, &_dz, size, cudaMemcpyHostToDevice); 

    AT_DISPATCH_FLOATING_TYPES(matrix.scalar_type(), "Determinant", ([&]
    {
        _CoFactorK<scalar_t><<< blk, threads >>>(
                  coef.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                matrix.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                x, 3, dy, dz); 

        _DetDotK<scalar_t><<< blk__, threads >>>(
                   out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                  coef.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                matrix.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                x);

        _DetSumK<scalar_t><<< blk_, threads >>>(
                det.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                x);
    
        _InvK<scalar_t><<< blk, threads >>>(
                 out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                 det.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
                coef.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                x);
    })); 

    cudaFree(dy); 
    cudaFree(dz);  
    return {out, det == 0}; 
}

torch::Tensor _Cross(torch::Tensor mat1, torch::Tensor mat2)
{
    const unsigned int x = mat1.size(0)*3; 
    const unsigned int threads = 1024; 
    const dim3 blk = BLOCKS(threads, x, 1, 3); 
    torch::Tensor form = torch::zeros({x, 3, 3}, _MakeOp(mat1));
    torch::Tensor out  = torch::zeros({x, 1, 3}, _MakeOp(mat1));

    unsigned int size = sizeof(unsigned int)*12; 
    unsigned int *dy, *dz; 

    unsigned int _dy[12] = {
        1, 1, 2, 2, 
        0, 0, 2, 2, 
        0, 0, 1, 1
    }; 

    unsigned int _dz[12] = {
        1, 2, 1, 2, 
        0, 2, 0, 2, 
        0, 1, 0, 1
    }; 

    cudaMalloc(&dy, size); 
    cudaMalloc(&dz, size); 
    cudaMemcpy(dy, &_dy, size, cudaMemcpyHostToDevice); 
    cudaMemcpy(dz, &_dz, size, cudaMemcpyHostToDevice); 

    AT_DISPATCH_FLOATING_TYPES(mat1.scalar_type(), "Cross", ([&]
    {
        _CrossK<scalar_t><<< blk, threads >>>(
                form.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                mat1.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                mat2.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                x); 

        _CoFactorK<scalar_t><<< blk, threads >>>(
                out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
                form.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(),                
                x, 1, dy, dz); 
    })); 
    
    cudaFree(dy); 
    cudaFree(dz);  
    return out.view({-1, 3, 3});  
}

#endif
