from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map, pair
from libcpp cimport bool

from cytypes cimport meta_t, selection_t, event_t
from cycode cimport CyCode


cdef extern from "../selection/selection.h" namespace "CyTemplate":
    cdef cppclass CySelectionTemplate nogil:
        CySelectionTemplate() except + nogil
        void ImportMetaData(meta_t meta) except + nogil
        selection_t Export() except + nogil
        void Import(selection_t selection) except + nogil

        string Hash() except + nogil
        void set_event_name(selection_t*, string) except + nogil

        void RegisterEvent(const event_t*) except + nogil

        bool CheckSelection(bool) except + nogil
        bool CheckSelection(string) except + nogil

        bool CheckStrategy(bool) except + nogil
        bool CheckStrategy(string) except + nogil

        void StartTime() except + nogil
        void EndTime() except + nogil

        double Mean() except + nogil
        double StandardDeviation() except + nogil
        double Luminosity() except + nogil

        bool operator == (CySelectionTemplate&) except + nogil
        CySelectionTemplate* operator + (CySelectionTemplate&) except + nogil
        void iadd(CySelectionTemplate* sel) except + nogil

        CyCode* code_link
        selection_t selection
        meta_t meta

        bool is_event
        bool is_graph
        bool is_selection

