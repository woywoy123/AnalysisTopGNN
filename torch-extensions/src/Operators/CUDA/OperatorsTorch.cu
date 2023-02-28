#include "OperatorsKernel.cu"

torch::TensorOptions _MakeOp(torch::Tensor v1)
{
	return torch::TensorOptions().dtype(v1.scalar_type()).device(v1.device()); 
}


torch::Tensor _Dot(torch::Tensor v1, torch::Tensor v2)
{
	const int l = v1.size(0);
	const int d = v1.size(1); 
	const int threads = 1024; 
	torch::Tensor _out = torch::zeros_like(v1); 
	
	const dim3 blocks((l + threads -1) / threads, d); 
	AT_DISPATCH_FLOATING_TYPES(v1.scalar_type(), "_Dot2K", ([&]
	{
		_Dot2K<scalar_t><<<blocks, threads>>>(
				v1.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				v2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				l, d
		); 
	})); 

	return _out; 
}

torch::Tensor _Mul(torch::Tensor v1, torch::Tensor v2)
{
	const int x = v1.size(0); 
	const int _t = v1.size(-1);
	const int y = v1.size(-2); 
	const int z = v2.size(-1);

	const int threads = 1024; 
	const dim3 blocks((x + threads -1) / threads, _t*z*y); 
	const dim3 blocks2((x + threads -1) / threads, y, z); 
	
	torch::Tensor _tmp = torch::zeros({x, _t, y, z}, _MakeOp(v1)); 
	torch::Tensor _out = torch::zeros({x, y, z}, _MakeOp(v1));

	AT_DISPATCH_FLOATING_TYPES(v1.scalar_type(), "_Dot3K", ([&]
	{
		_Dot3K<scalar_t><<<blocks, threads>>>(
				v1.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				v2.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_tmp.packed_accessor64<scalar_t, 4, torch::RestrictPtrTraits>(), 
				x, _t, y, z
		);
		_Sum3K<scalar_t><<<blocks2, threads>>>(
				_tmp.packed_accessor64<scalar_t, 4, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x, _t, y, z
		); 
	})); 
	return _out;
}

torch::Tensor _CosTheta(torch::Tensor v1, torch::Tensor v2)
{
	const int x = v1.size(0); 
	const int y = v1.size(1); 
	const int threads = 1024; 
	torch::Tensor _v12 = torch::zeros_like(v1);
	torch::Tensor _v22 = torch::zeros_like(v1);
	torch::Tensor _V1V2 = torch::zeros_like(v1);

	const dim3 blocks((x + threads -1) / threads, y); 
	const dim3 blocks2((x + threads -1) / threads); 
	AT_DISPATCH_FLOATING_TYPES(v1.scalar_type(), "_Dot2K", ([&]
	{
		_Dot2K<scalar_t><<<blocks, threads>>>(
				v1.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				v1.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_v12.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				x, y
		); 
		_Dot2K<scalar_t><<<blocks, threads>>>(
				v2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				v2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_v22.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				x, y
		); 
		_Dot2K<scalar_t><<<blocks, threads>>>(
				v1.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				v2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_V1V2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				x, y
		); 
	})); 
	_V1V2 = _V1V2.sum({-1}, true);
	_v12 = _v12.sum({-1}, true);
	_v22 = _v22.sum({-1}, true);
	AT_DISPATCH_FLOATING_TYPES(v1.scalar_type(), "_CosThetaK", ([&]
	{
		_CosThetaK<scalar_t><<<blocks2, threads>>>(
				_v12.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				_v22.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				_V1V2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				x
		); 
	})); 
	return _V1V2; 
}

torch::Tensor _Rx(torch::Tensor angle)
{
	const int threads = 1024; 
	const int x = angle.size(0); 
	torch::Tensor _rx = torch::zeros({x, 3, 3}, _MakeOp(angle)); 
	
	const dim3 blocks((x + threads -1) / threads, 3, 3); 
	AT_DISPATCH_FLOATING_TYPES(angle.scalar_type(), "_RxK", ([&]
	{
		_RxK<scalar_t><<<blocks, threads>>>(
				angle.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_rx.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>()
		); 
	})); 
	return _rx; 
}

torch::Tensor _Ry(torch::Tensor angle)
{
	const int threads = 1024; 
	const int x = angle.size(0); 
	torch::Tensor _ry = torch::zeros({x, 3, 3}, _MakeOp(angle)); 
	
	const dim3 blocks((x + threads -1) / threads, 3, 3); 
	AT_DISPATCH_FLOATING_TYPES(angle.scalar_type(), "_RyK", ([&]
	{
		_RyK<scalar_t><<<blocks, threads>>>(
				angle.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_ry.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>()
		); 
	})); 
	return _ry; 
}

