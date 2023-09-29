import inspect
import torch
import os

CUDA_SO   = "/".join(__file__.split("/")[:-2]) + "/libpyc_cuda.so"
FLOAT_SO  = "/".join(__file__.split("/")[:-2]) + "/libpyc_float.so"
TENSOR_SO = "/".join(__file__.split("/")[:-2]) + "/libpyc_tensor.so"
torch.ops.load_library(CUDA_SO)   if os.path.isfile(CUDA_SO) else None
torch.ops.load_library(TENSOR_SO) if os.path.isfile(TENSOR_SO) else None
torch.ops.load_library(FLOAT_SO)  if os.path.isfile(FLOAT_SO) else None

mod_ = __file__.split("/")
mod_ = mod_[mod_.index("pyc")+1].lower()
__name_c__ = mod_ + "_"

def __router__(
        inpt, get, trig_cmb,
        cmb = __name_c__,
        sgl = __name_c__
    ):

    inpt = [i for i in inpt if i is not None]
    comb = cmb if len(inpt) == trig_cmb else sgl
    comb += get
    fx = {}
    if len([i for i in inpt if torch.is_tensor(i)]) == 0: 
        fx = torch.ops.pyc_float
    elif len([i for i in inpt if i.is_cuda]) == 0:
        fx = torch.ops.pyc_tensor
    else:
        fx = torch.ops.pyc_cuda

    try: return fx.__dict__[comb], inpt
    except KeyError: pass
    return getattr(fx, comb), inpt

def Dot(ten1, ten2):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2], name, 1)
    return fn(*inpt)

def Mul(ten1, ten2):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2], name, 1)
    return fn(*inpt)

def CosTheta(ten1, ten2):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2], name, 1)
    return fn(*inpt)

def SinTheta(ten1, ten2):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2], name, 1)
    return fn(*inpt)

def Rx(ten1):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1], name, 1)
    return fn(*inpt)

def Ry(ten1):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1], name, 1)
    return fn(*inpt)

def Rz(ten1):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1], name, 1)
    return fn(*inpt)

def CoFactors(ten1):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1], name, 1)
    return fn(*inpt)

def Determinant(ten1):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1], name, 1)
    return fn(*inpt)

def Inverse(ten1):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1], name, 1)
    return fn(*inpt)

def Cross(ten1, ten2):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2], name, 2)
    return fn(*inpt)


