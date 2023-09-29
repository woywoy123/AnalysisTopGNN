#include "PolarKernel.cu"

torch::Tensor _Pt(torch::Tensor _px, torch::Tensor _py)
{
	_px = _px.view({-1, 1}); 
	_py = _py.view({-1, 1});
	torch::Tensor _pt = torch::zeros_like(_py); 
	
	const int l = _pt.size(0);
	const int threads = 1024; 
	const dim3 blocks((l+threads -1)/threads); 
	
	AT_DISPATCH_FLOATING_TYPES(_px.scalar_type(), "_PtK", ([&]
	{
		_PtK<scalar_t><<<blocks, threads>>>(
				_px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_pt.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>()
		); 
	}));
	return _pt; 
}

torch::Tensor _Phi(torch::Tensor _px, torch::Tensor _py)
{
	_px = _px.view({-1, 1}); 
	_py = _py.view({-1, 1});
	torch::Tensor _phi = torch::zeros_like(_py); 
	
	const int l = _phi.size(0);
	const int threads = 1024; 
	const dim3 blocks((l+threads -1)/threads); 
	
	AT_DISPATCH_FLOATING_TYPES(_px.scalar_type(), "_PhiK", ([&]
	{
		_PhiK<scalar_t><<<blocks, threads>>>(
				_px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_phi.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>()
		); 
	}));
	return _phi; 
}

torch::Tensor _Eta(torch::Tensor _px, torch::Tensor _py, torch::Tensor _pz)
{
	_px = _px.view({-1, 1}); 
	_py = _py.view({-1, 1});
	_pz = _pz.view({-1, 1});
	torch::Tensor _eta = torch::zeros_like(_py); 
	
	const int l = _eta.size(0);
	const int threads = 1024; 
	const dim3 blocks((l+threads -1)/threads); 
	
	AT_DISPATCH_FLOATING_TYPES(_px.scalar_type(), "_EtaK", ([&]
	{
		_EtaK<scalar_t><<<blocks, threads>>>(
				_px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_eta.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>()
		); 
	}));
	return _eta; 
}

torch::Tensor _PtEtaPhi(torch::Tensor _px, torch::Tensor _py, torch::Tensor _pz)
{
	_px = _px.view({-1, 1}); 
	_py = _py.view({-1, 1});
	_pz = _pz.view({-1, 1});
	torch::Tensor _out = torch::zeros_like(_py); 
	_out = torch::cat({_out, _out, _out}, -1); 

	const int l = _px.size(0);
	const int threads = 1024; 
	const dim3 blocks((l+threads -1)/threads, 2); 
	
	AT_DISPATCH_FLOATING_TYPES(_px.scalar_type(), "_PtEtaPhiK", ([&]
	{
		_PtEtaPhiK<scalar_t><<<blocks, threads>>>(
				_px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>()
		); 
	}));
	return _out; 
}
