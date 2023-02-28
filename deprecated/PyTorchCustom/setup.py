from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CppExtension

setup(
        name = "PyTorchCustom", 
        version = "1.0", 
        ext_modules = [
            CppExtension("LorentzVector", ["Source/LorentzVector.cpp"])
        ],
        cmdclass = {"build_ext" : BuildExtension}
    )
