#include <iostream>
#include <thread>
#include <vector>
#include <string>
#include <map>

#ifndef CYTYPES_H
#define CYTYPES_H

struct code_t
{
    std::vector<std::string> input_params = {}; 
    std::vector<std::string> co_vars = {}; 

    std::map<std::string, std::string> param_space = {}; 
    std::map<std::string, std::vector<std::string>> trace = {}; 
    std::map<std::string, std::vector<std::string>> extern_imports = {}; 
    std::vector<std::string> dependency_hashes = {}; 

    std::string function_name = "";
    std::string class_name = "";
    std::string hash = ""; 
    std::string source_code = ""; 
    std::string object_code = ""; 
    std::string defaults = ""; 
    
    bool is_class = false;
    bool is_function = false; 
    bool is_callable = false; 
    bool is_initialized = false; 
    bool has_param_variable = false; 
}; 

struct leaf_t
{
    std::string requested = "";
    std::string matched = "";
    std::string branch_name = "";
    std::string tree_name = "";
    std::string path = "";
};

struct branch_t
{
    std::string requested = "";
    std::string matched = "";
    std::string tree_name = "";
    std::vector<leaf_t> leaves = {};
};

struct tree_t
{
    unsigned int size = 0;
    std::string requested = "";
    std::string matched = "";
    std::vector<branch_t> branches = {};
    std::vector<leaf_t> leaves = {};
};

struct collect_t
{
    std::string tr_requested = "";
    std::string tr_matched = "";
    std::string br_requested = "";
    std::string br_matched = "";
    std::string lf_requested = "";
    std::string lf_matched = "";
    std::string lf_path = "";
    bool valid;
};

struct meta_t
{
    // basic IO content
    std::string hash = "";
    std::string original_input = "";
    std::string original_path = "";
    std::string original_name = "";

    // requested content of this root file
    std::vector<std::string> req_trees = {};
    std::vector<std::string> req_branches = {};
    std::vector<std::string> req_leaves = {};

    // Missing requested keys
    std::vector<std::string> mis_trees = {};
    std::vector<std::string> mis_branches = {};
    std::vector<std::string> mis_leaves = {};

    // Found content
    std::map<std::string, leaf_t> leaves = {};
    std::map<std::string, branch_t> branches = {}; 
    std::map<std::string, tree_t> trees = {}; 

    // AnalysisTracking values
    unsigned int dsid = 0;
    std::string AMITag = "";
    std::string generators = "";

    bool isMC = true;
    std::string derivationFormat = "";
    std::map<int, int> inputrange = {};
    std::map<int, std::string> inputfiles = {};
    std::map<std::string, std::string> config = {};

    // eventnumber is reserved for a ROOT specific mapping
    double eventNumber = -1;

    // event_index is used as a free parameter
    double event_index = -1;

    // search results
    bool found = false;
    std::string DatasetName = "";

    // dataset attributes
    double ecmEnergy = 0;
    double genFiltEff = 0;
    double completion = 0;
    double beam_energy = 0;
    double crossSection = 0;
    double crossSection_mean = 0;
    double totalSize = 0;

    unsigned int nFiles = 0;
    unsigned int run_number = 0;
    unsigned int totalEvents = 0;
    unsigned int datasetNumber = 0;

    std::string identifier = "";
    std::string prodsysStatus = "";
    std::string dataType = "";
    std::string version = "";
    std::string PDF = "";
    std::string AtlasRelease = "";
    std::string principalPhysicsGroup = "";
    std::string physicsShort = "";
    std::string generatorName = "";
    std::string geometryVersion = "";
    std::string conditionsTag = "";
    std::string generatorTune = "";
    std::string amiStatus = "";
    std::string beamType = "";
    std::string productionStep = "";
    std::string projectName = "";
    std::string statsAlgorithm = "";
    std::string genFilterNames = "";
    std::string file_type = "";
    std::string sample_name = ""; 
    std::string logicalDatasetName = ""; 

    std::vector<std::string> keywords = {};
    std::vector<std::string> weights = {};
    std::vector<std::string> keyword = {};

