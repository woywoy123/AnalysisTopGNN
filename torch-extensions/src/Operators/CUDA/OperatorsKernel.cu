#include "Operators.cu"

template <typename scalar_t> 
__global__ void _Dot2K(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> v1, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> v2, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _out, 
		const int len, const int dim)
{
	
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y; 
	
	if (indx >= len || indy >= dim){return;}
	_v1xv2(&_out[indx][indy], &v1[indx][indy], &v2[indx][indy]); 
}


template <typename scalar_t>
__global__ void _Dot3K(
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> v1, 
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> v2, 
		torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> _out, 
		const int x, const int _t, const int y, const int z)
{
	
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y;
	const int zi_1 = (indy/(_t*y))%z; 
	const int yi_2 = (indy/_t)%y; 
	const int t_ = indy%_t; 

	if (indx >= x || indy >= _t*y*z){return;}
	_out[indx][t_][yi_2][zi_1] = v1[indx][yi_2][t_] * v2[indx][t_][zi_1];  
}

template <typename scalar_t>
__global__ void _Sum3K(
		const torch::PackedTensorAccessor64<scalar_t, 4, torch::RestrictPtrTraits> v1, 
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _out, 
		const int x, const int _t, const int y, const int z)
{
	
	const int indx = blockIdx.x*blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y;
	const int indz = blockIdx.z;
	if (indx >= x || indy >= y || indz >= z){return;}
	_out[indx][indy][indz] = 0; 
	for (int i(0); i < _t; ++i){_recsum(&_out[indx][indy][indz], v1[indx][i][indy][indz]);}
}

template <typename scalar_t> 
__global__ void _CosThetaK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v12, 
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _v22, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _V1V2, 
		const int x)
{	
	const int indx = blockIdx.x * blockDim.x + threadIdx.x; 
	if (indx >= x){return;}
	_costheta(&_V1V2[indx][0], &_v12[indx][0], &_v22[indx][0], &_V1V2[indx][0]); 
}

template <typename scalar_t>
__global__ void _RxK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> agl, 
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _out)
{
	const int indx = blockIdx.x * blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y; 
	const int indz = blockIdx.z; 

	if (indx >= agl.size(0) || indy >= 3 || indz >= 3){ return; }
	
	if (indy == indz && indz == 0){ _out[indx][indy][indz] = 1; return; }	
	if (indy == indz && indz > 0){ _out[indx][indy][indz] = _cos(agl[indx][0]); return; }
	if (indy == 1 && indz == 2){ _out[indx][indy][indz] = -_sin(agl[indx][0]); return; }
	if (indy == 2 && indz == 1){ _out[indx][indy][indz] = _sin(agl[indx][0]); return; }
}

template <typename scalar_t>
__global__ void _RyK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> agl, 
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _out)
{
	const int indx = blockIdx.x * blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y; 
	const int indz = blockIdx.z; 

	if (indx >= agl.size(0) || indy >= 3 || indz >= 3){ return; }

	if (indy == indz && ( indz == 0 || indz == 2) ){ _out[indx][indy][indz] = _cos(agl[indx][0]); return; }	
	if (indy == 0 && indz == 2){ _out[indx][indy][indz] = _sin(agl[indx][0]); return; }	
	if (indy == 2 && indz == 0){ _out[indx][indy][indz] = -_sin(agl[indx][0]); return; }	
	if (indy == indz && indz == 1){ _out[indx][indy][indz] = 1; return; }	
}

template <typename scalar_t>
__global__ void _RzK(
		const torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> agl, 
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _out)
{
	const int indx = blockIdx.x * blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y; 
	const int indz = blockIdx.z; 

	if (indx >= agl.size(0) || indy >= 3 || indz >= 3){ return; }

	if (indy == indz && indz < 2){ _out[indx][indy][indz] = _cos(agl[indx][0]); return; }	
	if (indy == 1 && indz == 0){ _out[indx][indy][indz] = _sin(agl[indx][0]); return; }
	if (indy == 0 && indz == 1){ _out[indx][indy][indz] = -_sin(agl[indx][0]); return; }
	if (indy == indz && indz == 2){ _out[indx][indy][indz] = 1; return; }	
}

template <typename scalar_t>
__global__ void _CoFactors(
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> inpt, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _tmp, 
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _out, 
		const int x, const int y, const int z)
{
	const int indx = blockIdx.x * blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y; 
	const int indz = blockIdx.z;
	const int ith = indx*y*z + indy*z + indz;

	if (indx >= x){return;}
	
	int _i = 0; 
	for (int i(0); i < y*z; ++i)
	{
		int _c = i%y;
		int _r = (i/y)%z;
		if (_c == indz || _r == indy){ continue; }
		_tmp[ith][_i] = inpt[indx][_r][_c]; 
		_i++; 
	}
	_out[indx][indy][indz] = pow(-1, indy+indz)*(_tmp[ith][0]*_tmp[ith][3] - _tmp[ith][1]*_tmp[ith][2]); 
}

template <typename scalar_t>
__global__ void _Det(
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> Matrix, 
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> Coef, 
		torch::PackedTensorAccessor64<scalar_t, 2, torch::RestrictPtrTraits> _out, 
		const int x, const int y)
{

	const int indx = blockIdx.x * blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y; 
	if (indx >= x || indy >= y){ return; }
	_out[indx][indy] = Coef[indx][0][indy]*Matrix[indx][0][indy]; 
}


template <typename scalar_t>
__global__ void _Inv(
		const torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> Coef, 
		const torch::PackedTensorAccessor64<scalar_t, 1, torch::RestrictPtrTraits> Det, 
		torch::PackedTensorAccessor64<scalar_t, 3, torch::RestrictPtrTraits> _out, 
		const int x, const int y, const int z)
{

	const int indx = blockIdx.x * blockDim.x + threadIdx.x; 
	const int indy = blockIdx.y; 
	const int indz = blockIdx.z;
	if (indx >= x || indy >= y || indz >= z){ return; }
	
	if (Det[indx] != 0){ _out[indx][indy][indz] = Coef[indx][indz][indy]/Det[indx]; }
}
