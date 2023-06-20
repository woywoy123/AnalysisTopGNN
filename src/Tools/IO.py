from AnalysisG.Notification import _IO
from AnalysisG._Tools import Hash
from .Miscellaneous import *
from .String import *
from glob import glob
import copy
import os


class Code:
    def __init__(self, Instance):
        self._Name = None
        self._Module = None
        self._Path = None
        self._Code = None
        self._Hash = None
        self._File = None
        self._subclass = ""
        self._Instance = Instance
        self.DumpCode(Instance)

    def DumpCode(self, Instance):
        from AnalysisG.Templates import ParticleTemplate
        from AnalysisG.Templates import EventTemplate
        from AnalysisG.Templates import GraphTemplate
        from AnalysisG.Templates import SelectionTemplate

        try:
            self._Name = Instance.__qualname__
        except AttributeError:
            try:
                self._Name = Instance.__name__
            except AttributeError:
                self._Name = type(Instance).__name__
        try:
            self._Module = Instance.__module__
        except AttributeError:
            self._Module = Instance.__package__

        self._subclass = ""
        cl = self.clone
        try:
            cl = cl()
        except:
            pass
        if cl == None:
            try:
                cl = Instance()
            except:
                pass
        if issubclass(type(cl), ParticleTemplate):
            self._subclass += "from AnalysisG.Templates import ParticleTemplate"
        elif issubclass(type(cl), EventTemplate):
            self._subclass += "from AnalysisG.Templates import EventTemplate"
        elif issubclass(type(cl), GraphTemplate):
            self._subclass += "from AnalysisG.Templates import GraphTemplate"
        elif issubclass(type(cl), SelectionTemplate):
            self._subclass += "from AnalysisG.Templates import SelectionTemplate"

        self._Path = self._Module + "." + self._Name
        self._Code = GetSourceCode(Instance)
        self._Hash = Hash(self._Code)
        self._File = GetSourceFileDirectory(Instance)
        self._FileCode = "".join(open(self._File, "r").readlines())
        self._Get, self._Import = self.checkdependency

    @property
    def checkdependency(self):
        imports = {}
        cur = ""
        for i in self._FileCode.split("\n"):
            if "import" not in i and "from" not in i:
                continue
            if "AnalysisG" in i or "PyC" in i:
                continue
            for t in i.split(" "):
                if t == "from":
                    cur = t
                if t == "import":
                    cur = t
                if cur not in imports:
                    imports[cur] = []
                elif cur == t:
                    continue
                else:
                    if "," in t:
                        imports[cur] += t.split(",")
                    else:
                        imports[cur].append(t)
        if "from" not in imports:
            return [], []
        files = {}
        for i in set(imports["from"]):
            files[i] = "/".join(self._File.split("/")[:-1]) + "/" + i + ".py"
        get = []
        for i in files:
            if not os.path.isfile(files[i]):
                continue
            for j in list(imports["import"]):
                found = j in "".join(
                    [
                        k
                        for k in ("".join(open(files[i], "r").readlines())).split("\n")
                        if "class" in k or "def" in k
                    ]
                )
                if found:
                    imports["import"].pop(imports["import"].index(j))
                try:
                    imports["from"].pop(imports["from"].index(i))
                except:
                    pass
            get.append(files[i])
        return get, imports["from"]

    @property
    def clone(self):
        Instance = self._Instance
        if callable(Instance):
            try:
                Inst = Instance()
            except:
                Inst = Instance
        _, inst = StringToObject(self._Module, self._Name)
        return inst

    @property
    def purge(self):
        self._Instance = None
        return self

    def __eq__(self, other):
        return self._Hash == other._Hash

    def __str__(self):
        return self._Hash


class IO(String, _IO):
    def __init__(self):
        self.Caller = "IO"
        self.Verbose = 3

    def lsFiles(self, directory, extension=None):
        srch = (
            glob(directory + "/*")
            if extension == None
            else glob(directory + "/*" + extension)
        )
        srch = [i for i in srch]
        if len(srch) == 0:
            self.EmptyDirectoryWarning(directory)
        return srch

    def ls(self, directory):
        try:
            return os.listdir(directory)
        except OSError:
            return []

    def IsFile(self, directory):
        if os.path.isfile(directory):
            return True
        self.FileNotFoundWarning(self.path(directory), directory.split("/")[-1])
        return False

    def ListFilesInDir(self, directory, extension, _it=0):
        F = []
        directory = copy.deepcopy(directory)
        if isinstance(directory, dict):
            for i in directory:
                if i.endswith(extension):
                    F += [i]
                elif isinstance(directory[i], list):
                    directory[i] = [i + "/" + k for k in directory[i]]
                else:
                    directory[i] = [i + "/" + directory[i]]
                F += self.ListFilesInDir(
                    [k for k in self.ListFilesInDir(directory[i], extension, _it + 1)],
                    extension,
                    _it + 1,
                )
        elif isinstance(directory, list):
            F += [
                t for k in directory for t in self.ListFilesInDir(k, extension, _it + 1)
            ]
        elif isinstance(directory, str):
            if directory.endswith("*"):
                F += self.lsFiles(directory[:-2], extension)
            elif directory.endswith(extension):
                F += [directory]
            elif len(self.lsFiles(directory, extension)) != 0:
                F += self.lsFiles(directory, extension)
            F = [i for i in F if self.IsFile(i)]

        if _it == 0:
            dirs = {self.path(i): [] for i in F}
            F = {i: [k.split("/")[-1] for k in F if self.path(k) == i] for i in dirs}
            Out = {}
            for i in F:
                if len(F[i]) == 0:
                    self.EmptyDirectoryWarning(i)
                    continue
                Out[i] = F[i]
            self.FoundFiles(Out)
            return Out
        return F

    @property
    def pwd(self):
        return os.getcwd()

    def abs(self, directory):
        return os.path.abspath(directory)

    def path(self, inpt):
        return os.path.dirname(self.abs(inpt))

    def filename(self, inpt):
        return inpt.split("/")[-1]

    def mkdir(self, directory):
        try:
            os.makedirs(self.abs(directory))
        except FileExistsError:
            pass

    def rm(self, directory):
        try:
            os.remove(self.abs(directory))
        except IsADirectoryError:
            import shutil

            shutil.rmtree(self.abs(directory))
        except FileNotFoundError:
            pass

    def cd(self, directory):
        os.chdir(directory)
        return self.pwd

    def Hash(self, string):
        return Hash(string)
