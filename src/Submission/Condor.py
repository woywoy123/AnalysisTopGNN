import AnalysisTopGNN
from AnalysisTopGNN.Notification import Condor_
from AnalysisTopGNN.Generators import Settings
import os, stat 

class CondorScript(Settings):

    def __init__(self):
        self.Caller = "CONDORSCRIPT"
        Settings.__init__(self)
        self._config = []
    
    def __Memory(self):
        if self.Memory == None:
            return
        fact = 1024 if self.Memory.endswith("GB") else 1
        self.__AddConfig("Request_Memory = " + str(fact*float(self.Memory[:-2])))
    
    def __Time(self):
        if self.Time == None:
            return
        fact = 60*60 if self.Time.endswith("h") else fact
        fact = 60 if self.Time.endswith("m") else fact
        self.__AddConfig("+RequestRuntime = " + str(fact*float(self.Time[:-1])))       
    
    def __Exec(self):
        self.__AddConfig("executable = " + self.ExecPath + "/" + self.ScriptName + ".sh")
        self.__AddConfig("error = " + self.ExecPath + "/results.error.$(ClusterID)")
        self.__AddConfig('Requirements = OpSysAndVer == "' + self.OpSysAndVer + '"')
    
    def __Hardware(self):
        string = "Request_GPUs = 1" if self.Device == "cuda" else False
        if string:
            self.__AddConfig(string)
            return 
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
        if self.CondaEnv:
            self.__AddConfig('eval "$(conda shell.bash hook)"')
            self.__AddConfig("conda activate " + self.CondaEnv)
        elif self.PythonVenv:
            self.__AddConfig('source ' + self.PythonVenv)
        self.__AddConfig("python " + self.ExecPath + "/" + self.ScriptName + ".py")

    def __AddConfig(self, inpt):
        self._config.append(inpt)
            

class AnalysisScript(AnalysisTopGNN.Tools.General.Tools):

    def __init__(self):
        self.Code = []
        self.Script = []
        self.Name = None
        self.OutDir = None

    def __Build(self, txt, name):
        f = open(self.OutDir + "/" + name + ".py", "w")
        f.write(txt)
        f.close()

    def GroupHash(self, obj):
        for i in range(len(self.Script)):
            _hash = str(hex(id(obj)))
            if _hash not in self.Script[i]:
                continue
            self.Script[i] = self.Script[i].replace("'" + _hash + "'", obj.Name)
            return self.Script[i].split(" = ")[0].split(".")[-1]
        return False

    def Compile(self):

        Ad_key = {}
        Script = ["import sys"]
        Script += ["sys.path.append('" + self.abs("/".join(self.OutDir.split("/")[:-1]) + "/_SharedCode/')")]
        Script += ["from Event import *"]
        for i in self.Code:
            key = self.GroupHash(i)
            if key not in Ad_key and key:
                Ad_key[key] = []

            if "(ParticleTemplate):" in i.Code:
                self.__Build(i.Code, "../_SharedCode/Particles")
                continue

            if "(EventTemplate):" in i.Code:
                string = ["from AnalysisTopGNN.Templates import EventTemplate", "from Particles import *", "", i.Code]
                self.__Build("\n".join(string), "../_SharedCode/Event")
                self.Script += ["<*AnalysisName*>.Event = Event"]
                continue

            if "(EventGraphTemplate):" in i.Code:
                Ad_key[key] = ["from AnalysisTopGNN.Templates import EventGraphTemplate", "", i.Code]
                continue
            
            if "(Selection):" in i.Code:
                Ad_key[key] = ["from AnalysisTopGNN.Templates import Selection", "", i.Code]
                continue

            Ad_key[key].append(i.Code)
        
        for i in Ad_key:
            self.__Build("\n".join(Ad_key[i]), i)
            Script += ["from " + i + " import * "]
        
        Script += ["from AnalysisTopGNN.Generators import Analysis"]
        Script += ["", "ANA = Analysis()"]
        Script += [i.replace("<*AnalysisName*>", "ANA") for i in self.Script]
        Script += ["ANA.Launch()"]
        self.__Build("\n".join(Script), self.Name)