torch::Tensor _Rz(torch::Tensor angle)
{
	const int threads = 1024; 
	const int x = angle.size(0); 
	torch::Tensor _rz = torch::zeros({x, 3, 3}, _MakeOp(angle)); 
	
	const dim3 blocks((x + threads -1) / threads, 3, 3); 
	AT_DISPATCH_FLOATING_TYPES(angle.scalar_type(), "_RzK", ([&]
	{
		_RzK<scalar_t><<<blocks, threads>>>(
				angle.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_rz.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>()
		); 
	})); 
	return _rz; 
}

torch::Tensor _Cofactors(torch::Tensor v1)
{
	const int threads = 1024; 
	const int x = v1.size(0); 
	const int y = v1.size(-2);
	const int z = v1.size(-1);
		
	torch::Tensor _out = torch::zeros_like(v1); 
	torch::Tensor _tmp = torch::zeros({x*y*z, 4}, _MakeOp(v1)); 
	
	const dim3 blocks((x + threads -1) / threads, y, z);

	AT_DISPATCH_FLOATING_TYPES(v1.scalar_type(), "_CoFactors", ([&]
	{
		_CoFactors<scalar_t><<<blocks, threads>>>(
				v1.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_tmp.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x, y, z
		); 
	})); 
	return _out;
}

torch::Tensor _Determinant(torch::Tensor Cofact, torch::Tensor Matrix)
{
	const int threads = 1024; 
	const int x = Matrix.size(0); 
	const int y = 3; 

	torch::Tensor _out = torch::zeros({x, y}, _MakeOp(Cofact)); 

	const dim3 blocks( (x + threads -1) / threads, y ); 

	AT_DISPATCH_FLOATING_TYPES(Cofact.scalar_type(), "_Determinant", ([&]
	{
		_Det<scalar_t><<<blocks, threads>>>(
				Matrix.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				Cofact.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				x, y
		); 
	}));

	return _out.sum(-1);	
}


torch::Tensor _Inverse(torch::Tensor Cofact, torch::Tensor Dets)
{
	const int threads = 1024; 
	const int x = Cofact.size(0); 
	const int y = Cofact.size(-2); 
	const int z = Cofact.size(-1); 

	torch::Tensor _out = torch::zeros_like(Cofact);  

	const dim3 blocks( (x + threads -1) / threads, y, z); 

	AT_DISPATCH_FLOATING_TYPES(Cofact.scalar_type(), "_Inverse", ([&]
	{
		_Inv<scalar_t><<<blocks, threads>>>(
				Cofact.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				Dets.packed_accessor64<scalar_t, 1, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x, y, z
		); 
	}));

	return _out;	
}

torch::Tensor _det(torch::Tensor Matrix)
{
	const int threads = 1024; 
	const int x = Matrix.size(0); 
	const int y = Matrix.size(-2); 
	const int z = Matrix.size(-1); 

	torch::Tensor _out = torch::zeros_like(Matrix); 
	torch::Tensor _tmp = torch::zeros({x*y*z, 4}, _MakeOp(Matrix)); 
	torch::Tensor _det = torch::zeros({x, y}, _MakeOp(Matrix)); 
	
	const dim3 blocks( (x + threads -1) / threads, y, z);
	const dim3 blocks2( (x + threads -1) / threads, y ); 

	AT_DISPATCH_FLOATING_TYPES(Matrix.scalar_type(), "_Det", ([&]
	{
		_CoFactors<scalar_t><<<blocks, threads>>>(
				Matrix.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_tmp.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x, y, z
		); 

		_Det<scalar_t><<<blocks2, threads>>>(
				Matrix.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_det.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				x, y
		);
		_det = _det.sum(-1);
	})); 

	return _det; 
}

torch::Tensor _inv(torch::Tensor Matrix)
{
	const int threads = 1024; 
	const int x = Matrix.size(0); 
	const int y = Matrix.size(-2); 
	const int z = Matrix.size(-1); 

	torch::Tensor _out = torch::zeros_like(Matrix); 
	torch::Tensor _tmp = torch::zeros({x*y*z, 4}, _MakeOp(Matrix)); 
	torch::Tensor _det = torch::zeros({x, y}, _MakeOp(Matrix)); 
	
	const dim3 blocks((x + threads -1) / threads, y, z);
	const dim3 blocks2( (x + threads -1) / threads, y ); 

	AT_DISPATCH_FLOATING_TYPES(Matrix.scalar_type(), "_Inverse", ([&]
	{
		_CoFactors<scalar_t><<<blocks, threads>>>(
				Matrix.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_tmp.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x, y, z
		); 

		_Det<scalar_t><<<blocks2, threads>>>(
				Matrix.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_det.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				x, y
		);
		_det = _det.sum(-1);
		_tmp = _tmp.view({-1, y, z}); 
		_Inv<scalar_t><<<blocks, threads>>>(
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_det.packed_accessor64<scalar_t, 1, torch::RestrictPtrTraits>(), 
				_tmp.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x, y, z
		); 
	})); 

	return _tmp.index({
			torch::indexing::Slice(torch::indexing::None, x), 
			torch::indexing::Slice(), 
			torch::indexing::Slice()}); 
}
