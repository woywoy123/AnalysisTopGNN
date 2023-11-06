from cytypes cimport meta_t, event_t
from cycode cimport CyCode

from libcpp.string cimport string
from libcpp.map cimport map
from libcpp cimport bool

cdef extern from "../event/event.h" namespace "CyTemplate":
    cdef cppclass CyEventTemplate:
        CyEventTemplate() except + nogil

        void ImportMetaData(meta_t meta) except + nogil
        void Import(event_t event) except + nogil
        event_t Export() except + nogil

        string Hash() except + nogil
        void addleaf(string key, string leaf) except + nogil
        void addbranch(string key, string branch) except + nogil
        void addtree(string key, string tree) except + nogil

        void set_event_name(event_t*, string) except + nogil

        bool operator == (CyEventTemplate& ev) except + nogil

        map[string, string] leaves
        map[string, string] branches
        map[string, string] trees

        CyCode* code_link

        event_t event
        meta_t meta

        bool is_event
        bool is_graph
        bool is_selection



