from setuptools import setup, Extension
from Cython.Build import cythonize

src = "src/cmodules/"

def h_format(name): return [src + name + "/"]
def s_format(name, incl, cxx_ = True):
    if incl: source = [src + "cyincludes/cy" + name + ".pyx"]
    else: source = []
    if not cxx_: return source
    source += [src + name + "/" + name + ".cxx"]
    return source

def make(module, name, dependency, cxx_ = True, add_cy = []):
    _src = s_format(name, True, cxx_)
    for i in dependency: _src += s_format(i, False)
    _src += [src + "cyincludes/cy"+i+".pyx" for i in add_cy]
    _incl = h_format(name)
    for i in dependency: _incl += h_format(i)

    x = {"name" : None, "sources" : _src, "include_dirs" : _incl}
    x["name"] = "AnalysisG._cmodules." + module
    return x

modules = [
        make("ctools", "tooling", ["abstractions"], False),
        make("code", "code", ["abstractions"]),
        make("EventTemplate", "event", ["abstractions", "code"]),
        make("ParticleTemplate", "particle", ["abstractions"]),
        make("MetaData", "metadata", ["abstractions"]),
        make("GraphTemplate", "graph", ["abstractions", "code"]),
        make("SelectionTemplate", "selection", ["abstractions", "code"]),
        make("cWrapping", "wrapping", ["abstractions"], False),
        make("cPlots", "plotting", ["abstractions"]),
        make("cOptimizer", "optimizer", ["abstractions", "epoch"]),
        make("Runner", "runner", ["abstractions"], False),
        make("SampleTracer", "sampletracer", ["root", "abstractions", "metadata", "event", "graph", "selection", "code"])
]

for i in range(len(modules)):
    modules[i]["language"] = "c++"
    modules[i] = Extension(**modules[i])

setup(ext_modules = cythonize(modules, nthreads = 12))



