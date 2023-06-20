from setuptools import setup, Extension
import Cython.Build

setup(
    ext_modules=[
        Extension("AnalysisTopGNN.Vectors", sources=["src/Vectors/Lorentz.pyx"])
    ],
    cmdclass={"build_ext": Cython.Build.build_ext},
)
