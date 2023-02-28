#include "NuSolKernel.cu"
#include <iostream>

torch::Tensor _Solutions(
		torch::Tensor _muP2, torch::Tensor _bP2, 
		torch::Tensor _mu_e, torch::Tensor _b_e, 
		torch::Tensor _cos, torch::Tensor _sin,
		torch::Tensor mT2, torch::Tensor mW2, torch::Tensor mNu2)
{

	const int x = _mu_e.size(0);
	const int threads = 1024;
	
	const dim3 blocks1((x + threads -1)/threads, 10); 
	const dim3 blocks2((x + threads -1)/threads, 3);
	const dim3 blocks3((x + threads -1)/threads);

	torch::Tensor out_ = torch::zeros_like(_cos); 
	out_ = torch::cat({out_, out_, out_, 
			   out_, out_, out_, 
			   out_, out_, out_, 
			   out_, out_, out_, out_}, -1); 
	torch::Tensor bB_ = torch::zeros_like(_cos); 
	torch::Tensor muB_ = torch::zeros_like(_cos); 
	torch::Tensor muB2_ = torch::zeros_like(_cos); 

	//{ c_, s_, x0, x0p, Sx, Sy, w, w_, x1, y1, Z, O2, e2}
	//   0,  1,  2,   3,  4,  5, 6,  7,  8,  9,10, 11, 12

	// Calculates: bB, muB, muB2, x0p, x0, w_, w, 
	AT_DISPATCH_FLOATING_TYPES(out_.scalar_type(), "_SolsK", ([&]
	{
		_baseValsK<scalar_t><<<blocks1, threads>>>(
				_muP2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_bP2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_mu_e.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_b_e.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_cos.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				_sin.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				mT2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				mW2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				mNu2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				out_.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				bB_.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				muB_.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				muB2_.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				x, 10
		); 
		_baseValsK<scalar_t><<<blocks2, threads>>>(
				muB2_.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				muB_.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_muP2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				out_.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				x, 3
		); 

		_baseVals_K<scalar_t><<<blocks3, threads>>>(
				bB_.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_cos.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				_sin.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				out_.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				x
		); 

		_baseValsK<scalar_t><<<blocks2, threads>>>(
				mW2.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				out_.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				x, 3
		); 

		_baseValsK<scalar_t><<<blocks3, threads>>>(
				out_.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(), 
				x
		); 
	})); 
	return out_;  
}

torch::Tensor _H_Matrix(torch::Tensor sols, torch::Tensor mu_P)
{
	const int x = sols.size(0); 
	const int threads = 1024; 
	const dim3 blocks( (x + threads -1)/threads, 3, 3); 
	torch::Tensor out_ = torch::zeros(
			{x, 3, 3}, 
			torch::TensorOptions().dtype(sols.dtype()).device(sols.device())); 
	
	AT_DISPATCH_FLOATING_TYPES(out_.scalar_type(), "_H", ([&]
	{
		_HMatrix<scalar_t><<<blocks, threads>>>(
				sols.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				mu_P.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				out_.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x, 3, 3
		); 
	})); 
	return out_; 
}

torch::Tensor _Pi_2(torch::Tensor v)
{
	const int x = v.size(0); 
	const int threads = 1024; 
	const dim3 blocks( (x + threads -1)/threads ); 
	torch::TensorOptions op = torch::TensorOptions().device(v.device()).dtype(v.dtype()); 
	torch::Tensor _out = torch::zeros({x, 1}, op); 

	AT_DISPATCH_FLOATING_TYPES(_out.scalar_type(), "_pi2", ([&]
	{
		_Pi2<scalar_t><<<blocks, threads>>>(
				_out.packed_accessor64<scalar_t, 2, torch::RestrictPtrTraits>(),
				x
		); 
	})); 

	return _out; 
}

torch::Tensor _Unit(torch::Tensor v, std::vector<int> diag)
{
	const int x = v.size(0); 
	const int threads = 1024; 
	const dim3 blocks( (x + threads -1)/threads, 3 ); 
	torch::TensorOptions op = torch::TensorOptions().device(v.device()).dtype(v.dtype()); 
	torch::Tensor _out = torch::zeros({x, 3, 3}, op); 
	torch::Tensor _diag = torch::tensor(diag, op);
	
	AT_DISPATCH_FLOATING_TYPES(_out.scalar_type(), "_Unit", ([&]
	{
		_Unit_<scalar_t><<<blocks, threads>>>(
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(),
				_diag.packed_accessor64<scalar_t, 1, torch::RestrictPtrTraits>(),
				x
		); 
	})); 

	return _out;
}

