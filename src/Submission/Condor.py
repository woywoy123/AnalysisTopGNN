import AnalysisG
from AnalysisG.Notification import _Condor
from AnalysisG.Settings import Settings
import os, stat
import subprocess


class CondorScript(Settings):
    def __init__(self):
        self.Caller = "CONDORSCRIPT"
        Settings.__init__(self)
        self._config = []

    def __Memory(self):
        if self.Memory == None:
            return
        fact = 1024 if self.Memory.endswith("GB") else 1
        self.__AddConfig("Request_Memory = " + str(fact * float(self.Memory[:-2])))

    def __Time(self):
        if self.Time == None:
            return
        fact = 60 * 60 if self.Time.endswith("h") else fact
        fact = 60 if self.Time.endswith("m") else fact
        self.__AddConfig("+RequestRuntime = " + str(fact * float(self.Time[:-1])))

    def __Exec(self):
        self.__AddConfig(
            "executable = " + self.ExecPath + "/" + self.ScriptName + ".sh"
        )
        self.__AddConfig("error = " + self.ExecPath + "/results.error.$(ClusterID)")
        self.__AddConfig('Requirements = OpSysAndVer == "' + self.OpSysAndVer + '"')

    def __Hardware(self):
        string = "Request_GPUs = 1" if self.Device == "cuda" else False
        if string:
            return self.__AddConfig(string)
        self.__AddConfig("Request_Cpus = " + str(self.Threads))

    def Compile(self):
        self.__Exec()
        self.__Hardware()
        self.__Memory()
        self.__Time()
        self.__AddConfig("queue 1")

    def Shell(self):
        self._config = []
        self.__AddConfig("#!/bin/bash")
        self.__AddConfig("source ~/.bashrc")
        if self.CondaEnv is not None:
            self.__AddConfig('eval "$(conda shell.bash hook)"')
            self.__AddConfig("conda activate " + self.CondaEnv)
        elif self.PythonVenv is not None:
            self.__AddConfig("source " + self.PythonVenv)
        self.__AddConfig("python " + self.ExecPath + "/" + self.ScriptName + ".py")

    def __AddConfig(self, inpt):
        self._config.append(inpt)


