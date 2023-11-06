from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.map cimport map
from libcpp cimport bool

from cyevent cimport CyEventTemplate
from cygraph cimport CyGraphTemplate
from cyselection cimport CySelectionTemplate

from cytypes cimport meta_t, event_t, graph_t, selection_t
from cytypes cimport settings_t, tracer_t, batch_t, code_t, export_t
from cycode cimport CyCode


cdef extern from "../root/root.h" namespace "SampleTracer" nogil:
    cdef cppclass CyBatch nogil:
        CyBatch(string) except + nogil
        string Hash() except + nogil

        batch_t ExportPickled() except + nogil
        void ImportPickled(const batch_t*) except + nogil

        batch_t Export() except + nogil
        void Import(const meta_t*) except + nogil
        void Import(const event_t*) except + nogil
        void Import(const graph_t*) except + nogil
        void Import(const selection_t*) except + nogil
        void Import(const batch_t*) except + nogil

        void Contextualize() except + nogil
        void ApplyCodeHash(const map[string, CyCode*]*) except + nogil

        map[string, CyEventTemplate*] events
        map[string, CyGraphTemplate*] graphs
        map[string, CySelectionTemplate*] selections

        const meta_t* meta

        bool get_event
        bool get_graph
        bool get_selection
        bool valid

        CyEventTemplate* this_ev
        CyGraphTemplate* this_gr
        CySelectionTemplate* this_sel

        map[string, CyCode*] code_hashes
        map[string, string] event_dir
        map[string, string] graph_dir
        map[string, string] selection_dir

        string hash
        bool lock_meta


cdef extern from "../sampletracer/sampletracer.h":
    struct HDF5_t:
        string root_name
        map[string, string] cache_path

cdef extern from "../sampletracer/sampletracer.h" namespace "SampleTracer":

    cdef cppclass CySampleTracer:
        CySampleTracer() except +
        void AddMeta(meta_t, string) except +
        void AddEvent(event_t, meta_t) except +
        void AddGraph(graph_t, meta_t) except +
        void AddSelection(selection_t, meta_t) except +
        void AddCode(code_t code) except +

        map[string, string] RestoreTracer(map[string, HDF5_t]* hdf5, string event_root) except +
        map[string, vector[CyBatch*]] RestoreCache(string type) except +

        map[string, vector[CyEventTemplate*]] DumpEvents() except +
        map[string, vector[CyGraphTemplate*]] DumpGraphs() except +
        map[string, vector[CySelectionTemplate*]] DumpSelections() except +

        void FlushEvents(vector[string]) except +
        void FlushGraphs(vector[string]) except +
        void FlushSelections(vector[string]) except +

        void DumpTracer() except +

        tracer_t Export() except +
        void Import(tracer_t) except +

        settings_t ExportSettings() except +
        void ImportSettings(settings_t) except +

        vector[CyBatch*] MakeIterable() except +
        map[string, int] length() except +

        CySampleTracer* operator+(CySampleTracer*) except +
        void iadd(CySampleTracer*) except +

        settings_t settings
        export_t state
        map[string, CyCode*] code_hashes
        map[string, int] event_trees

        map[string, string] link_event_code
        map[string, string] link_graph_code
        map[string, string] link_selection_code
        string caller