torch::Tensor _Factorization(torch::Tensor G)
{
	const int threads = 1024; 
	const int x = G.size(0); 
	const int t_th = (x + threads - 1)/threads; 
	const dim3 blocks13(t_th, 3); 
	const dim3 blocks22(t_th, 2, 2); 
	const dim3 blocks33(t_th, 3, 3);

	torch::Tensor _out = torch::zeros_like(G);
	torch::Tensor _tmp = _out.index({torch::indexing::Slice(), 1, 1}).clone(); 
	AT_DISPATCH_FLOATING_TYPES(_out.scalar_type(), "_Factorization", ([&]
	{
		_FacSol1<scalar_t><<<blocks22, threads>>>(
				G.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x
		); 

		_Swp1<scalar_t><<<blocks33, threads>>>(
				G.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x
		); 

		_Swp2<scalar_t><<<blocks13, threads>>>(
				G.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x
		); 
		_tmp = _out.index({torch::indexing::Slice(), 1, 1}).clone();	
		_DivG<scalar_t><<<blocks33, threads>>>(
				G.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_tmp.packed_accessor64<scalar_t, 1, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x
		); 


	})); 

	return _out; 
}

torch::Tensor _Factorization(torch::Tensor G, torch::Tensor Q, torch::Tensor Cofactors)
{
	const int threads = 1024; 
	const int x = G.size(0); 
	const int t_th = (x + threads - 1)/threads; 
	const dim3 blocks33(t_th, 3, 3);
	torch::Tensor _out = torch::zeros_like(G);

	AT_DISPATCH_FLOATING_TYPES(_out.scalar_type(), "_Factorization", ([&]
	{
		_FacSol2<scalar_t><<<blocks33, threads>>>(
				G.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				Q.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				Cofactors.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(),
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x
		); 
	})); 
	return _out; 
}

torch::Tensor _SwapXY(torch::Tensor G, torch::Tensor Q)
{
	const int threads = 1024; 
	const int x = G.size(0);
	const dim3 blocks((x + threads - 1)/threads, 3, 3); 
	
	torch::Tensor _out = torch::zeros_like(G); 
	AT_DISPATCH_FLOATING_TYPES(_out.scalar_type(), "_SwapXY", ([&]
	{
		_SwapXY_<scalar_t><<<blocks, threads>>>(
				G.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				Q.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				_out.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x
		); 
	})); 
	return _out; 
}

std::vector<torch::Tensor> _EllipseLines(torch::Tensor Lines, torch::Tensor Q, torch::Tensor A, double cutoff)
{
	const int threads = 1024; 
	const int x = Lines.size(0); 
	const int y = Lines.size(-2); 
	const int z = y; 
	
	torch::Tensor _out = torch::zeros_like(Q);
	torch::Tensor out = torch::zeros_like(Q); 
	torch::Tensor _diagL = torch::zeros_like(Q);
	torch::Tensor _diagA = torch::zeros_like(Q);
	const double _cutoff = cutoff;

	const dim3 blocks( (x + threads -1)/threads, y*y, z);
	const dim3 block2( (x + threads -1)/threads, y); 
	AT_DISPATCH_FLOATING_TYPES(_out.scalar_type(), "_EllipseLines", ([&]
	{
		_EllipseLines_<scalar_t><<<blocks, threads>>>(
				Lines.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				A.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				Q.packed_accessor64<scalar_t, 4, torch::RestrictPtrTraits>(),
				_out.packed_accessor64<scalar_t, 4, torch::RestrictPtrTraits>(), 
				_diagL.packed_accessor64<scalar_t, 4, torch::RestrictPtrTraits>(),
				_diagA.packed_accessor64<scalar_t, 4, torch::RestrictPtrTraits>(), 
				x, y, z
		);
		_diagL = _diagL.sum({-1}); 
		_diagA = _diagA.sum({-1}); 

		_EllipseLines_<scalar_t><<<block2, threads>>>(
				_diagL.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(),
				_diagA.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(), 
				x, y
		); 
	})); 
	std::tuple<torch::Tensor, torch::Tensor> idx = _diagA.sort(2, false);
	torch::Tensor id = std::get<1>(idx);
	id = id.to(out.dtype()); 
	_diagL = _diagA; 
	_diagA = std::get<0>(idx); 
	
	AT_DISPATCH_FLOATING_TYPES(_out.scalar_type(), "_gathering", ([&]
	{
		_gather_<scalar_t><<<blocks, threads>>>(
				_out.packed_accessor64<scalar_t, 4, torch::RestrictPtrTraits>(),
				id.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(),
				_diagL.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(),
				out.packed_accessor64<scalar_t, 4, torch::RestrictPtrTraits>(), 
				x, y, z, _cutoff 
		); 
	})); 

	torch::Tensor v = _out.index({
			torch::indexing::Slice(), 0,
			torch::indexing::Slice(), 
			torch::indexing::Slice()}).view({-1, 1, 3, 3});

	torch::Tensor v_ = _out.index({
			torch::indexing::Slice(), 1, 
			torch::indexing::Slice(), 
			torch::indexing::Slice()}).view({-1, 1, 3, 3});
	v = torch::cat({v, v_}, 1);

	_diagL = _diagL.index({
			torch::indexing::Slice(), 
			torch::indexing::Slice(torch::indexing::None, 2), 
			torch::indexing::Slice()}).view({-1, 2, 3});

	_diagA = _diagA.index({
			torch::indexing::Slice(), 
			torch::indexing::Slice(torch::indexing::None, 2), 
			torch::indexing::Slice()}).view({-1, 2, 3});
	return {_diagA, out, _diagL, v}; 
}
