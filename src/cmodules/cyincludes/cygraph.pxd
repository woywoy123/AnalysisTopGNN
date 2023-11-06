from libcpp.string cimport string
from libcpp.map cimport map
from libcpp cimport bool

from cycode cimport CyCode

from cytypes cimport meta_t, graph_t, event_t
from cytypes cimport code_t

cdef extern from "../graph/graph.h" namespace "CyTemplate":
    cdef cppclass CyGraphTemplate nogil:
        CyGraphTemplate() except +
        bool operator == (CyGraphTemplate& gr) except +

        void ImportMetaData(meta_t meta) except +
        void set_event_name(graph_t*, string) except +
        string Hash() except +

        void Import(graph_t graph) except +
        graph_t Export() except +

        void RegisterEvent(const event_t*) except +
        void AddParticle(string, int) except +
        void FullyConnected() except +
        string IndexToHash(int) except +

        graph_t graph
        meta_t meta

        bool code_owner
        map[string, CyCode*] edge_fx
        map[string, CyCode*] node_fx
        map[string, CyCode*] graph_fx
        map[string, CyCode*] pre_sel_fx

        CyCode* topo_link
        CyCode* code_link

        bool is_event
        bool is_graph
        bool is_selection



