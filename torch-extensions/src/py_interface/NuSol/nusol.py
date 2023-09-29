import inspect
import torch
import os

CUDA_SO   = "/".join(__file__.split("/")[:-3]) + "/libpyc_cuda.so"
FLOAT_SO  = "/".join(__file__.split("/")[:-3]) + "/libpyc_float.so"
TENSOR_SO = "/".join(__file__.split("/")[:-3]) + "/libpyc_tensor.so"
torch.ops.load_library(CUDA_SO)   if os.path.isfile(CUDA_SO) else None
torch.ops.load_library(TENSOR_SO) if os.path.isfile(TENSOR_SO) else None
torch.ops.load_library(FLOAT_SO)  if os.path.isfile(FLOAT_SO) else None

cmb_ = __file__.split("/")[-1].rstrip(".py")
mod_ = __file__.split("/")
mod_ = mod_[mod_.index("pyc")+1].lower()

__name_c__ = mod_ + "_"
__name_s__ = mod_ + "_"

def __router__(
        inpt, get, trig_cmb,
        cmb = __name_c__,
        sgl = __name_s__
    ):

    inpt = [i for i in inpt if i is not None]
    comb = cmb if len(inpt) == trig_cmb else sgl
    comb += get
    fx = {}
    if len([i for i in inpt if torch.is_tensor(i)]) == 0: 
        fx = torch.ops.pyc_float
    elif len([i for i in inpt if i.is_cuda]) == len(inpt):
        fx = torch.ops.pyc_cuda
    else:
        inpt = [i.to(device = "cpu") for i in inpt]
        fx = torch.ops.pyc_tensor

    try: return fx.__dict__[comb], inpt
    except KeyError: pass
    return getattr(fx, comb), inpt

def BaseMatrix(ten1, ten2, ten3):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2, ten3], name, 1)
    return fn(*inpt)

def Intersection(ten1, ten2, null = 10e-10):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2], name, 2)
    inpt += [null]
    return fn(*inpt)

def Nu(ten1, ten2, ten3, ten4, ten5, null = 10e-10):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2, ten3, ten4, ten5], name, 5)
    inpt += [null]
    if null == -1: return fn(*inpt)[0]
    return fn(*inpt)

def NuNu(b1, b2, l1, l2, metxy, mass, null = 10e-10):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([b1, b2, l1, l2, metxy, mass], name, 5)
    inpt += [null]
    return fn(*inpt)
