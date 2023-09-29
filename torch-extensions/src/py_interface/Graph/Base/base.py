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

__name_c__ = mod_ + "_" + cmb_ + "_combined_"
__name_s__ = mod_ + "_" + cmb_ + "_separate_"

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

def edge_aggregation(ten1, ten2, ten3, include_zero = False):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2, ten3], name, 3)
    inpt += [include_zero]
    res = fn(*inpt)
    keys = [
            (0, "clusters"),
            (1, "unique_sum"),
            (2, "reverse_clusters"),
            (3, "node_sum")
    ]

    out = {}
    for i in range(len(res)):
        out[i] = { n : res[i][k] for k, n in keys }
    return out

def node_aggregation(ten1, ten2, ten3, include_zero = False):
    name = inspect.currentframe().f_code.co_name
    fn, inpt = __router__([ten1, ten2, ten3], name, 3)
    inpt += [include_zero]
    res = fn(*inpt)
    keys = [
            (0, "clusters"),
            (1, "unique_sum"),
            (2, "reverse_clusters"),
            (3, "node_sum")
    ]

    out = {}
    for i in range(len(res)):
        out[i] = { n : res[i][k] for k, n in keys }
    return out


