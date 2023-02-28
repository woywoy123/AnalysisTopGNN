from setuptools import setup 
from torch.utils.cpp_extension import BuildExtension, CppExtension, CUDAExtension
import torch
import os 
os.environ["CC"] = "gcc-11"
os.environ["CXX"] = "gcc-11"

Transform_H  = "src/Transform/Headers/"
Transform_C  = "src/Transform/CXX/"
Transform_S  = "src/Transform/Shared/"
Transform_Cu = "src/Transform/CUDA/"

Operators_H  = "src/Operators/Headers/"
Operators_C  = "src/Operators/CXX/"
Operators_S  = "src/Operators/Shared/"
Operators_Cu = "src/Operators/CUDA/"

Physics_H  = "src/Physics/Headers/"
Physics_C  = "src/Physics/CXX/"
Physics_S  = "src/Physics/Shared/"
Physics_Cu = "src/Physics/CUDA/"

NuRecon_H  = "src/NuRecon/Headers/"
NuRecon_C  = "src/NuRecon/CXX/"
NuRecon_S  = "src/NuRecon/Shared/"
NuRecon_Cu = "src/NuRecon/CUDA/"

PkgH = {
            "PyC.Transform.Floats" : [
                Transform_H + "ToCartesianFloats.h", 
                Transform_H + "ToPolarFloats.h"
            ], 
            
            "PyC.Transform.Tensors" : [
                Transform_H + "ToCartesianTensors.h", 
                Transform_H + "ToPolarTensors.h", 
            ],

            "PyC.Transform.CUDA" : [
                Transform_H + "ToCartesianCUDA.h", 
                Transform_H + "ToPolarCUDA.h"
            ], 

            "PyC.Operators.Tensors" : [
                Operators_H + "Tensors.h" 
            ],
            "PyC.Operators.CUDA" : [
                Operators_H + "CUDA.h"
            ], 

            "PyC.Physics.Tensors.Cartesian" : [
                Transform_H + "ToPolarTensors.h", 
                Physics_H + "FromCartesianTensors.h",
                Physics_H + "Tensors.h"
            ],
            
            "PyC.Physics.CUDA.Cartesian" : [ 
                Transform_H + "ToPolarCUDA.h",
                Physics_H + "CUDA.h", 
                Physics_H + "FromCartesianCUDA.h", 
            ], 

            "PyC.Physics.Tensors.Polar" : [
                Transform_H + "ToCartesianTensors.h", 
                Physics_H + "FromPolarTensors.h",
                Physics_H + "Tensors.h"
            ],
            "PyC.Physics.CUDA.Polar" : [ 
                Transform_H + "ToCartesianCUDA.h",
                Physics_H + "CUDA.h", 
                Physics_H + "FromPolarCUDA.h", 
            ], 
            "PyC.NuSol.Tensors" : [
                Transform_H + "ToCartesianTensors.h", 
                Physics_H + "Tensors.h",
                Operators_H + "Tensors.h",

                NuRecon_H + "NuSolTensor.h",
            ], 

            "PyC.NuSol.Tensors" : [
                Transform_H + "ToCartesianTensors.h", 
                Transform_H + "ToPolarTensors.h",

                Physics_H + "Tensors.h",
                Operators_H + "Tensors.h",

                NuRecon_H + "NuSolTensor.h",
            ], 
            "PyC.NuSol.CUDA" : [
                Transform_H + "ToCartesianCUDA.h",
                Transform_H + "ToPolarCUDA.h", 
                Physics_H + "CUDA.h", 
                Operators_H + "CUDA.h", 

                NuRecon_H + "NuSolCUDA.h",
            ], 
}