class AnalysisScript(AnalysisG.Tools.General.Tools, Settings):
    def __init__(self):
        self.Code = {}
        self.Config = {}
        self.Name = None
        self.OutDir = None
        Settings.__init__(self, "ANALYSIS")

    def __Build(self, txt, name):
        f = open(self.OutDir + "/" + name + ".py", "w")
        f.write(txt)
        f.close()

    def Compile(self):
        s_dir = self.abs("/".join(self.OutDir.split("/")[:-1])) + "/_SharedCode/"
        shared = {}
        shared["code"] = {}
        shared["imports"] = ["import sys"]
        shared["imports"] += ["sys.path.append('" + s_dir + "')"]
        shared["imports"] += ["from AnalysisG import Analysis"]

        script = ["<*Analysis*> = Analysis()"]
        for i in self.Config:
            if i.startswith("_"):
                continue
            if i in self.Code:
                continue
            if isinstance(self.Config[i], str):
                script += [
                    "<*Analysis*>." + i + " = " + "'" + str(self.Config[i]) + "'"
                ]
            else:
                script += ["<*Analysis*>." + i + " = " + str(self.Config[i])]

        for i in self.Code:
            if i == "Event":
                shared["imports"] += [
                    "from " + self.Code[i]._Name + " import " + self.Code[i]._Name
                ]
                script += ["<*Analysis*>.Event = " + self.Code[i]._Name]
                shared["code"][self.Code[i]._Name] = [
                    "from AnalysisG.Templates import EventTemplate"
                ]
                shared["code"][self.Code[i]._Name] += [
                    "from "
                    + list(self.Code["Particles"].values())[0]
                    ._File.split("/")[-1]
                    .replace(".py", "")
                    + " import "
                ]
                shared["code"][self.Code[i]._Name][-1] += ", ".join(
                    [p._Name for p in self.Code["Particles"].values()]
                )
                shared["code"][self.Code[i]._Name] += [""]
                shared["code"][self.Code[i]._Name] += [self.Code[i]._Code]
            elif i == "Particles":
                for part in self.Code[i].values():
                    shared["code"][part._File] = [part._FileCode]
            elif i == "Model":
                shared["imports"] += [
                    "from " + self.Code[i]._Name + " import " + self.Code[i]._Name
                ]
                self.__Build(self.Code[i]._FileCode, self.Code[i]._Name)
                script += ["<*Analysis*>." + i + " = " + self.Code[i]._Name]
            else:
                if type(self.Code[i]).__name__ == "Code":
                    shared["imports"] += [
                        "from " + self.Code[i]._Name + " import " + self.Code[i]._Name
                    ]
                    self.__Build(
                        self.Code[i]._subclass + "\n\n" + self.Code[i]._Code,
                        self.Code[i]._Name,
                    )
                    script += ["<*Analysis*>." + i + " = " + self.Code[i]._Name]
                else:
                    _buildCode = ""
                    for j in self.Code[i]:
                        for k in self.Code[i][j]._Get:
                            _buildCode += (
                                "import sys\n" if "import sys" not in _buildCode else ""
                            )
                            _buildCode += (
                                "sys.path.append('"
                                + "/".join(k.split("/")[:-1])
                                + "')\n"
                            )
                            _buildCode += (
                                "from "
                                + k.split("/")[-1].replace(".py", "")
                                + " import *\n"
                            )
                        for k in self.Code[i][j]._Import:
                            _buildCode += "try: from " + k + " import *\n"
                            _buildCode += "except: pass\n"

                    shared["imports"] += [
                        "from "
                        + i
                        + " import "
                        + ", ".join([self.Code[i][j]._Name for j in self.Code[i]])
                    ]
                    _buildCode += "\n".join(
                        set([self.Code[i][j]._subclass for j in self.Code[i]])
                    )
                    for j in self.Code[i]:
                        _buildCode += "\n\n" + self.Code[i][j]._Code
                    self.__Build(_buildCode, i)
                    script += ["<*Analysis*>." + i + " = {"]
                    for j in self.Code[i]:
                        script[-1] += (
                            "'" + j + "'" + " : " + self.Code[i][j]._Name + ", "
                        )
                    script[-1] = ", ".join(script[-1].split(", ")[:-1]) + "}"

        for i in shared["code"]:
            fname = i.split("/")[-1]
            if not fname.endswith(".py"):
                fname += ".py"
            fname = s_dir + fname
            f = open(fname, "w")
            f.write("\n".join(shared["code"][i]))
            f.close()
        script = shared["imports"] + [""] + script + ["<*Analysis*>.Launch"]
        self.__Build("\n".join(script).replace("<*Analysis*>", "Ana"), self.Name)


class JobSpecification(AnalysisG.Tools.General.Tools, Settings):
    def __init__(self):
        self.Caller = "JOBSPECS"
        Settings.__init__(self)

    def __Build(self, txt, name, pth, exe=True):
        f = open(pth + "/" + name, "w")
        f.write("\n".join(txt))
        f.close()
        if exe:
            os.chmod(pth + "/" + name, stat.S_IRWXU)

    @property
    def Launch(self):
        self.Job.Launch

    def DumpConfig(self):
        self.Job.__build__
        pth = self.Job.OutputDirectory + "/CondorDump/" + self.Name
        self.mkdir(pth)
        self.mkdir(pth + "/../_SharedCode")

        self.Job.OutputDirectory = "/".join(self.Job.OutputDirectory.split("/")[:-1])
        conf = self.Job.DumpSettings

        Ana = AnalysisScript()
        Ana.Name = "main"
        Ana.OutDir = pth
        Ana.Code.update(self.Job.Launch)
        Ana.Config.update(conf)
        Ana.Compile()

        self.ImportSettings(self.Job)

        Con = CondorScript()
        Con.ImportSettings(self)
        Con.ExecPath = pth
        Con.Device = self.Device
        Con.Threads = self.Job.Threads
        Con.Compile()

        self.__Build(Con._config, self.Name + ".submit", pth)
        Con.Shell()
        self.__Build(Con._config, "main.sh", pth, True)