    // Local File Name
    std::map<std::string, int> LFN = {};
    std::vector<std::string> fileGUID = {};
    std::vector<int> events = {};
    std::vector<double> fileSize = {};
};

struct particle_t
{
    double e = -0.000000000000001; 
    double mass = -1;  

    double px = 0; 
    double py = 0; 
    double pz = 0; 

    double pt = 0; 
    double eta = 0; 
    double phi = 0; 

    bool cartesian = false; 
    bool polar = false; 

    double charge = 0; 
    int pdgid = 0; 
    int index = -1; 

    std::string type = ""; 
    std::string hash = "";
    std::string symbol = "";  
    std::vector<int> lepdef = {11, 13, 15};
    std::vector<int> nudef  = {12, 14, 16};         

    std::map<std::string, std::string> pickle_string = {}; 
}; 

struct event_t 
{
    // implementation information
    std::string commit_hash = "";
    std::string event_name = ""; 
    std::string code_hash = "";  
    bool deprecated = false; 

    // io state
    bool cached = false;
    
    // state variables
    double weight = 1; 
    double event_index = -1;
    std::string event_hash = ""; 
    std::string event_tagging = "";
    std::string event_tree = "";  
    std::string event_root = ""; 
    std::string pickled_data = "";  
    
    // template type indicators
    bool graph = false; 
    bool selection = false; 
    bool event = false;
};

struct graph_t
{
    // implementation information
    std::string event_name = ""; 
    std::string code_hash = "";
    std::string topo_hash = ""; 
    std::map<std::string, std::string> errors = {}; 

    // io state
    bool cached = false;
    
    // state variables
    double event_index = -1;
    double weight = 1; 
    std::string event_hash = ""; 
    std::string event_tagging = "";
    std::string event_tree = "";  
    std::string event_root = ""; 
    std::string pickled_data = "";  

    // Usage mode
    bool train      = false; 
    bool evaluation = false; 
    bool validation = false;  

    // Error / Skip properties
    bool empty_graph = false; 
    bool skip_graph  = false;
  
    // Topology properties 
    std::map<std::string, int> hash_particle = {}; 
    std::map<std::string, std::vector<int>> src_dst = {}; 
    bool self_loops = true; 

    // Pre-Selection metrics
    std::map<std::string, int> presel = {}; 
    
    // Feature properties
    // The key is the function name and the paired is the code hash
    std::map<std::string, std::string> graph_feature = {}; 
    std::map<std::string, std::string> node_feature = {}; 
    std::map<std::string, std::string> edge_feature = {}; 
    std::map<std::string, std::string> pre_sel_feature = {}; 

    // template type indicators
    bool graph     = false; 
    bool selection = false; 
    bool event     = false;
};

struct selection_t
{
    // implementation information
    std::string event_name = ""; 
    std::string code_hash = "";
    std::map<std::string, int> errors = {}; 

    bool cached = false; 
    double event_index = -1; 
    double weight = 1;
    std::string event_hash = ""; 
    std::string event_tagging = ""; 
    std::string event_tree = ""; 
    std::string event_root = ""; 
    std::string pickled_data = ""; 
    std::string pickled_strategy_data = "";
    std::map<std::string, std::string> data_merge = {};
    std::map<std::string, std::string> strat_merge = {}; 

    // Statistics content 
    std::map<std::string, int> cutflow = {}; 
    std::vector<double> timestats = {}; 
    std::vector<double> all_weights = {}; 
    std::vector<double> selection_weights = {}; 

    // user specific options
    bool allow_failure = false; 
    std::string _params_ = "";

    bool event = false; 
    bool graph = false; 
    bool selection = false; 
}; 


struct batch_t
{
    std::map<std::string, event_t> events = {}; 
    std::map<std::string, graph_t> graphs = {}; 
    std::map<std::string, selection_t> selections = {}; 
    std::map<std::string, code_t> code_hashes = {}; 

    meta_t meta; 
    std::string hash = ""; 
};

struct folds_t
{
    int kfold = -1; 
    bool test = false; 
    bool train = false; 
    bool evaluation = false;     
    std::string event_hash = "";
};