PkgC = {
        "PyC.Transform.Floats" : [
                Transform_C + "ToCartesianFloats.cxx", 
                Transform_C + "ToPolarFloats.cxx", 
                Transform_S + "Floats.cxx"
        ],

        "PyC.Transform.Tensors" : [
                Transform_C + "ToCartesianTensors.cxx", 
                Transform_C + "ToPolarTensors.cxx", 
                Transform_S + "Tensors.cxx"
        ],

        "PyC.Transform.CUDA" : [
                Transform_Cu + "Cartesian.cu",
                Transform_Cu + "CartesianKernel.cu", 
                Transform_Cu + "CartesianTorch.cu", 
                Transform_Cu + "Polar.cu",
                Transform_Cu + "PolarKernel.cu", 
                Transform_Cu + "PolarTorch.cu", 
                Transform_S  + "CUDA.cxx", 
        ],

        "PyC.Operators.Tensors" : [
                Operators_C + "Tensors.cxx", 
                Operators_S + "Tensors.cxx", 
        ], 

        "PyC.Operators.CUDA" : [
                Operators_Cu + "Operators.cu", 
                Operators_Cu + "OperatorsKernel.cu", 
                Operators_Cu + "OperatorsTorch.cu", 
                Operators_S  + "CUDA.cxx"
        ],

        "PyC.Physics.Tensors.Cartesian" : [
                Transform_C + "ToPolarTensors.cxx",
                Physics_C + "Tensors.cxx",
                Physics_S + "CartesianTensors.cxx"
        ], 

        "PyC.Physics.CUDA.Cartesian" : [
                Transform_Cu + "Polar.cu",
                Transform_Cu + "PolarKernel.cu", 
                Transform_Cu + "PolarTorch.cu", 

                Physics_Cu + "Physics.cu", 
                Physics_Cu + "PhysicsKernel.cu",
                Physics_Cu + "PhysicsTorch.cu", 

                Physics_S + "CartesianCUDA.cxx",
        ], 

        "PyC.Physics.Tensors.Polar" : [
                Transform_C + "ToCartesianTensors.cxx",
                Physics_C + "Tensors.cxx",
                Physics_S + "PolarTensors.cxx"
        ], 

        "PyC.Physics.CUDA.Polar" : [
                Transform_Cu + "Cartesian.cu",
                Transform_Cu + "CartesianKernel.cu", 
                Transform_Cu + "CartesianTorch.cu", 

                Physics_Cu + "Physics.cu", 
                Physics_Cu + "PhysicsKernel.cu",
                Physics_Cu + "PhysicsTorch.cu", 

                Physics_S + "PolarCUDA.cxx",
        ], 

        "PyC.NuSol.Tensors" : [
                Transform_C + "ToCartesianTensors.cxx",
                Transform_C + "ToPolarTensors.cxx", 

                Physics_C + "Tensors.cxx",
                Operators_C + "Tensors.cxx",

                NuRecon_C + "NuSolTensor.cxx",
                NuRecon_C + "SingleNuTensor.cxx",
                NuRecon_C + "DoubleNuTensor.cxx",
                NuRecon_S + "Tensor.cxx"
        ], 

        "PyC.NuSol.CUDA" : [
                Transform_Cu + "Cartesian.cu",
                Transform_Cu + "CartesianKernel.cu", 
                Transform_Cu + "CartesianTorch.cu", 

                Transform_Cu + "Polar.cu",
                Transform_Cu + "PolarKernel.cu", 
                Transform_Cu + "PolarTorch.cu", 

                Physics_Cu + "Physics.cu", 
                Physics_Cu + "PhysicsKernel.cu",
                Physics_Cu + "PhysicsTorch.cu", 

                Operators_Cu + "Operators.cu", 
                Operators_Cu + "OperatorsKernel.cu", 
                Operators_Cu + "OperatorsTorch.cu", 

                NuRecon_Cu + "NuSol.cu", 
                NuRecon_Cu + "NuSolKernel.cu", 
                NuRecon_Cu + "NuSolTorch.cu", 

                NuRecon_S + "CUDA.cxx"
        ], 
}

Pkg = [
        "PyC.Transform.Floats", "PyC.Transform.Tensors", "PyC.Transform.CUDA", 
        "PyC.Operators.Tensors", "PyC.Operators.CUDA", 
        "PyC.Physics.Tensors.Cartesian", "PyC.Physics.CUDA.Cartesian", 
        "PyC.Physics.Tensors.Polar", "PyC.Physics.CUDA.Polar", 
        "PyC.NuSol.Tensors", "PyC.NuSol.CUDA"
        ]
if torch.cuda.is_available() == False:
    Pkg = [i for i in Pkg if i.endswith("CUDA") == False]
setup(
        name = "AnalysisTopGNN-Extensions", 
        version = "1.0", 
        package_data = { i : PkgH[i] for i in Pkg }, 
        ext_modules = [ CUDAExtension(i, PkgC[i]) if i.endswith("CUDA") else CppExtension(i, PkgC[i]) for i in Pkg ], 
        cmdclass = {"build_ext" : BuildExtension}, 
)


