import os
import torch
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension
from torch.utils.cpp_extension import CppExtension
try: from torch.utils.cpp_extension import CUDAExtension
except ModuleNotFoundError: pass


_dir = "src/"
TrH, TrC, TrS, TrCu = (
    _dir + "Transform/Headers/",
    _dir + "Transform/CXX/",
    _dir + "Transform/Shared/",
    _dir + "Transform/CUDA/",
)
OpH, OpC, OpS, OpCu = (
    _dir + "Operators/Headers/",
    _dir + "Operators/CXX/",
    _dir + "Operators/Shared/",
    _dir + "Operators/CUDA/",
)
PhH, PhC, PhS, PhCu = (
    _dir + "Physics/Headers/",
    _dir + "Physics/CXX/",
    _dir + "Physics/Shared/",
    _dir + "Physics/CUDA/",
)
NuH, NuC, NuS, NuCu = (
    _dir + "NuRecon/Headers/",
    _dir + "NuRecon/CXX/",
    _dir + "NuRecon/Shared/",
    _dir + "NuRecon/CUDA/",
)

PkgH = {
    "PyC.Transform.Floats": [TrH + "ToCartesianFloats.h", TrH + "ToPolarFloats.h"],
    "PyC.Transform.Tensors": [
        TrH + "ToCartesianTensors.h",
        TrH + "ToPolarTensors.h",
    ],
    "PyC.Transform.CUDA": [TrH + "ToCartesianCUDA.h", TrH + "ToPolarCUDA.h"],
    "PyC.Operators.Tensors": [OpH + "Tensors.h"],
    "PyC.Operators.CUDA": [OpH + "CUDA.h"],
    "PyC.Physics.Tensors.Cartesian": [
        TrH + "ToPolarTensors.h",
        PhH + "FromCartesianTensors.h",
        PhH + "Tensors.h",
    ],
    "PyC.Physics.CUDA.Cartesian": [
        TrH + "ToPolarCUDA.h",
        PhH + "CUDA.h",
        PhH + "FromCartesianCUDA.h",
    ],
    "PyC.Physics.Tensors.Polar": [
        TrH + "ToCartesianTensors.h",
        PhH + "FromPolarTensors.h",
        PhH + "Tensors.h",
    ],
    "PyC.Physics.CUDA.Polar": [
        TrH + "ToCartesianCUDA.h",
        PhH + "CUDA.h",
        PhH + "FromPolarCUDA.h",
    ],
    "PyC.NuSol.Tensors": [
        TrH + "ToCartesianTensors.h",
        TrH + "ToPolarTensors.h",
        PhH + "Tensors.h",
        OpH + "Tensors.h",
        NuH + "NuSolTensor.h",
    ],
    "PyC.NuSol.CUDA": [
        TrH + "ToCartesianCUDA.h",
        TrH + "ToPolarCUDA.h",
        PhH + "CUDA.h",
        OpH + "CUDA.h",
        NuH + "NuSolCUDA.h",
    ],
}

PkgC = {
    "PyC.Transform.Floats": [
        TrC + "ToCartesianFloats.cxx",
        TrC + "ToPolarFloats.cxx",
        TrS + "Floats.cxx",
    ],
    "PyC.Transform.Tensors": [
        TrC + "ToCartesianTensors.cxx",
        TrC + "ToPolarTensors.cxx",
        TrS + "Tensors.cxx",
    ],
    "PyC.Transform.CUDA": [
        TrCu + "Cartesian.cu",
        TrCu + "CartesianKernel.cu",
        TrCu + "CartesianTorch.cu",
        TrCu + "Polar.cu",
        TrCu + "PolarKernel.cu",
        TrCu + "PolarTorch.cu",
        TrS + "CUDA.cxx",
    ],
    "PyC.Operators.Tensors": [
        OpC + "Tensors.cxx",
        OpS + "Tensors.cxx",
    ],
    "PyC.Operators.CUDA": [
        OpCu + "Operators.cu",
        OpCu + "OperatorsKernel.cu",
        OpCu + "OperatorsTorch.cu",
        OpS + "CUDA.cxx",
    ],
    "PyC.Physics.Tensors.Cartesian": [
        TrC + "ToPolarTensors.cxx",
        PhC + "Tensors.cxx",
        PhS + "CartesianTensors.cxx",
    ],
    "PyC.Physics.CUDA.Cartesian": [
        TrCu + "Polar.cu",
        TrCu + "PolarKernel.cu",
        TrCu + "PolarTorch.cu",
        PhCu + "Physics.cu",
        PhCu + "PhysicsKernel.cu",
        PhCu + "PhysicsTorch.cu",
        PhS + "CartesianCUDA.cxx",
    ],
    "PyC.Physics.Tensors.Polar": [
        TrC + "ToCartesianTensors.cxx",
        PhC + "Tensors.cxx",
        PhS + "PolarTensors.cxx",
    ],
    "PyC.Physics.CUDA.Polar": [
        TrCu + "Cartesian.cu",
        TrCu + "CartesianKernel.cu",
        TrCu + "CartesianTorch.cu",
        PhCu + "Physics.cu",
        PhCu + "PhysicsKernel.cu",
        PhCu + "PhysicsTorch.cu",
        PhS + "PolarCUDA.cxx",
    ],
    "PyC.NuSol.Tensors": [
        TrC + "ToCartesianTensors.cxx",
        TrC + "ToPolarTensors.cxx",
        PhC + "Tensors.cxx",
        OpC + "Tensors.cxx",
        NuC + "NuSolTensor.cxx",
        NuC + "SingleNuTensor.cxx",
        NuC + "DoubleNuTensor.cxx",
        NuS + "Tensor.cxx",
    ],
    "PyC.NuSol.CUDA": [
        TrCu + "Cartesian.cu",
        TrCu + "CartesianKernel.cu",
        TrCu + "CartesianTorch.cu",
        TrCu + "Polar.cu",
        TrCu + "PolarKernel.cu",
        TrCu + "PolarTorch.cu",
        PhCu + "Physics.cu",
        PhCu + "PhysicsKernel.cu",
        PhCu + "PhysicsTorch.cu",
        OpCu + "Operators.cu",
        OpCu + "OperatorsKernel.cu",
        OpCu + "OperatorsTorch.cu",
        NuCu + "NuSol.cu",
        NuCu + "NuSolKernel.cu",
        NuCu + "NuSolTorch.cu",
        NuS + "CUDA.cxx",
    ],
}

_cmd = {
    "package_data": {},
    "ext_modules": [],
    "cmdclass": {"build_ext": BuildExtension},
}

cu = ""
if "CUDA_PATH" in os.environ:
    cu = os.environ["CUDA_PATH"]
else:
    import subprocess
    try:
        o = subprocess.check_output("which nvcc", stderr = subprocess.STDOUT, shell = True)
        cu = o.decode("UTF-8")
        os.environ["CUDA_PATH"] = cu
    except subprocess.CalledProcessError:
        pass
    if not torch.cuda.is_available():
        cu = ""

for i in PkgH:
    if len(cu) == 0 and "CUDA" in i:
        continue
    cmd = {"name": i, "sources": PkgC[i], "extra_compile_args": ["-std=c++14"]}
    if "CUDA" in i:
        cmd = CUDAExtension(**cmd)
    else:
        cmd = CppExtension(**cmd)

    _cmd["ext_modules"].append(cmd)
    _cmd["package_data"][i] = PkgH[i]


setup(**_cmd)
