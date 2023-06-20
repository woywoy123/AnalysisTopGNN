from setuptools.command.install import install as InstallCommand
from setuptools import setup, Extension
from pathlib import Path
import os

# import torch


class build_ext:
    def __init__(self):
        self.cuda = torch.cuda.is_available()

    def _check(self, inpt, ext=[".h", ".cxx", ".cu"]):
        if isinstance(ext, str):
            return inpt.endswith(ext)
        return len([i for i in ext if i in inpt and not ".swp" in inpt]) > 0

    def _clean(self, inpt):
        if isinstance(inpt, list):
            return [j for i in inpt for j in self._clean(i)]
        if not self._check(inpt, ["#include"]):
            return []
        if self._check(inpt, ["<", ">"]):
            return []
        inpt = inpt.replace("\n", "")
        inpt = inpt.replace(" ", "")
        inpt = inpt.replace('"', "")
        return [inpt.split("#include")[-1]]

    def _getPath(self, inpt, src):
        src = src.split("/")[:-1] + [inpt]
        pth = os.path.abspath("/".join(src))
        pth = pth.split(os.getcwd())[-1][1:]
        return pth

    def _reference(self, inpt, ref):
        try:
            _ref = self._clean(open(inpt).readlines())
            if len(_ref) == 0:
                return False
        except:
            return False
        return ref in [self._getPath(i, inpt) for i in _ref]

    def _recursive(self, inpt):
        if isinstance(inpt, str):
            inpt = [inpt] if self._check(inpt) else []
        else:
            inpt = [i for i in inpt if self._check(i)]

        out = []
        out += list(inpt)
        f = {}
        for i in inpt:
            try:
                v = open(i).readlines()
            except:
                continue
            f[i] = self._clean(v)
        f = {self._getPath(k, i): i for i in f for k in f[i]}
        for j in list(f):
            out += [j] + self._recursive(j)

        this_f = inpt.pop()
        for p in Path("/".join(this_f.split("/")[:2])).rglob("*"):
            if (
                self._check(str(p), ".cu")
                or self._check(str(p), ".h")
                or self._check(str(p), ".cxx")
            ):
                pass
            else:
                continue
            if "Shared" in str(p):
                continue
            if "CUDA" in this_f and ".cu" in str(p):
                pass
            elif not self._reference(str(p), this_f):
                continue
            out.append(str(p))
        return list(set(out))

    @property
    def cmd(self):
        import torch.utils.cpp_extension as ext

        PACKAGES_CXX = {
            "PyC.Transform.Floats": "src/Transform/Shared/Floats.cxx",
            # "PyC.Transform.Tensors" : "src/Transform/Shared/Tensors.cxx",
            # "PyC.Operators.Tensors" : "src/Operators/Shared/Tensors.cxx",
            # "PyC.Physics.Tensors.Cartesian" : "src/Physics/Shared/CartesianTensors.cxx",
            # "PyC.Physics.Tensors.Polar" : "src/Physics/Shared/PolarTensors.cxx",
            # "PyC.NuSol.Tensors" : "src/NuRecon/Shared/Tensor.cxx",
        }

        PACKAGES_CUDA = {
            "PyC.Transform.CUDA": "src/Transform/Shared/CUDA.cxx",
            # "PyC.Operators.CUDA" : "src/Operators/Shared/CUDA.cxx",
            # "PyC.Physics.CUDA.Cartesian" : "src/Physics/Shared/CartesianCUDA.cxx",
            # "PyC.Physics.CUDA.Polar" : "src/Physics/Shared/PolarCUDA.cxx",
            # "PyC.NuSol.CUDA" : "src/NuRecon/Shared/CUDA.cxx"
        }

        PACKAGES = {}
        PACKAGES |= PACKAGES_CXX
        PACKAGES |= PACKAGES_CUDA if self.cuda else {}
        DEPENDS = {}
        REFDEPENDS = {}
        self.INST_ = []
        self.INST_H = {}

        for pkg in PACKAGES:
            deps = self._recursive(PACKAGES[pkg])
            HEADER = [k for k in deps if self._check(k, ".h")]
            CXX = [k for k in deps if self._check(k, ".cxx")]
            CU = [k for k in deps if self._check(k, ".cu")]

            dic = {
                "name": pkg,
                "sources": CXX + CU,
                "extra_compile_args": ["-std=c++14"],
            }
            if not len(CU):
                dic = Extension(
                    **(dic | {"language": "c++", "include_dirs": ext.include_paths()})
                )
            elif self.cuda:
                dic = ext.CUDAExtension(**dic)
            else:
                continue

            self.INST_.append(dic)
            self.INST_H[pkg] = HEADER

        cmd = {
            "ext_modules": self.INST_,
            "package_data": self.INST_H,
            "cmdclass": {"build_ext": ext.BuildExtension},
        }
        return cmd


def _getTorch():
    import subprocess

    def _getcmd(cmd):
        return subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, shell=True
        ).decode("UTF-8")

    gcc_cu = {
        12: ["12.1.0"],
        11: ["11.4.1", "11.5", "11.6", "11.7", "11.8"],
        10: ["11.1", "11.2", "11.3", "11.4.0"],
        9: ["11"],
        8: ["10.1", "10.2"],
        7: ["9.2", "10.0"],
        6: ["9.0", "9.1"],
        5.3: ["8"],
    }

    nvcc = _getcmd("n --version | grep release | awk '{print $5}'")[:-2]
    this_gcc = [i for i in gcc_cu if nvcc in gcc_cu[i]]
    gcc = _getcmd("gcc --version | grep gcc | awk '{print $3}'").split("-")[0]
    if len(this_gcc) > 0 and float(this_gcc[0]) <= this_gcc[0]:
        cu = "cu" + nvcc.replace(".", "")
    else:
        cu = "cpu"
    _torch = "--extra-index-url https://download.pytorch.org/whl/" + cu
    f = open("requirements.txt", "w")
    f.write(_torch + "\n")
    f.write("torch==2.0.1+" + cu)
    f.close()


# class Install(InstallCommand):
#    def run(self, *args, **kwargs):
#        _getTorch()
#        #print(torch.cuda.is_available())
#        print("here")
#        #ext_ = build_ext()
#        InstallCommand.run(self, *args, **kwargs)
#
# class Test(InstallCommand):
#    def run(self, *args, **kwargs):
#        print(torch.cuda.is_available())
#        exit()
#        InstallCommand.run(self, *args, **kwargs)
#
exit()
if __name__ == "__main__":
    setup(
        cmdclass={
            "test": Test,
        }
    )
