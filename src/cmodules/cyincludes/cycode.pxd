from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool

from cytypes cimport code_t

cdef extern from "../code/code.h" namespace "Code":
    cdef cppclass CyCode:
        CyCode() except +

        void Hash() except +

        void ImportCode(code_t) except +
        void ImportCode(code_t, map[string, code_t]) except +

        code_t ExportCode() except +

        void AddDependency(map[string, code_t ]) except +
        void AddDependency(map[string, CyCode*]) except +
        bool operator==(CyCode& code) except +

        string hash
        code_t container
        map[string, CyCode*] dependency

