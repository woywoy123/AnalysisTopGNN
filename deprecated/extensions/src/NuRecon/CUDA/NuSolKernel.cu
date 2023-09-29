#include "NuSol.cu"

template <typename scalar_t>
__global__ void _baseValsK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> muP2, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> bP2,
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> mue, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> be,
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> cos,
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> sin, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> mT2, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> mW2, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> mNu2,
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _out, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _bB, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _muB, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _muB2, 
		const int x, const int y)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y;

	if (indx >= x || indy >= y){return;}
	if (indy == 0){ _out[indx][indy] = cos[indx][0]; return; }
	if (indy == 1){ _out[indx][indy] = sin[indx][0]; return; }
	if (indy == 2){ _out[indx][indy] = _x0(mW2[indx][0], mNu2[indx][0], muP2[indx][0], mue[indx][0]); return; }
	if (indy == 3){ _out[indx][indy] = _x0(mT2[indx][0], mW2[indx][0], bP2[indx][0], be[indx][0]); return; }
	if (indy == 4){ _bB[indx][0] = sqrt(_beta2(bP2[indx][0], be[indx][0])); return; }
	if (indy == 5){ _muB[indx][0] = sqrt(_beta2(muP2[indx][0], mue[indx][0])); return; }
	if (indy == 6)
	{
		_out[indx][indy] = _w(muP2[indx][0], bP2[indx][0], mue[indx][0], be[indx][0], cos[indx][0], sin[indx][0], 1); 
		return; 
	}
	if (indy == 7)
	{
		_out[indx][indy] = _w(muP2[indx][0], bP2[indx][0], mue[indx][0], be[indx][0], cos[indx][0], sin[indx][0], -1); 
		return; 
	}
	if (indy == 8){ _muB2[indx][0] = _beta2(muP2[indx][0], mue[indx][0]); return; }
	if (indy == 9){ _out[indx][12] = (mW2[indx][0] - mNu2[indx][0]); return; }


}

template <typename scalar_t>
__global__ void _baseValsK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> muB2,
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> muB,
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> muP2, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _out, 
		const int x, const int y)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y;

	if (indx >= x || indy >= y){return;}
	if (indy == 0){ _out[indx][11] = _out[indx][6]*_out[indx][6] + 1 - muB2[indx][0]; return; } // O2
	if (indy == 1){ _out[indx][12] = _out[indx][12]*(1 - muB2[indx][0]); return; } // e2
	if (indy == 2){ _out[indx][4] = (_out[indx][2] * muB[indx][0] - sqrt(muP2[indx][0]) * ( 1 - muB2[indx][0] )) / muB2[indx][0]; return; } //Sx
}

template <typename scalar_t>
__global__ void _baseVals_K(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> bB, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> cos, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> sin, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _out, 
		const int x)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 

	if (indx >= x){return;}
	_out[indx][5] = ((_out[indx][3] / bB[indx][0]) - cos[indx][0] * _out[indx][4]) / sin[indx][0]; return; 
}


template <typename scalar_t>
__global__ void _baseValsK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> mW2,
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _out, 
		const int x, const int y)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y;

	if (indx >= x || indy >= y){return;}
	if (indy == 0)
	{
		_out[indx][8] = _out[indx][4] - (_out[indx][4] + _out[indx][6]*_out[indx][5])/_out[indx][11]; // x1
		return; 
	}

	if (indy == 1)
	{
		_out[indx][9] = _out[indx][5] - (_out[indx][4] + _out[indx][6]*_out[indx][5])*(_out[indx][6]/_out[indx][11]); // y1
		return; 
	}
	if (indy == 2)
	{
		// Z_tmp = - (Sy - w*Sx)^2 - (mW2 - x0^2 - e2)
		_out[indx][10] = -(_out[indx][5] - _out[indx][6]*_out[indx][4])*(_out[indx][5] - _out[indx][6]*_out[indx][4]) 
			         - (mW2[indx][0] - (_out[indx][2]*_out[indx][2]) - _out[indx][12]); return; 
	}

}

template <typename scalar_t>
__global__ void _baseValsK(
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _out, 
		const int x)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	if (indx >= x){return;}
	_out[indx][10] = _sqrt(_out[indx][8]*_out[indx][8]*_out[indx][11] + _out[indx][10]); 
}

