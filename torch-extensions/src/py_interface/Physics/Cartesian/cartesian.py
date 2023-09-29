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

__name_c__ = mod_ + "_combined_" + cmb_ + "_"
__name_s__ = mod_ + "_separate_" + cmb_ + "_"

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
    elif len([i for i in inpt if i.is_cuda]) == 0:
        fx = torch.ops.pyc_tensor
    else:
        fx = torch.ops.pyc_cuda

    try: return fx.__dict__[comb], inpt
    except KeyError: pass
    return getattr(fx, comb), inpt

def P(ten1, ten2 = None, ten3 = None):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2, ten3], name, 1)
    return fn(*inpt)

def P2(ten1, ten2 = None, ten3 = None):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2, ten3], name, 1)
    return fn(*inpt)

def Beta(ten1, ten2 = None, ten3 = None, ten4 = None):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2, ten3, ten4], name, 1)
    return fn(*inpt)

def Beta2(ten1, ten2 = None, ten3 = None, ten4 = None):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2, ten3, ten4], name, 1)
    return fn(*inpt)

def M2(ten1, ten2 = None, ten3 = None, ten4 = None):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2, ten3, ten4], name, 1)
    return fn(*inpt)

def M(ten1, ten2 = None, ten3 = None, ten4 = None):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2, ten3, ten4], name, 1)
    return fn(*inpt)

def Mt2(ten1, ten2 = None):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2], name, 1)
    return fn(*inpt)

def Mt(ten1, ten2 = None):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2], name, 1)
    return fn(*inpt)

def Theta(ten1, ten2 = None, ten3 = None):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2, ten3], name, 1)
    return fn(*inpt)

def DeltaR(ten1, ten2, ten3 = None, ten4 = None, ten5 = None, ten6 = None):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2, ten3, ten4, ten5, ten6], name, 2)
    return fn(*inpt)


