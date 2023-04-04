from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CppExtension

setup(
        name = "NuReconstruction",
        package_data = {
            "NuR.Physics.Floats" : [
                "NuReconstruction/Physics/Tensors/Headers/PhysicsTensors.h", 
                "NuReconstruction/Physics/Floats/Headers/PhysicsFloats.h"
            ],
            "NuR.Physics.Tensors" : [
                "NuReconstruction/Physics/Tensors/Headers/PhysicsTensors.h"
            ], 
            "NuR.Sols.Floats" : [
                "NuReconstruction/Physics/Floats/Headers/PhysicsFloats.h", 
                "NuReconstruction/Physics/Tensors/Headers/PhysicsTensors.h",
                "NuReconstruction/NuSolutions/Headers/NuSolFloats.h"
                "NuReconstruction/NuSolutions/Headers/NuSolTensors.h"
            ], 
            "NuR.Sols.Tensors" : [
                "NuReconstruction/Physics/Tensors/Headers/PhysicsTensors.h", 
                "NuReconstruction/NuSolutions/Headers/NuSolTensors.h"
            ], 
            "NuR.SingleNu.Floats" : [
                "NuReconstruction/Physics/Tensors/Headers/PhysicsTensors.h", 
                "NuReconstruction/Physics/Floats/Headers/PhysicsFloats.h",

                "NuReconstruction/NuSolutions/Headers/NuSolTensors.h", 
                "NuReconstruction/SingleNeutrino/Headers/Floats.h"
            ],
            "NuR.DoubleNu.Floats" : [
                "NuReconstruction/Physics/Tensors/Headers/PhysicsTensors.h", 
                "NuReconstruction/Physics/Floats/Headers/PhysicsFloats.h",

                "NuReconstruction/NuSolutions/Headers/NuSolTensors.h", 
                "NuReconstruction/DoubleNeutrino/Headers/Floats.h"
            ], 
        }, 
        ext_modules = [
            CppExtension("NuR.Physics.Tensors", 
                            [
                                "NuReconstruction/Physics/Tensors/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Tensors/CXX/Polar.cxx", 
                                
                                "NuReconstruction/Physics/Tensors/Shared/PhysicsTensors.cxx"
                            ]
            ), 
            CppExtension("NuR.Physics.Floats", 
                            [
                                "NuReconstruction/Physics/Floats/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Floats/CXX/Polar.cxx", 

                                "NuReconstruction/Physics/Tensors/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Tensors/CXX/Polar.cxx", 

                                "NuReconstruction/Physics/Floats/Shared/PhysicsFloats.cxx", 
                            ]
            ),
            CppExtension("NuR.Sols.Tensors", 
                            [
                                "NuReconstruction/Physics/Tensors/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Tensors/CXX/Polar.cxx", 

                                "NuReconstruction/NuSolutions/CXX/NuSolTensors.cxx", 
                                
                                "NuReconstruction/NuSolutions/Shared/NuSolTensors.cxx"
                            ]
            ),
            CppExtension("NuR.Sols.Floats", 
                            [
                                "NuReconstruction/Physics/Floats/CXX/Cartesian.cxx",
                                "NuReconstruction/Physics/Floats/CXX/Polar.cxx",
                                "NuReconstruction/Physics/Tensors/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Tensors/CXX/Polar.cxx", 

                                "NuReconstruction/NuSolutions/CXX/NuSolFloats.cxx", 
                                "NuReconstruction/NuSolutions/CXX/NuSolTensors.cxx", 

                                "NuReconstruction/NuSolutions/Shared/NuSolFloats.cxx"
                            ]
            ), 
            
            CppExtension("NuR.SingleNu.Floats", 
                            [
                                "NuReconstruction/Physics/Floats/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Floats/CXX/Polar.cxx", 
                                
                                "NuReconstruction/Physics/Tensors/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Tensors/CXX/Polar.cxx", 

                                "NuReconstruction/NuSolutions/CXX/NuSolTensors.cxx", 

                                "NuReconstruction/SingleNeutrino/CXX/Tensors.cxx", 
                                
                                "NuReconstruction/SingleNeutrino/Shared/Floats.cxx", 
                            ]
            ), 

            CppExtension("NuR.DoubleNu.Floats", 
                            [
                                "NuReconstruction/Physics/Floats/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Floats/CXX/Polar.cxx", 
                                
                                "NuReconstruction/Physics/Tensors/CXX/Cartesian.cxx", 
                                "NuReconstruction/Physics/Tensors/CXX/Polar.cxx", 

                                "NuReconstruction/NuSolutions/CXX/NuSolTensors.cxx", 

                                "NuReconstruction/DoubleNeutrino/CXX/Tensors.cxx", 
                                
                                "NuReconstruction/DoubleNeutrino/Shared/Floats.cxx", 
                            ]
            ),


        ], 
        cmdclass = {"build_ext" : BuildExtension}
)
