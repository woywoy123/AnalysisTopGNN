# distuils: language = c++
# cython: language_level = 3

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map, pair
from libcpp cimport bool

from cython.operator cimport dereference
from cytypes cimport settings_t
from cytools cimport env, enc

cdef extern from "../abstractions/abstractions.h" namespace "Tools":
    cdef vector[string] split(string, string) except +

cdef map[string, map[string, bool]] resolve(map[string, map[string, bool]]* inpt, string key):
    cdef pair[string, map[string, bool]] i
    cdef map[string, map[string, bool]] out
    cdef string ks, start, ls

    if not key.size():
        for i in dereference(inpt):
            out[i.first]
            for ks in list(resolve(inpt, i.first)[i.first]):
                if i.first == ks: continue
                out[i.first][ks] = False
        return out
    for ks in list(dereference(inpt)[key]):
        start = key + b"<-" + ks
        for ls in list(resolve(inpt, ks)[ks]):
            start = start + b"<-" + ls
        for ks in split(start, b"<-"):
            out[key][ks] = False
    return out



cdef struct job_t:

    string job_name
    string output_directory

    string device
    string threads
    string time
    string memory

    string op_sys_ver
    string pyvenv_path
    string conda_path

cdef struct runner_t:

    map[string, map[string, bool]] sequence
    map[string, map[string, bool]] resolve
    map[string, settings_t] analysis_params
    map[string, job_t] jobs_params


cdef class Job:
    cdef public str JobName
    cdef public str OutputDirectory
    cdef public str Device
    cdef public str Threads
    cdef public str Time
    cdef public str Memory
    cdef public str bash_script
    cdef public str condor_script
    cdef public str python_script
    cdef public str dag_script
    cdef public str OpSysVer
    cdef public dict parents
    cdef public str set_path
    cdef public str py_path
    cdef public settings_t ana_s

    def __cinit__(self):
        self.JobName = ""
        self.OutputDirectory = ""
        self.Device = ""
        self.Threads = ""
        self.Time = ""
        self.Memory = ""
        self.OpSysVer = ""
        self.parents = {}

        self.bash_script = ""
        self.condor_script = ""
        self.python_script = ""
        self.dag_script = ""
        self.set_path = ""
        self.py_path = ""

    def __init__(self): pass

    cdef jImport(self, job_t* inpt):
        self.JobName = env(inpt.job_name)
        self.OutputDirectory = env(inpt.output_directory)
        self.Device = env(inpt.device)
        self.Threads = env(inpt.threads)
        self.Time = env(inpt.time)
        self.Memory = env(inpt.memory)
        self.OpSysVer = env(inpt.op_sys_ver)

    cdef sImport(self, settings_t* inpt):
        self.ana_s = dereference(inpt)


cdef class Runner:

    cdef runner_t run
    def __cinit__(self):
        self.run = runner_t()
        self.OutputDirectory = ""
        self.ProjectName = ""
        self.PythonVenv = ""
        self.CondaVenv = ""
        self._dag_path = ""
        self._bash_path = ""
        self._dag_script = ""
        self.Verbose = 0
        self.Jobs = {}

    def __init__(self): pass

    cdef Job MakeJob(self, string name):
        try: return self.Jobs[env(name)]
        except KeyError: pass
        jb = Job()
        jb.jImport(&self.run.jobs_params[name])
        jb.sImport(&self.run.analysis_params[name])
        self.Jobs[env(name)] = jb
        return self.MakeJob(name)

    def RegisterAnalysis(self, str job_name, ana):
        cdef string name = enc(job_name)
        if self.run.analysis_params.count(name): return False
        self.run.analysis_params[name] = ana.ExportSettings()
        self.run.jobs_params[name].job_name = name
        self.run.jobs_params[name].output_directory = enc(ana.OutputDirectory)
        self.run.jobs_params[name].device = enc(ana.Device)
        self.run.jobs_params[name].threads = enc(str(ana.Threads))
        return True

    def RegisterJob(self, str job_name, str mem, str time, list wait):
        cdef string name = enc(job_name)
        self.run.jobs_params[name].time = enc(time)
        self.run.jobs_params[name].memory = enc(mem)

        cdef str i
        self.run.sequence[name]
        for i in wait: self.run.sequence[name][enc(i)] = False

    def Make(self):
        cdef pair[string, map[string, bool]] itr
        cdef pair[string, bool] k
        cdef Job jb
        self.run.resolve = resolve(&self.run.sequence, b"")
        for itr in self.run.resolve:
            if not self.run.jobs_params.count(itr.first): return False
            jb = self.MakeJob(itr.first)
            jb.parents = {env(k.first) : self.MakeJob(k.first) for k in itr.second}
