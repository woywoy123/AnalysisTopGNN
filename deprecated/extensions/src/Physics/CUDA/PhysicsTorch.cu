#include "../../Operators/CUDA/OperatorsKernel.cu"
#include "PhysicsKernel.cu"

torch::Tensor _P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
	const int l = px.size(0); 
	const int threads = 1024; 	
	const dim3 blocks((l + threads -1) / threads); 
	torch::Tensor _p2 = torch::zeros_like(px);

	AT_DISPATCH_FLOATING_TYPES(pz.scalar_type(), "_P2K", ([&] 
	{
		_P2K<scalar_t><<<blocks, threads>>>(
				px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_p2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_P2K<scalar_t><<<blocks, threads>>>(
				py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_p2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_P2K<scalar_t><<<blocks, threads>>>(
				pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_p2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
	})); 

	return _p2; 
}

torch::Tensor _P(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
	const int l = px.size(0); 
	const int threads = 1024; 	
	const dim3 blocks((l + threads -1) / threads); 
	torch::Tensor _p = torch::zeros_like(px);
	
	AT_DISPATCH_FLOATING_TYPES(pz.scalar_type(), "_PK", ([&] 
	{
		_P2K<scalar_t><<<blocks, threads>>>(
				px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_p.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_P2K<scalar_t><<<blocks, threads>>>(
				py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_p.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_P2K<scalar_t><<<blocks, threads>>>(
				pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_p.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);
		_SqrtK<scalar_t><<<blocks, threads>>>(
				_p.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
	})); 
	return _p; 
}

torch::Tensor _Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{
	const int l = px.size(0); 
	const int threads = 1024; 	
	const dim3 blocks((l + threads -1) / threads); 
	torch::Tensor _b2 = torch::zeros_like(px);
	
	AT_DISPATCH_FLOATING_TYPES(pz.scalar_type(), "_PK", ([&] 
	{
		_P2K<scalar_t><<<blocks, threads>>>(
				px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_b2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_P2K<scalar_t><<<blocks, threads>>>(
				py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_b2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_P2K<scalar_t><<<blocks, threads>>>(
				pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_b2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);
		_Beta2K<scalar_t><<<blocks, threads>>>(
				e.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				_b2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
	})); 
	return _b2; 
}


torch::Tensor _Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{
	const int l = px.size(0); 
	const int threads = 1024; 	
	const dim3 blocks((l + threads -1) / threads); 
	torch::Tensor _b = torch::zeros_like(px);
	
	AT_DISPATCH_FLOATING_TYPES(pz.scalar_type(), "_PK", ([&] 
	{
		_P2K<scalar_t><<<blocks, threads>>>(
				px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_b.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_P2K<scalar_t><<<blocks, threads>>>(
				py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_b.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_P2K<scalar_t><<<blocks, threads>>>(
				pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_b.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);
		_SqrtK<scalar_t><<<blocks, threads>>>(
				_b.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_DivK<scalar_t><<<blocks, threads>>>(
				_b.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				e.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				_b.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
	})); 
	return _b; 
}

torch::Tensor _M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{
	const int l = px.size(0); 
	const int threads = 1024; 	
	const dim3 blocks((l + threads -1) / threads); 
	torch::Tensor _m2 = torch::zeros_like(px);
	
	AT_DISPATCH_FLOATING_TYPES(pz.scalar_type(), "_PK", ([&] 
	{
		_P2K<scalar_t><<<blocks, threads>>>(
				px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_m2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_P2K<scalar_t><<<blocks, threads>>>(
				py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_m2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_P2K<scalar_t><<<blocks, threads>>>(
				pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_m2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);
		_SubPowv1_v2K<scalar_t><<<blocks, threads>>>(
				e.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_m2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);
	})); 
	return _m2;
}

torch::Tensor _M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{
	const int l = px.size(0); 
	const int threads = 1024; 	
	const dim3 blocks((l + threads -1) / threads); 
	torch::Tensor _m = torch::zeros_like(px);
	
	AT_DISPATCH_FLOATING_TYPES(pz.scalar_type(), "_PK", ([&] 
	{
		_P2K<scalar_t><<<blocks, threads>>>(
				px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_m.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_P2K<scalar_t><<<blocks, threads>>>(
				py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_m.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_P2K<scalar_t><<<blocks, threads>>>(
				pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_m.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);
		_SubPowv1_v2K<scalar_t><<<blocks, threads>>>(
				e.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_m.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);
		_SqrtK<scalar_t><<<blocks, threads>>>(
				_m.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
	})); 
	return _m;
}


torch::Tensor _Mt2(torch::Tensor pz, torch::Tensor e)
{
	const int l = pz.size(0); 
	const int threads = 1024; 	
	const dim3 blocks((l + threads -1) / threads); 
	torch::Tensor _mt2 = torch::zeros_like(pz);
	
	AT_DISPATCH_FLOATING_TYPES(pz.scalar_type(), "_PK", ([&] 
	{
		_P2K<scalar_t><<<blocks, threads>>>(
				pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_mt2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
		_SubPowv1_v2K<scalar_t><<<blocks, threads>>>(
				e.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_mt2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);
	})); 
	return _mt2;
}

torch::Tensor _Mt(torch::Tensor pz, torch::Tensor e)
{
	const int l = pz.size(0); 
	const int threads = 1024; 	
	const dim3 blocks((l + threads -1) / threads); 
	torch::Tensor _mt = torch::zeros_like(pz);
	
	AT_DISPATCH_FLOATING_TYPES(pz.scalar_type(), "_PK", ([&] 
	{
		_P2K<scalar_t><<<blocks, threads>>>(
				pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_mt.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);
		_SubPowv1_v2K<scalar_t><<<blocks, threads>>>(
				e.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_mt.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);
		_SqrtK<scalar_t><<<blocks, threads>>>(
				_mt.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
	})); 
	return _mt;
}

torch::Tensor _Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
	const int l = pz.size(0); 
	const int threads = 1024; 	
	const dim3 blocks((l + threads -1) / threads); 
	torch::Tensor _theta = torch::zeros_like(pz);

	AT_DISPATCH_FLOATING_TYPES(pz.scalar_type(), "_PK", ([&] 
	{
		_P2K<scalar_t><<<blocks, threads>>>(
				pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_theta.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);

		_P2K<scalar_t><<<blocks, threads>>>(
				py.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_theta.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);

		_P2K<scalar_t><<<blocks, threads>>>(
				px.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_theta.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);

		_SqrtK<scalar_t><<<blocks, threads>>>(
				_theta.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 

		_acos_v1_v2K<scalar_t><<<blocks, threads>>>(
				pz.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_theta.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				_theta.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);
	})); 
	return _theta;
}


torch::Tensor _DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2)
{
	const int l = eta1.size(0); 
	const int threads = 1024; 	
	const dim3 blocks((l + threads -1) / threads); 
	torch::Tensor _dR = torch::zeros_like(eta1);
	
	AT_DISPATCH_FLOATING_TYPES(phi2.scalar_type(), "_PK", ([&] 
	{
		_Diff_pow2_v1_v2K<scalar_t><<<blocks, threads>>>(
				eta1.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				eta2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_dR.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);

		_Diff_pow2_v1_v2K_bfly<scalar_t><<<blocks, threads>>>(
				phi1.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				phi2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_dR.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		);

		_SqrtK<scalar_t><<<blocks, threads>>>(
				_dR.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				l
		); 
	})); 
	return _dR;
}
