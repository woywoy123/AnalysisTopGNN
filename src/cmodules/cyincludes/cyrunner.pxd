from cytypes cimport settings_t

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool

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
    map[string, settings_t] analysis_params
    map[string, job_t] jobs_params

cdef class Runner:

    cdef public str OutputDirectory
    cdef public str ProjectName
    cdef public str EventName
    cdef public str GraphName
    cdef public str PythonVenv
    cdef public str CondaVenv
    cdef public int Verbose
    cdef public bool EnablePyAmi
    cdef runner_t run
