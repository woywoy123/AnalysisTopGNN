from AnalysisG.Notification import _IO
from glob import glob
import shutil
import copy
import os

class Tools(_IO):
    def __init__(self):
        self.Caller = "IO"
        self.Verbose = 3

    def lsFiles(self, directory, extension=None):
        files = []
        for i in self.ls(directory):
            p = directory + "/" + i
            if self.IsFile(p, True): files += [p]
            else: files += self.lsFiles(p, extension)
        if extension is None: return [self.abs(i) for i in files]
        else: return [self.abs(i) for i in files if i.endswith(extension)]
        return files

    def ls(self, directory):
        try: return os.listdir(directory)
        except OSError: return []

    def IsPath(self, directory):
        try: return os.listdir(directory)
        except OSError: return False

    def IsFile(self, directory, quiet = False):
        if os.path.isfile(directory): return True
        if not quiet: self.FileNotFoundWarning(self.path(directory), directory.split("/")[-1])
        return False

    def ListFilesInDir(self, dirc, extension, _it=0):
        F = []
        dirc = copy.deepcopy(dirc)
        if isinstance(dirc, dict):
            for i in dirc:
                if i.endswith(extension): F += [i]
                elif isinstance(dirc[i], list): dirc[i] = [i + "/" + k for k in dirc[i]]
                else: dirc[i] = [i + "/" + dirc[i]]
                x = [k for k in self.ListFilesInDir(dirc[i], extension, _it + 1)]
                F += self.ListFilesInDir(x, extension, _it+1)
        elif isinstance(dirc, list):
            F += [t for k in dirc for t in self.ListFilesInDir(k, extension, _it + 1)]
        elif isinstance(dirc, str):
            if dirc.endswith("*"): F += self.lsFiles(dirc[:-2], extension)
            elif dirc.endswith(extension): F += [dirc]
            elif len(self.lsFiles(dirc, extension)) != 0:
                F += self.lsFiles(dirc, extension)
            F = [i for i in F if self.IsFile(i)]
        if _it: return F

        dirs = {self.path(i): [] for i in F}
        F = {i: [k.split("/")[-1] for k in F if self.path(k) == i] for i in dirs}
        Out = {}
        for i in F:
            if len(F[i]): Out[i] = F[i]; continue
            self.EmptyDirectoryWarning(i)
        self.FoundFiles(Out)
        return Out

    def pwd(self): return os.getcwd()

    def abs(self, directory): return os.path.abspath(directory)

    def path(self, inpt): return os.path.dirname(self.abs(inpt))

    def filename(self, inpt): return inpt.split("/")[-1]

    def mkdir(self, directory):
        try: os.makedirs(self.abs(directory))
        except FileExistsError: pass

    def rm(self, directory):
        try: os.remove(self.abs(directory))
        except IsADirectoryError:
            try: shutil.rmtree(self.abs(directory))
            except: pass
        except FileNotFoundError: pass
        except: pass

    def cd(self, directory):
        os.chdir(directory)
        return self.pwd()

    def MergeListsInDict(self, inpt):
        if isinstance(inpt, list): return inpt
        out = []
        for i in inpt: out += self.MergeListsInDict(inpt[i])
        return self.MergeNestedList(out)

    def DictToList(self, inpt, key=None):
        if isinstance(inpt, str) and key is not None:
            return key + "/" + inpt
        if isinstance(inpt, list) and key is not None:
            return [self.DictToList(i, key) for i in inpt]
        if isinstance(inpt, dict) and key is not None:
            return [self.DictToList(inpt[i], i) for i in inpt]
        if key is None:
            out = []
            for i in inpt: out += self.DictToList(inpt[i], i)
            return out

    def Quantize(self, inpt, size):
        for i in range(0, len(inpt), size): yield inpt[i : i + size]

    def MergeNestedList(self, inpt):
        if isinstance(inpt, list) == False: return [inpt]
        out = []
        for i in inpt: out += self.MergeNestedList(i)
        return out

    def MergeData(self, ob2, ob1):
        if isinstance(ob1, dict) and isinstance(ob2, dict):
            l1, l2 = list(ob1), list(ob2)
            out = {}
            for i in set(l1 + l2):
                if isinstance(ob1[i] if i in l1 else ob2[i], dict):
                    ob1[i] = {} if i not in l1 else ob1[i]
                    ob2[i] = {} if i not in l2 else ob2[i]
                    out[i] = self.MergeData(ob1[i], ob2[i])

                elif isinstance(ob1[i] if i in l1 else ob2[i], list):
                    ob1[i] = [] if i not in l1 else ob1[i]
                    ob2[i] = [] if i not in l2 else ob2[i]
                    out[i] = self.MergeData(ob1[i], ob2[i])

                else:
                    try: o1 = ob1[i]
                    except KeyError: o1 = None
                    except IndexError: o1 = None

                    try: o2 = ob2[i]
                    except KeyError: o2 = None
                    except IndexError: o2 = None

                    if o1 is not None and o2 is not None: out[i] = o1 + o2
                    elif o1 is not None: out[i] = o1
                    elif o2 is not None: out[i] = o2
                    else: out[i] = None
            return out

        if isinstance(ob1, list) and isinstance(ob2, list):
            l1, l2 = len(ob1), len(ob2)
            out = []
            for i in range(l1 if l1 > l2 else l2):
                if isinstance(ob1[i] if i >= l2 else ob2[i], dict):
                    out.append(self.MergeData(ob1[i], ob2[i]))
                if isinstance(ob1[i] if i >= l2 else ob2[i], list):
                    inpt1 = ob1[i] if l1 > i else []
                    inpt2 = ob2[i] if l2 > i else []
                    out.append(self.MergeData(inpt1, inpt2))
                else: return ob1 + ob2
            return out

        if isinstance(ob1, int) and isinstance(ob2, int): return ob1 + ob2
        if isinstance(ob1, float) and isinstance(ob2, float): return ob1 + ob2
