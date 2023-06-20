from setuptools import setup, Extension
from Cython.Build import cythonize

ext_mod = [
    Extension(
                name = "AnalysisG.Templates.ParticleTemplate",
                sources = [
                    "src/Templates/Cython/Particle.pyx",
                    "src/Templates/CXX/Templates.cxx",
                    "src/Templates/CXX/Tools.cxx",
                ],
    ),
    Extension(
                name = "AnalysisG.Templates.EventTemplate",
                sources = [
                    "src/Templates/Cython/Event.pyx",
                    "src/Templates/CXX/Templates.cxx",
                    "src/Templates/CXX/Tools.cxx",
                ],
    ),
    Extension(
                name = "AnalysisG.Tracer",
                sources = [
                    "src/Templates/Cython/ROOT.pyx",
                    "src/Templates/CXX/ROOT.cxx",
                    "src/Templates/CXX/Tools.cxx",
                ],
    ),
    Extension(
                name = "AnalysisG._Tools",
                sources = [
                    "src/Templates/Cython/Tools.pyx",
                    "src/Templates/CXX/Tools.cxx",
                ],
    ),
]

setup(ext_modules = cythonize(ext_mod, nthreads = 12))