template <typename scalar_t>
__global__ void _HMatrix(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> sols_,
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> muP_,
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> out, 
		const int x, const int y, const int z)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y;
	const int indz = blockIdx.z;
	
	if (indx >= x || indy >= y || indz >= z){return;}
	if (indy == 0 && indz == 1){ return; }
	if (indy == 1 && indz == 1){ return; }
	if (indy == 2 && indz == 0){ return; }
	if (indy == 2 && indz == 2){ return; }

	if (indy == 0 && indz == 0){ out[indx][indy][indz] = sols_[indx][10]/_sqrt(sols_[indx][11]); return; }
	if (indy == 0 && indz == 2){ out[indx][indy][indz] = sols_[indx][8] - muP_[indx][0]; return; }
	if (indy == 1 && indz == 0){ out[indx][indy][indz] = (sols_[indx][10]/_sqrt(sols_[indx][11]))*sols_[indx][6]; return; }
	if (indy == 1 && indz == 2){ out[indx][indy][indz] = sols_[indx][9]; return; }
	if (indy == 2 && indz == 1){ out[indx][indy][indz] = sols_[indx][10]; return; }
}

template <typename scalar_t>
__global__ void _Pi2(
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> out_, 
		const int x)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	if (indx >= x){ return; }
	out_[indx][0] = acos(out_[indx][0]);
}

template <typename scalar_t>
__global__ void _Unit_(
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> out_, 
		torch::PackedTensorAccessor64<scalar_t, 1, torch::RestrictPtrTraits> diag_, 
		const int x)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y; 
	if (indx >= x){ return; }
	out_[indx][indy][indy] = diag_[indy]; 
}

template <typename scalar_t>
__global__ void _FacSol1(
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> G, 
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _out, 
		const int x)
{

	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y; 
	const int indz = blockIdx.z;

	if (indx >= x){ return; }
	if ( G[indx][0][0] != 0 && G[indx][1][1] != 0 ){ return; }

	if (indy == indz){ _out[indx][indy][indz] = G[indx][0][1]; return; }
	if (indy == 0){ _out[indx][0][2] = G[indx][1][2]; return; }	
	if (indy == 1){ _out[indx][1][2] = G[indx][0][2] - G[indx][1][2]; return; }
}

template <typename scalar_t>
__global__ void _Swp1(
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> G, 
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _out, 
		const int x)
{

	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y; 
	const int indz = blockIdx.z;

	if (indx >= x){ return; }
	if ( G[indx][0][0] == 0 && G[indx][1][1] == 0 ){ return; }
	if ( abs(G[indx][0][0]) < abs(G[indx][1][1]))
	{
		_out[indx][indy][indz] = G[indx][indy][indz]; 
		return; 
	}
	if (indy == 2)
	{
		_out[indx][indy][indz] = G[indx][indy][indz]; 
		return; 
	}
	_out[indx][indy][indz] = G[indx][1-indy][indz]; 	
}

template <typename scalar_t>
__global__ void _Swp2(
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> G, 
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _out, 
		const int x)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y;

	if (indx >= x){ return; }
	if ( G[indx][0][0] == 0 && G[indx][1][1] == 0 ){ return; }

	if ( abs(G[indx][0][0]) < abs(G[indx][1][1]) ){ return; }
	const scalar_t tmp = _out[indx][indy][0]; 
	_out[indx][indy][0] = _out[indx][indy][1]; 
	_out[indx][indy][1] = tmp; 
}

template <typename scalar_t>
__global__ void _DivG(
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> G, 
		const torch::PackedTensorAccessor64<scalar_t, 1, torch::RestrictPtrTraits> _tmp, 
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _out, 
		const int x)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y;
	const int indz = blockIdx.z;

	if (indx >= x){ return; }
	if ( G[indx][0][0] == 0 && G[indx][1][1] == 0 ){ return; }
	_out[indx][indy][indz] = _out[indx][indy][indz] / _tmp[indx]; 
}

