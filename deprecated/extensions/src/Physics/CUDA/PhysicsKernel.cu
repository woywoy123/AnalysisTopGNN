#include <torch/extension.h>
#include "Physics.cu"

template <typename scalar_t>
__global__ void _P2K(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _p, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _p2, 
		const int x)
{
	const int indx = blockIdx.x * blockDim.x + threadIdx.x; 
	if (indx >= x){return;}
	_p2[indx][0] += _pow(_p[indx][0]);  
}

template <typename scalar_t>
__global__ void _SqrtK(
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _p, 
		const int x)
{
	const int indx = blockIdx.x * blockDim.x + threadIdx.x; 
	if (indx >= x){return;}
	_p[indx][0] = _sqrt(_p[indx][0]);  
}

template <typename scalar_t>
__global__ void _Beta2K(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _e,
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _p, 
		const int x)
{
	const int indx = blockIdx.x * blockDim.x + threadIdx.x;
	if (indx >= x) {return;}
	_p[indx][0] = _div_e2(_p[indx][0], _e[indx][0]); 
}

template <typename scalar_t>
__global__ void _DivK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v1,
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v2, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v, 
		const int x)
{
	const int indx = blockIdx.x * blockDim.x + threadIdx.x;
	if (indx >= x) {return;}
	_v[indx][0] = _div_v1_v2(_v1[indx][0], _v2[indx][0]); 
}

template <typename scalar_t>
__global__ void _SubPowv1_v2K(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v1,
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v, 
		const int x)
{
	const int indx = blockIdx.x * blockDim.x + threadIdx.x;
	if (indx >= x) {return;}
	_v[indx][0] = _sub_v1pow2_v2(_v1[indx][0], _v[indx][0]); 
}

template <typename scalar_t>
__global__ void _acos_v1_v2K(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v1,
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v2, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v, 
		const int x)
{
	const int indx = blockIdx.x * blockDim.x + threadIdx.x;
	if (indx >= x) {return;}
	_v[indx][0] = _acos_v1_v2(_v1[indx][0], _v2[indx][0]); 
}

template <typename scalar_t>
__global__ void _Diff_pow2_v1_v2K(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v1,
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v2, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v, 
		const int x)
{
	const int indx = blockIdx.x * blockDim.x + threadIdx.x;
	if (indx >= x) {return;}
	_v[indx][0] += _diff_pow2_v1_v2(_v1[indx][0], _v2[indx][0]); 
}

template <typename scalar_t>
__global__ void _Diff_pow2_v1_v2K_bfly(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v1,
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v2, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v, 
		const int x)
{
	const int indx = blockIdx.x * blockDim.x + threadIdx.x;
	if (indx >= x) {return;}
	_v[indx][0] += _diff_pow2_v1_v2_bfly(_v1[indx][0], _v2[indx][0]); 
}
