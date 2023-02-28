#include <torch/extension.h>
#include "Polar.cu"

template <typename scalar_t>
__global__ void _PtK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> px, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> py, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _pt)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 

	if (indx >= _pt.size(0)){return;}
	_pxpy_pt(&_pt[indx][0], &px[indx][0], &py[indx][0]); 
}

template <typename scalar_t>
__global__ void _PhiK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> px, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> py, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _phi)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 

	if (indx >= _phi.size(0)){return;}
	_pxpy_phi(&_phi[indx][0], &px[indx][0], &py[indx][0]); 
}

template <typename scalar_t>
__global__ void _EtaK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> px, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> py, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pz, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _eta)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 

	if (indx >= _eta.size(0)){return;}
	_pxpypz_eta(&_eta[indx][0], &px[indx][0], &py[indx][0], &pz[indx][0]); 
}

template <typename scalar_t>
__global__ void _PtEtaPhiK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> px, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> py, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> pz, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _out)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y; 
	if (indx >= _out.size(0)){return;}
	if (indy == 0){ _pxpypz_pteta(&_out[indx][0], &_out[indx][1], &px[indx][0], &py[indx][0], &pz[indx][0]); return; }
	if (indy == 1){ _pxpy_phi(&_out[indx][2], &px[indx][0], &py[indx][0]); return; }
}
