#include <generators/analysis.h>

void analysis::build_events(){
    std::set<std::string> trees, branches, leaves; 
    event_template* event_f = nullptr; 

    std::map<std::string, std::string>::iterator itf = this -> file_labels.begin(); 
    for (; itf != this -> file_labels.end(); ++itf){
        if (!this -> event_labels.count(itf -> second)){continue;}
        if (this -> skip_event_build[itf -> first]){continue;}
        this -> reader -> root_files[itf -> first] = true;

        if (event_f){continue;}
        event_f = this -> event_labels[itf -> second]; 

        std::vector<std::string> _trees    = event_f -> trees; 
        std::vector<std::string> _branches = event_f -> branches; 
        std::vector<std::string> _leaves   = event_f -> leaves; 

        trees.insert(_trees.begin(), _trees.end()); 
        branches.insert(_branches.begin(), _branches.end()); 
        leaves.insert(_leaves.begin(), _leaves.end()); 
    } 
    if (!this -> reader -> root_files.size()){return this -> info("Skipping event building due to being in cache.");}
    if (!event_f){return this -> warning("Missing Event Implementation for specified samples!");}
    this -> success("+============================+"); 
    this -> success("|   Starting Event Builder   |");
    this -> success("+============================+"); 

    std::vector<std::string>* trees_    = &this -> reader -> trees; 
    std::vector<std::string>* branches_ = &this -> reader -> branches; 
    std::vector<std::string>* leaves_   = &this -> reader -> leaves; 

    trees_ -> insert(trees_ -> end(), trees.begin(), trees.end()); 
    branches_ -> insert(branches_ -> end(), branches.begin(), branches.end()); 
    leaves_ -> insert(leaves_ -> end(), leaves.begin(), leaves.end()); 
    this -> reader -> check_root_file_paths(); 

    long index = 0; 
    size_t nevents = 0;
    std::map<std::string, long> len = this -> reader -> root_size(); 
    std::map<std::string, long>::iterator ity = len.begin(); 
    for (; ity != len.end(); ++ity){nevents += ity -> second;}
    if (nevents == 0){return;}
    std::map<std::string, std::map<std::string, long>> root_entries = this -> reader -> tree_entries; 

    std::string title = ""; 
    std::vector<size_t> th_prg(1, 0); 
    std::thread* th_ = new std::thread(this -> progressbar2, &th_prg, &nevents, &title); 
    std::map<std::string, data_t*>* io_handle = this -> reader -> get_data(); 

    while (index < nevents){
        std::map<std::string, event_template*> evnts = event_f -> build_event(io_handle);
        if (!evnts.size()){continue;}
        th_prg[0]+=1; 
        ++index;  
        std::map<std::string, event_template*>::iterator tx = evnts.begin(); 
        event_template* ev_ = tx -> second; 

        std::string label = this -> file_labels[ev_ -> filename]; 
        meta* meta_ = this -> reader -> meta_data[ev_ -> filename]; 
        bool detach = this -> tracer -> add_meta_data(meta_, ev_ -> filename); 
        if (detach){
            this -> meta_data[ev_ -> filename] = meta_; 
            this -> reader -> meta_data[ev_ -> filename] = nullptr;
        }

        std::vector<std::string> tmp = this -> split(ev_ -> filename, "/"); 
        title = tmp[tmp.size()-1]; 
        for (; tx != evnts.end(); ++tx){
            long lx = root_entries[ev_ -> filename][tx -> first]; 
            if (!this -> tracer -> add_event(tx -> second, label, &lx)){continue;} 
            delete tx -> second; 
        }
    }
    th_ -> join(); 
    delete th_; 

    this -> reader -> root_end(); 
    delete this -> reader; 
    this -> reader = new io(); 
    std::cout << std::endl;
    this -> success("Finished Building Events"); 
}
