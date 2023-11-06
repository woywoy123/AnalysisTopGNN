from AnalysisG._cmodules.Runner import Runner
from AnalysisG.Notification import _Condor
from subprocess import Popen, PIPE, STDOUT
from AnalysisG.IO import PickleObject
from AnalysisG.Tools import Tools
from .script_builder import *
import subprocess

class Condor(Runner, Tools, _Condor):

    def __init__(self):
        Runner.__init__(self)
        _Condor.__init__(self)
        self.Caller = "Condor"

    def AddJob(self, job_name, instance, memory = "", time = "", waitfor = []):
        self.ProjectInheritance(instance)
        self._CheckWaitFor(job_name, waitfor)
        if self.RegisterAnalysis(job_name, instance): pass
        else: return False
        if memory is not None: pass
        else: memory = ""

        if time is not None: pass
        else: time = ""

        self.RegisterJob(job_name, memory, time, waitfor)

    def __DumpConfiguration__(self):
        self.Make()
        build_shell_script(self)
        build_condor_script(self)
        build_analysis_script(self)
        build_dag(self)

        dag = self.path(self._dag_path)
        self.mkdir(dag)
        f = open(self._dag_path, "w")
        f.write(self._dag_script)
        f.close()

        bashes = self.path(self._bash_path[0])
        self.mkdir(bashes)
        f = open(self._bash_path[0], "w")
        f.write(self._bash_path[1])
        f.close()

        for i in self.Jobs:
            self.DumpedJob(i, bashes)

            self.mkdir(self.abs(self.Jobs[i].py_path))
            f = open(self.Jobs[i].py_path + "/" + i + ".py", "w")
            f.write(self.Jobs[i].python_script)
            f.close()
            PickleObject(self.Jobs[i].ana_s, self.Jobs[i].set_path)

            f = open(bashes + "/" + i + ".sh", "w")
            f.write(self.Jobs[i].bash_script)
            f.close()

            f = open(dag + "/" + i + ".submit", "w")
            f.write(self.Jobs[i].condor_script)
            f.close()

    def LocalRun(self):
        self._CheckEnvironment()
        self.__DumpConfiguration__()
        pth = self.abs(self.OutputDirectory + "/" + self.ProjectName + "/Condor/shells/")
        cmd = ["sh", pth + "/main.sh"]
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode("UTF-8")

    def SubmitToCondor(self):
        self.__DumpConfiguration__()
        pth = self.abs(self.OutputDirectory + "/" + self.ProjectName + "/Condor/condor/")
        cmd = ["condor_submit_dag", pth + "/DAG_Submission.submit"]
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode("UTF-8")