class Condor(AnalysisG.Tools.General.Tools, _Condor, Settings):
    def __init__(self):
        self.Caller = "CONDOR"
        Settings.__init__(self)
        self._Jobs = {}
        self._Time = {}
        self._Memory = {}
        self._wait = {}
        self._Complete = {}
        self._sequence = {}
        self._dumped = False

    def AddJob(self, name, instance, memory=None, time=None, waitfor=None):
        if name not in self._Jobs:
            self._Jobs[name] = JobSpecification()
            self._Jobs[name].Job = instance
            self._Jobs[name].Job._condor = True
            self._Jobs[name].Name = name
            if self.EventCache is not None:
                self._Jobs[name].Job.EventCache = self.EventCache
            if self.DataCache is not None:
                self._Jobs[name].Job.DataCache = self.DataCache
        self.AddListToDict(self._wait, name)
        if waitfor == None:
            pass
        elif isinstance(waitfor, str):
            self._wait[name].append(waitfor)
        elif isinstance(waitfor, list):
            self._wait[name] += waitfor
        self._Jobs[name].Memory = memory
        self._Jobs[name].Time = time
        self.ProjectInheritance(instance)

    @property
    def __Sequencer(self):
        def Recursion(inpt, key=None, start=None):
            if key == None and start == None:
                out = {}
                for i in inpt:
                    out[i] = [
                        k for k in Recursion(inpt[i], i, inpt).split("<-") if k != i
                    ]
                return out
            if len(inpt) == 0:
                return key
            for i in inpt:
                key += (
                    "<-" + Recursion(start[i], i, start)
                    if self._CheckWaitFor(start, i)
                    else ""
                )
            return key

        self._sequence = Recursion(self._wait)
        for i in self._wait:
            self._Complete[i] = False

    @property
    def LocalRun(self):
        self.__Sequencer
        self._sequence = {j: [j] + self._sequence[j] for j in self._sequence}
        for t in self._sequence:
            for j in reversed(self._sequence[t]):
                if self._Complete[j]:
                    continue
                self.RunningJob(j)
                self._Jobs[j].Job._condor = False
                self._Jobs[j].Launch
                self._Complete[j] = True
                del self._Jobs[j]
                self._Jobs[j] = None
        self.FinishExit()

    @property
    def TestCondorShell(self):
        pwd = self.pwd
        self.cd(self.abs(self.OutputDirectory + "/" + self.ProjectName + "/CondorDump"))
        subprocess.call(["sh", "RunAsBash.sh"])
        self.cd(pwd)

    @property
    def SubmitToCondor(self):
        if self._dumped == False:
            self.DumpCondorJobs
        pwd = self.pwd
        self.cd(self.abs(self.OutputDirectory + "/" + self.ProjectName + "/CondorDump"))
        subprocess.Popen(["condor_submit_dag", "DAGSUBMISSION.submit"])
        self.cd(pwd)

    @property
    def DumpCondorJobs(self):
        self._CheckEnvironment
        self.__Sequencer
        outDir = self.abs(self.OutputDirectory)
        self.mkdir(outDir + "/" + self.ProjectName + "/CondorDump")
        DAG = ["JOB " + i + " " + i + "/" + i + ".submit" for i in self._sequence]
        for i in self._sequence:
            jb = [i] if len(self._sequence[i]) == 0 else self._sequence[i]
            jb = [i for i in jb if self._Complete[i] == False]

            self.mkdir(outDir + "/" + self.ProjectName + "/CondorDump/" + i)
            self.DumpedJob(i, outDir + "/" + self.ProjectName + "/CondorDump/" + i)

            for p in reversed(self._sequence[i]):
                s = "PARENT " + p + " CHILD " + i
                if s not in DAG and p in self._wait[i]:
                    DAG.append(s)
            for j in jb:
                self._Jobs[j].ImportSettings(self)
                self._Jobs[j].DumpConfig()
                self._Complete[j] = True
        for j in self._Complete:
            if self._Complete[j] == True:
                continue
            self._Jobs[j].ImportSettings(self)
            self._Jobs[j].DumpConfig()
            self._Complete[j] = True

        F = open(
            outDir + "/" + self.ProjectName + "/CondorDump/DAGSUBMISSION.submit", "w"
        )
        F.write("\n".join(DAG))
        F.close()

        F = open(outDir + "/" + self.ProjectName + "/CondorDump/RunAsBash.sh", "w")
        F.write("#!/bin/bash\n")

        jb = []
        self._Complete = {i: False for i in self._Complete}

        self._sequence = {j: [j] + self._sequence[j] for j in self._sequence}
        for j in self._sequence:
            for k in reversed(self._sequence[j]):
                if self._Complete[k]:
                    continue
                self._Complete[k] = True
                F.write("bash " + k + "/main.sh\n")
        F.close()
        self._dumped = True