class JobSpecification(AnalysisTopGNN.Tools.General.Tools, Settings):

    def __init__(self):
        self.Caller = "JOBSPECS"
        Settings.__init__(self)
   
    def __Preconf(self):
        if self.EventCache != None and self.Job.Event != None:
            self.Job.EventCache = self.EventCache
        if self.DataCache != None and self.Job.EventGraph != None:
            self.Job.DataCache = self.DataCache
        self.Device = self.Job.Device

    def __Build(self, txt, name, pth, exe = True):
        f = open(pth + "/" + name, "w")
        f.write("\n".join(txt))
        f.close()

        if exe: 
            os.chmod(pth + "/" + name, stat.S_IRWXU)

    def Launch(self):
        self.__Preconf()
        self.Job.Launch()
    
    def DumpConfig(self):
        self.Job.OutputDirectory = self.abs(self.Job.OutputDirectory)
        pth = self.Job.OutputDirectory + "/" + self.Job.ProjectName + "/CondorDump/" + self.Name
        self.mkdir(pth)
        self.mkdir(pth + "/../_SharedCode")
        
        self.__Preconf()
        
        Ana = AnalysisScript()
        Ana.Script += self.Job.ExportAnalysisScript()
        Ana.Code += self.Job._Code
        Ana.Name = "main"
        Ana.OutDir = pth
        Ana.Compile()
       
        Con = CondorScript()
        Con.RestoreSettings(self.DumpSettings())
        Con.ExecPath = pth
        Con.Threads = self.Job.Threads

        Con.Compile()
        self.__Build(Con._config, self.Name + ".submit", pth)
        Con.Shell()
        self.__Build(Con._config, "main.sh", pth, True)

class Condor(AnalysisTopGNN.Tools.General.Tools, Condor_, Settings):
    def __init__(self):
        self.Caller = "CONDOR"
        Settings.__init__(self)
        self._Jobs = {}
        self._Time = {}
        self._Memory = {}
        self._wait = {}
        self._Complete = {}
        self._sequence = {}
        self._Device = {}
    
    def AddJob(self, name, instance, memory = None, time = None, waitfor = None):
        if name not in self._Jobs:
            self._Jobs[name] = JobSpecification()
            self._Jobs[name].Job = instance
            self._Jobs[name].Name = name

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
    
    def __Sequencer(self):
        def Recursion(inpt, key = None, start = None):
            if key == None and start == None:
                out = {}
                for i in inpt:
                    out[i] = [k for k in Recursion(inpt[i], i, inpt).split("<-") if k != i]
                return out
            if len(inpt) == 0:
                return key
            for i in inpt:
                key += "<-" + Recursion(start[i], i, start)
            return key 
        self._sequence = Recursion(self._wait) 
        for i in self._wait:
            self._Complete[i] = False

    def LocalDryRun(self):
        self.__Sequencer()
        for i in self._sequence:
            jb = [i] if len(self._sequence[i]) == 0 else self._sequence[i]
            jb = [i for i in jb if self._Complete[i] == False]
            for j in jb:
                self._Jobs[j].EventCache = self.EventCache
                self._Jobs[j].DataCache = self.DataCache 
                self.RunningJob(j)
                
                self._Jobs[j].Launch()
                
                self._Complete[j] = True
                del self._Jobs[j]
                self._Jobs[j] = None
        self.FinishExit()

    def DumpCondorJobs(self):
        self.__Sequencer()
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
                self._Jobs[j].RestoreSettings(self.DumpSettings())
                self._Jobs[j].DumpConfig()
                
                self._Complete[j] = True

        F = open(outDir + "/" + self.ProjectName + "/CondorDump/DAGSUBMISSION.submit", "w")
        F.write("\n".join(DAG))
        F.close()
        
        F = open(outDir + "/" + self.ProjectName + "/CondorDump/RunAsBash.sh", "w")
        F.write("#!/bin/bash\n")
        
        jb = []
        self._Complete = { i : False for i in self._Complete }

        self._sequence = { j : [j] + self._sequence[j] for j in self._sequence }
        for j in self._sequence:
            for k in reversed(self._sequence[j]):
                if self._Complete[k]:
                    continue
                self._Complete[k] = True
                F.write("bash " + k + "/main.sh\n")
            

        F.close()
