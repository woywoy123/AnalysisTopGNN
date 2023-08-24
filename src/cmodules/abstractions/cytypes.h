#include <iostream>
#include <thread>
#include <vector>
#include <string>
#include <map>

#ifndef CYTYPES_H
#define CYTYPES_H

struct code_t
{
    std::vector<std::string> input_params; 
    std::vector<std::string> co_vars; 

    std::map<std::string, std::string> param_space; 

    std::string function_name;
    std::string class_name;
    std::string hash; 
    std::string source_code; 
    std::string object_code; 
    
    bool is_class;
    bool is_function; 
    bool is_callable; 
    bool is_initialized; 
    bool has_param_variable; 
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
    std::string tr_requested;
    std::string tr_matched;
    std::string br_requested;
    std::string br_matched;
    std::string lf_requested;
    std::string lf_matched;
    std::string lf_path;
    bool valid;
};

struct meta_t
{
    // basic IO content
    std::string hash;
    std::string original_input;
    std::string original_path;
    std::string original_name;

    // requested content of this root file
    std::vector<std::string> req_trees;
    std::vector<std::string> req_branches;
    std::vector<std::string> req_leaves;

    // Missing requested keys
    std::vector<std::string> mis_trees;
    std::vector<std::string> mis_branches;
    std::vector<std::string> mis_leaves;

    // Found content
    std::map<std::string, leaf_t> leaves;
    std::map<std::string, branch_t> branches; 
    std::map<std::string, tree_t> trees; 

    // AnalysisTracking values
    unsigned int dsid;
    std::string AMITag;
    std::string generators;

    bool isMC;
    std::string derivationFormat;
    std::map<int, int> inputrange;
    std::map<int, std::string> inputfiles;
    std::map<std::string, std::string> config;

    // eventnumber is reserved for a ROOT specific mapping
    int eventNumber;

    // event_index is used as a free parameter
    int event_index;

    // search results
    bool found;
    std::string DatasetName;

    // dataset attributes
    double ecmEnergy;
    double genFiltEff;
    double completion;
    double beam_energy;
    double crossSection;
    double crossSection_mean;
    double totalSize;

    unsigned int nFiles;
    unsigned int run_number;
    unsigned int totalEvents;
    unsigned int datasetNumber;

    std::string identifier;
    std::string prodsysStatus;
    std::string dataType;
    std::string version;
    std::string PDF;
    std::string AtlasRelease;
    std::string principalPhysicsGroup;
    std::string physicsShort;
    std::string generatorName;
    std::string geometryVersion;
    std::string conditionsTag;
    std::string generatorTune;
    std::string amiStatus;
    std::string beamType;
    std::string productionStep;
    std::string projectName;
    std::string statsAlgorithm;
    std::string genFilterNames;
    std::string file_type;

    std::vector<std::string> keywords;
    std::vector<std::string> weights;
    std::vector<std::string> keyword;

    // Local File Name
    std::map<std::string, int> LFN;
    std::vector<std::string> fileGUID;
    std::vector<int> events;
    std::vector<double> fileSize;
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
    std::string event_name; 
    std::string commit_hash; 
    bool deprecated = false; 

    // io state
    bool cached = false;
    
    // state variables
    double weight; 
    int event_index = -1;
    std::string event_hash; 
    std::string event_tagging;
    std::string event_tree;  
    std::string event_root = ""; 
    std::map<std::string, std::string> pickled_data; 
    
    // template type indicators
    bool graph = false; 
    bool selection = false; 
    bool event = false;
};

struct event_T
{
    std::map<std::string, std::string> leaves; 
    std::map<std::string, std::string> branches; 
    std::map<std::string, std::string> trees; 
    event_t event; 
    meta_t meta; 
}; 

struct batch_t
{
    std::map<std::string, event_t> events; 
};

struct root_t
{
    meta_t meta; 
    std::map<std::string, batch_t> batches;
    std::map<std::string, int> n_events;
    std::map<std::string, int> n_graphs; 
    std::map<std::string, int> n_selections; 
};

struct tracer_t
{
    std::map<std::string, root_t> root_names; 
    std::map<std::string, meta_t> root_meta; 
    std::map<std::string, code_t> code; 
};







#endif
