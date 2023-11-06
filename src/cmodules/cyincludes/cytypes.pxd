from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool

cdef extern from "../abstractions/cytypes.h":
    struct code_t:
        vector[string] input_params
        vector[string] co_vars

        map[string, string] param_space
        map[string, vector[string]] trace
        map[string, vector[string]] extern_imports
        vector[string] dependency_hashes

        string function_name
        string class_name
        string source_code
        string object_code
        string defaults
        string hash

        bool is_class
        bool is_function
        bool is_callable
        bool is_initialized
        bool has_param_variable

    struct leaf_t:
        string requested
        string matched
        string branch_name
        string tree_name
        string path

    struct branch_t:
        string requested
        string matched
        string tree_name
        vector[leaf_t] leaves

    struct tree_t:
        unsigned int size
        string requested
        string matched

        vector[branch_t] branches
        vector[leaf_t] leaves

    struct meta_t:
        string hash
        string original_input
        string original_path
        string original_name

        vector[string] req_trees
        vector[string] req_branches
        vector[string] req_leaves

        vector[string] mis_trees
        vector[string] mis_branches
        vector[string] mis_leaves

        unsigned int dsid
        string AMITag
        string generators

        bool isMC
        string derivationFormat
        map[int, int] inputrange
        map[int, string] inputfiles
        map[string, string] config

        double eventNumber
        double event_index

        bool found
        string DatasetName

        double ecmEnergy
        double genFiltEff
        double completion
        double beam_energy
        double crossSection
        double crossSection_mean
        double totalSize

        unsigned int nFiles
        unsigned int run_number
        unsigned int totalEvents
        unsigned int datasetNumber

        string identifier
        string prodsysStatus
        string dataType
        string version
        string PDF
        string AtlasRelease
        string principalPhysicsGroup
        string physicsShort
        string generatorName
        string geometryVersion
        string conditionsTag
        string generatorTune
        string amiStatus
        string beamType
        string productionStep
        string projectName
        string statsAlgorithm
        string genFilterNames
        string file_type
        string sample_name
        string logicalDatasetName

        vector[string] keywords
        vector[string] weights
        vector[string] keyword

        map[string, int] LFN
        vector[string] fileGUID
        vector[int] events
        vector[double] fileSize


    struct particle_t:

        double e
        double mass

        double px
        double py
        double pz

        double pt
        double eta
        double phi

        bool cartesian
        bool polar

        double charge
        int pdgid
        int index

        string type
        string hash
        string symbol
        vector[int] lepdef
        vector[int] nudef

    struct event_t:

        string event_name
        string commit_hash
        string code_hash
        bool deprecated

        bool cached

        double weight
        double event_index
        string event_hash
        string event_tagging
        string event_tree
        string event_root
        string pickled_data

        bool graph
        bool selection
        bool event

    struct graph_t:

        string event_name
        string code_hash
        map[string, string] errors
        map[string, int] presel

        bool cached
        double event_index
        double weight
        string event_hash
        string event_tagging
        string event_tree
        string event_root
        string pickled_data

        bool train
        bool evaluation
        bool validation

        bool empty_graph
        bool skip_graph

        map[string, vector[int]] src_dst
        map[string, int] hash_particle
        bool self_loops

        map[string, string] graph_feature
        map[string, string] node_feature
        map[string, string] edge_feature
        map[string, string] pre_sel_feature
        string topo_hash

        bool graph
        bool selection
        bool event

    struct selection_t:
        string event_name
        string code_hash
        map[string, int] errors

        bool cached
        double event_index
        double weight
        string event_hash
        string event_tagging
        string event_tree
        string event_root
        string pickled_data
        string pickled_strategy_data

        map[string, string] strat_merge
        map[string, string] data_merge

        map[string, int] cutflow
        vector[double] timestats
        vector[double] all_weights
        vector[double] selection_weights

        bool allow_failure
        string _params_

        bool graph
        bool selection
        bool event

    struct batch_t:
        map[string, event_t] events
        map[string, graph_t] graphs
        map[string, selection_t] selections
        map[string, code_t] code_hashes

        meta_t meta
        string hash

    struct folds_t:
        bool test
        bool train
        bool evaluation
        int kfold
        string event_hash

    struct data_t:
        vector[vector[float]] truth
        vector[vector[float]] pred
        vector[vector[float]] index

        vector[vector[float]] nodes
        vector[vector[float]] loss
        vector[vector[float]] accuracy

        map[int, vector[vector[float]]] mass_truth
        map[int, vector[vector[float]]] mass_pred

    struct root_t:
        map[string, batch_t] batches
        map[string, int] n_events
        map[string, int] n_graphs
        map[string, int] n_selections

    struct tracer_t:
        map[string, root_t] root_names
        map[string, meta_t] root_meta
        map[string, code_t] hashed_code

        map[string, int] event_trees
        map[string, string] link_event_code
        map[string, string] link_graph_code


    struct export_t:
        map[string, meta_t] root_meta
        map[string, code_t] hashed_code

        map[string, string] link_event_code
        map[string, string] link_graph_code
        map[string, string] link_selection_code

        map[string, vector[string]] event_name_hash
        map[string, vector[string]] graph_name_hash
        map[string, vector[string]] selection_name_hash

        map[string, string] event_dir
        map[string, string] graph_dir
        map[string, string] selection_dir


    struct settings_t:
        # General IO stuff
        string projectname
        string outputdirectory
        map[string, vector[string]] files
        map[string, vector[string]] samplemap
        int verbose

        # multithreading options
        int chunks
        unsigned int threads

        # PyAMI
        bool enable_pyami

        # Sample/Compiler stuff
        string tree
        string eventname
        string graphname
        string selectionname

        # Generation specific options
        int event_start
        int event_stop

        # Machine learning 
        string device
        string training_name
        string run_name
        float training_size
        vector[int] kfold
        float max_gpu_memory
        float max_ram_memory

        string optimizer_name
        map[string, string] optimizer_params

        string scheduler_name
        map[string, string] scheduler_params

        int kfolds
        int batch_size
        int epochs
        map[int, int] epoch
        vector[int] kfold

        code_t model

        map[string, string] model_params
        map[string, string] kinematic_map

        bool debug_mode
        bool continue_training
        bool runplotting
        bool sort_by_nodes
        bool enable_reconstruction

        # Getter object option
        bool getgraph
        bool getevent
        bool getselection

        # Cache options
        bool eventcache
        bool graphcache

        # Getter variable
        vector[string] search
        bool get_all

        # Code linking
        map[string, code_t] hashed_code
        map[string, string] link_event_code
        map[string, string] link_graph_code
        map[string, string] link_selection_code