struct data_t
{
    std::vector<std::vector<float>> truth    = {};
    std::vector<std::vector<float>> pred     = {};
    std::vector<std::vector<float>> index    = {};

    std::vector<std::vector<float>> nodes    = {};
    std::vector<std::vector<float>> loss     = {}; 
    std::vector<std::vector<float>> accuracy = {};

    std::map<int, std::vector<std::vector<float>>> mass_truth = {};
    std::map<int, std::vector<std::vector<float>>> mass_pred  = {};
};

struct root_t
{
    std::map<std::string, batch_t> batches = {};
    std::map<std::string, int> n_events = {};
    std::map<std::string, int> n_graphs = {}; 
    std::map<std::string, int> n_selections = {}; 
};

struct tracer_t
{
    std::map<std::string, root_t> root_names = {}; 
    std::map<std::string, meta_t> root_meta = {}; 
    std::map<std::string, code_t> hashed_code = {}; 

    std::map<std::string, int> event_trees = {}; 
    std::map<std::string, std::string> link_event_code = {};
    std::map<std::string, std::string> link_graph_code = {};  
    std::map<std::string, std::string> link_selection_code = {}; 
};

struct export_t
{
    std::map<std::string, meta_t> root_meta = {}; 
    std::map<std::string, code_t> hashed_code = {}; 
    
    std::map<std::string, std::string> link_event_code = {};
    std::map<std::string, std::string> link_graph_code = {};  
    std::map<std::string, std::string> link_selection_code = {}; 

    std::map<std::string, std::vector<std::string>> event_name_hash = {}; 
    std::map<std::string, std::vector<std::string>> graph_name_hash = {}; 
    std::map<std::string, std::vector<std::string>> selection_name_hash = {};

    std::map<std::string, std::string> event_dir = {}; 
    std::map<std::string, std::string> graph_dir = {}; 
    std::map<std::string, std::string> selection_dir = {};
};

struct settings_t
{
    // General settings
    std::string projectname = "UNTITLED"; 
    std::string outputdirectory = "./";
    std::map<std::string, std::vector<std::string>> files = {}; 
    std::map<std::string, std::vector<std::string>> samplemap = {}; 
    int verbose = 3; 
   
    // Multithreading options 
    int chunks = 100; 
    unsigned int threads = 6;

    // PyAMI
    bool enable_pyami = true; 

    // Compiler settings
    std::string tree = ""; 
    std::string eventname = "";
    std::string graphname = ""; 
    std::string selectionname = ""; 

    // Generation Options
    int event_start = -1; 
    int event_stop = 0; 

    // Machine Learning 
    std::string device = "cpu";
    std::string training_name = "untitled";
    std::string run_name = "untitled"; 
    float training_size = -1;
    float max_gpu_memory = -1; 
    float max_ram_memory = -1; 

    std::string optimizer_name = ""; 
    std::map<std::string, std::string> optimizer_params = {}; 

    std::string scheduler_name = ""; 
    std::map<std::string, std::string> scheduler_params = {}; 

    int kfolds = -1; 
    int epochs = -1; 
    int batch_size = 1; 
    std::map<int, int> epoch = {}; 
    std::vector<int> kfold = {}; 

    code_t model; 
    std::map<std::string, std::string> model_params = {}; 

    bool debug_mode = false; 
    bool continue_training = false; 
    bool runplotting = false; 

    bool sort_by_nodes = false;
    bool enable_reconstruction = false; 
    std::map<std::string, std::string> kinematic_map = {};
    
    // Getter options
    bool getgraph = false; 
    bool getevent = false; 
    bool getselection = false; 

    // Cache options    
    bool eventcache = false; 
    bool graphcache = false; 

    // Search fields
    std::vector<std::string> search = {};
    bool get_all = false; 

    // code linking
    std::map<std::string, code_t> hashed_code = {}; 
    std::map<std::string, std::string> link_event_code = {}; 
    std::map<std::string, std::string> link_graph_code = {}; 
    std::map<std::string, std::string> link_selection_code = {}; 
};

#endif
