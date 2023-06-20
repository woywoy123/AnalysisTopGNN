#include <torch/torch.h>
#include <iostream>
#include "cartesian.cu"

template <typename scalar_t>
__global__ void _PxK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pt, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> phi, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _px)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 

	if (indx >= _px.size(0)){return;}
	_ptphi_to_px(&_px[indx][0], &pt[indx][0], &phi[indx][0]); 
}

template <typename scalar_t>
__global__ void _PyK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pt, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> phi, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _py)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 

	if (indx >= _py.size(0)){return;}
	_ptphi_to_py(&_py[indx][0], &pt[indx][0], &phi[indx][0]); 
}

template <typename scalar_t>
__global__ void _PzK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pt, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> eta, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _pz)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 

	if (indx >= _pz.size(0)){return;}
	_pteta_to_pz(&_pz[indx][0], &pt[indx][0], &eta[indx][0]); 
}

template <typename scalar_t>
__global__ void _PxPyPzK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pt, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> eta, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> phi, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _out)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y; 
	
	if (indx >= pt.size(0) || indy >= 3){ return; }
	if (indy == 0){_ptphi_to_px(&_out[indx][indy], &pt[indx][0], &phi[indx][0]); return; }
	if (indy == 1){_ptphi_to_py(&_out[indx][indy], &pt[indx][0], &phi[indx][0]); return; }
	if (indy == 2){_pteta_to_pz(&_out[indx][indy], &pt[indx][0], &eta[indx][0]); return; }
}