template <typename scalar_t>
__global__ void _FacSol2(
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> G, 
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> Q, 
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> Cofact, 
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _out, 
		const int x)
{
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y;
	const int indz = blockIdx.z;

	if (indx >= x){ return; }
	if ( G[indx][0][0] == 0 && G[indx][1][1] == 0 ){ return; }

	const scalar_t g22 = Cofact[indx][2][2]; 
	_out[indx][indy][indz] = 0; 
	
	if (-g22 <= 0.)
	{
		const scalar_t g00 = -Cofact[indx][0][0]; 
		
		// Negative solution
		if (indy == 0 && indz == 0 && g00 >= 0){ _out[indx][0][indz] = Q[indx][0][1]; return; }
		if (indy == 0 && indz == 1 && g00 >= 0){ _out[indx][0][indz] = Q[indx][1][1]; return; }
		if (indy == 0 && indz == 2 && g00 >= 0){ _out[indx][0][indz] = Q[indx][1][2] - sqrt(g00); return; }
			
		// Positive solution 
		if (indy == 1 && indz == 0 && g00 > 0){ _out[indx][1][indz] = Q[indx][0][1]; return; }
		if (indy == 1 && indz == 1 && g00 > 0){ _out[indx][1][indz] = Q[indx][1][1]; return; }
		if (indy == 1 && indz == 2 && g00 > 0){ _out[indx][1][indz] = Q[indx][1][2] + sqrt(g00); return; }
	}


	if (-g22 > 0.)
	{
		const scalar_t x0 = Cofact[indx][0][2] / g22; 
		const scalar_t y0 = Cofact[indx][1][2] / g22;

		if (indy == 0 && indz == 0)
		{ 
			_out[indx][0][0] = Q[indx][0][1] - sqrt( -g22 ); 
			return; 
		}	

		if (indy == 1 && indz == 0)
		{ 
			_out[indx][1][0] = Q[indx][0][1] + sqrt( -g22 ); 
			return; 
		}	

		if ((indy == 0 || indy == 1) && indz == 1)
		{ 
			_out[indx][indy][1] = Q[indx][1][1]; 
			return; 
		}	
		
		if (indy == 0 && indz == 2)
		{ 
			_out[indx][0][2] = -Q[indx][1][1] * y0 - (Q[indx][0][1] - sqrt( -g22 )) * x0;
			return;   
		}

		if (indy == 1 && indz == 2)
		{ 
			_out[indx][1][2] = -Q[indx][1][1] * y0 - (Q[indx][0][1] + sqrt( -g22 )) * x0;
			return;   
		}
	}
}


template <typename scalar_t>
__global__ void _SwapXY_(
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> G, 
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> Q, 
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _out, 
		const int x)
{

	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y;
	const int indz = blockIdx.z;
	
	if (indx >= x){return;}
	
	if (abs(G[indx][0][0]) > abs(G[indx][1][1]) && indz < 2)
	{
		_out[indx][indy][1-indz] = Q[indx][indy][indz];
		return; 
	}
	_out[indx][indy][indz] = Q[indx][indy][indz];
}

template <typename scalar_t>
__global__ void _EllipseLines_(
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> Lines,
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> A,
		const torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> Q, 
		torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> _out, 
		torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> _diagL, 
		torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> _diagA, 
		const int x, const int y, const int z)
{

	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y;
	const int indz = blockIdx.z;
	const int _iy = indy/y; 
	const int _y = indy%y;

	if (indx >= x){return;}

	_diagL[indx][_iy][_y][indz] = Q[indx][_iy][_y][indz] * Lines[indx][_iy][indz]; 
	for (int i(0); i < y; ++i)	
	{
		_diagA[indx][_iy][_y][indz] += Q[indx][_iy][_y][i] * A[indx][indz][i];
	}
	_diagA[indx][_iy][_y][indz] = Q[indx][_iy][_y][indz] * _diagA[indx][_iy][_y][indz];

	if (Q[indx][_iy][_y][2] == 0){ _out[indx][_iy][_y][indz] = 0; return; }
	_out[indx][_iy][_y][indz] = Q[indx][_iy][_y][indz]/Q[indx][_iy][_y][2]; 
}

template <typename scalar_t>
__global__ void _EllipseLines_(
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _diagL, 
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _diagA, 
		const int x, const int y)
{

	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y;
	if (indx >= x){return;}
	
	for (int i(0); i < y; ++i)
	{
		_diagA[indx][indy][i] = pow(_diagL[indx][indy][i], 2) + pow(_diagA[indx][indy][i], 2); 
	}

}

template <typename scalar_t>
__global__ void _gather_(
		const torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> _out, 
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _id, 
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _diag, 
		torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> out,
		const int x, const int y, const int z, const double cutoff)
{

	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y;
	const int indz = blockIdx.z;
	const int _iy = indy/y; 
	const int _y = indy%y; 

	if (indx >= x){return;}
	if (_diag[indx][_iy][ _y ] >= cutoff){return;}
	out[indx][_iy][ _id[indx][_iy][_y]  ][indz] = _out[indx][_iy][ _y ][indz]; 
}
