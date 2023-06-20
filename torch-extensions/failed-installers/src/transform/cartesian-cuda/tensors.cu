#include <torch/torch.h>
#include "kernel.cu"
#include "cartesian.h"

#ifndef TENSOR_CARTESIAN_CUDA 
#define TENSOR_CARTESIAN_CUDA 

torch::Tensor _Px(torch::Tensor _pt, torch::Tensor _phi)
{
	_pt = _pt.view({-1, 1}); 
	_phi = _phi.view({-1, 1});
	torch::Tensor _px = torch::zeros_like(_pt); 
	
	const int l = _px.size(0);
	const int threads = 1024; 
	const dim3 blocks((l+threads -1)/threads); 
	
	AT_DISPATCH_FLOATING_TYPES(_pt.scalar_type(), "_PxK", ([&]
	{
		_PxK<scalar_t><<<blocks, threads>>>(
				_pt.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>()
		); 
	}));
	return _px; 
}

torch::Tensor _Py(torch::Tensor _pt, torch::Tensor _phi)
{
	_pt = _pt.view({-1, 1}); 
	_phi = _phi.view({-1, 1});
	torch::Tensor _py = torch::zeros_like(_pt); 
	
	const int l = _py.size(0);
	const int threads = 1024; 
	const dim3 blocks((l+threads -1)/threads); 
	
	AT_DISPATCH_FLOATING_TYPES(_pt.scalar_type(), "_PyK", ([&]
	{
		_PyK<scalar_t><<<blocks, threads>>>(
				_pt.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>()
		); 
	}));
	return _py; 
}

torch::Tensor _Pz(torch::Tensor _pt, torch::Tensor _eta)
{
	_pt = _pt.view({-1, 1}); 
	_eta = _eta.view({-1, 1});
	torch::Tensor _pz = torch::zeros_like(_pt); 
	
	const int l = _pz.size(0);
	const int threads = 1024; 
	const dim3 blocks((l+threads -1)/threads); 
	
	AT_DISPATCH_FLOATING_TYPES(_pt.scalar_type(), "_PzK", ([&]
	{
		_PzK<scalar_t><<<blocks, threads>>>(
				_pt.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_eta.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>()
		); 
	}));
	return _pz; 
}

torch::Tensor _PxPyPz(torch::Tensor _pt, torch::Tensor _eta, torch::Tensor _phi)
{
	_pt = _pt.view({-1, 1}); 
	_eta = _eta.view({-1, 1});
	_phi = _phi.view({-1, 1});
	torch::Tensor _out = torch::zeros_like(_pt);	
	_out = torch::cat({_out, _out, _out}, -1); 
	
	const int l = _out.size(0);
	const int threads = 1024; 
	const dim3 blocks((l+threads -1)/threads, 3, 1); 
	
	AT_DISPATCH_FLOATING_TYPES(_pt.scalar_type(), "_PxPyPzK", ([&]
	{
		_PxPyPzK<scalar_t><<<blocks, threads>>>(
				_pt.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),  
				_eta.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				_out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>()
		); 
	})); 
	return _out; 
}

#endif 
