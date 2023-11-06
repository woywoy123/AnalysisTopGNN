#include "../root/root.h"

namespace SampleTracer
{

    CyBatch::CyBatch(std::string hash){this -> hash = hash;}
    CyBatch::~CyBatch()
    {
        this -> destroy(&(this -> events)); 
        this -> destroy(&(this -> graphs)); 
        this -> destroy(&(this -> selections)); 
        if (!this -> code_hashes.size()){return;}
        std::map<std::string, Code::CyCode*>::iterator it; 
        it = this -> code_hashes.begin(); 
        for (; it != this -> code_hashes.end(); ++it){delete it -> second;}
    }
    
    std::string CyBatch::Hash(){ return this -> hash; }
    void CyBatch::Import(const event_t* event)
    { 
        std::string name = ""; 
        name += event -> event_tree + "/"; 
        name += event -> event_name; 

        if (this -> events.count(name)){ delete this -> events[name]; }
        CyEventTemplate* _event = new CyEventTemplate(); 
        _event -> Import(*event); 
        this -> events[name] = _event; 
        this -> this_ev = _event; 
    }

    void CyBatch::Import(const graph_t* graph)
    {
        std::string name = ""; 
        name += graph -> event_tree + "/"; 
        name += graph -> event_name; 
     
        if (this -> graphs.count(name)){ delete this -> graphs[name]; }
        CyGraphTemplate* _graph = new CyGraphTemplate(); 
        _graph -> Import(*graph); 
        this -> graphs[name] = _graph; 
        this -> this_gr = _graph; 
    }


    void CyBatch::Import(const selection_t* selection)
    {
        std::string name = ""; 
        name += selection -> event_tree + "/"; 
        name += selection -> event_name; 
        
        if (this -> selections.count(name)){ delete this -> selections[name]; }
        CySelectionTemplate* _selection = new CySelectionTemplate(); 
        _selection -> Import(*selection); 
        this -> selections[name] = _selection; 
        this -> this_sel = _selection; 
    }

    void CyBatch::Import(const meta_t* meta)
    {
        if (this -> lock_meta){ return; }
        this -> meta = meta; 
        this -> lock_meta = true;
    }

    void CyBatch::Import(const batch_t* bth)
    {
        std::map<std::string, event_t>::const_iterator ite;
        std::map<std::string, graph_t>::const_iterator itg;
        std::map<std::string, selection_t>::const_iterator its;
        ite = bth -> events.begin();
        itg = bth -> graphs.begin();
        its = bth -> selections.begin();
        
        for (; ite != bth -> events.end(); ++ite){this -> Import(&ite -> second);}
        for (; itg != bth -> graphs.end(); ++itg){this -> Import(&itg -> second);}
        for (; its != bth -> selections.end(); ++its){this -> Import(&its -> second);}
        this -> hash = bth -> hash;
    }

    batch_t CyBatch::ExportPickled()
    {
        batch_t batch = this -> Export(); 
        this -> export_code(this -> events, &batch.code_hashes); 
        this -> export_code(this -> graphs, &batch.code_hashes); 
        this -> export_code(this -> selections, &batch.code_hashes); 
        return batch; 
    }

    void CyBatch::ImportPickled(const batch_t* inpt)
    {
        this -> Import(inpt);  
        const std::map<std::string, code_t>* code = &(inpt -> code_hashes);
        std::map<std::string, code_t>::const_iterator it; 
        std::map<std::string, Code::CyCode*> code_hashes = {}; 
        it = code -> begin();
        for (; it != code -> end(); ++it){
            code_hashes[it -> first] = new Code::CyCode();
            code_hashes[it -> first] -> ImportCode(it -> second, *code); 
        }
        this -> ApplyCodeHash(&code_hashes); 
        this -> code_hashes = code_hashes; 
    }

    batch_t CyBatch::Export()
    {
        batch_t output; 
        output.hash = this -> hash;
        if (this -> this_ev){ this -> export_this(this -> this_ev, &(output.events));}
        else {this -> export_this(this -> events, &(output.events));}

        if (this -> this_gr){this -> export_this(this -> this_gr, &(output.graphs));}
        else {this -> export_this(this -> graphs, &(output.graphs));}

        if (this -> this_sel){this -> export_this(this -> this_sel, &(output.selections));}
        else {this -> export_this(this -> selections, &(output.selections));}
        return output; 
    }

    void CyBatch::Export(batch_t* exp)
    {
        exp -> hash = this -> hash;
        this -> export_this(this -> events, &(exp -> events));  
        this -> export_this(this -> graphs, &(exp -> graphs));  
        this -> export_this(this -> selections, &(exp -> selections));
    }

    void CyBatch::Contextualize()
    {
        // Find the event implementations if specified
        std::string ev_name = ""; 
        if (this -> this_tree.size() && this -> this_event_name.size()){
            ev_name  = this -> this_tree + "/" + this -> this_event_name;
        }
        else if (this -> this_event_name.size()){ev_name = this -> this_event_name;}

        if (this -> events.count(ev_name)){this -> this_ev = this -> events[ev_name];}
        else { this -> this_ev = this -> find(&this -> events, ev_name); }

        // Find the graph implementations if specified
        std::string gr_name = ""; 
        if (this -> this_tree.size() && this -> this_graph_name.size()){
            gr_name  = this -> this_tree + "/" + this -> this_graph_name;
        }
        else if (this -> this_graph_name.size()){gr_name = this -> this_graph_name;}

        if (this -> graphs.count(gr_name)){this -> this_gr = this -> graphs[gr_name];}
        else { this -> this_gr = this -> find(&this -> graphs, gr_name); }

        // Find the selection implementations if specified
        std::string sel_name = ""; 
        if (this -> this_tree.size() && this -> this_selection_name.size()){
            sel_name  = this -> this_tree + "/" + this -> this_selection_name;
        }
        else if (this -> this_selection_name.size()){sel_name = this -> this_selection_name;}

        if (this -> selections.count(sel_name)){this -> this_sel = this -> selections[sel_name];}
        else { this -> this_sel = this -> find(&this -> selections, sel_name); }

        if (!this -> get_event){this -> this_ev  = nullptr;}
        if (!this -> get_graph){this -> this_gr  = nullptr;}
        if (!this -> get_selection){this -> this_sel = nullptr;}

        if (this -> this_ev) { this -> valid = true; }
        else if (this -> this_gr) { this -> valid = true; }
        else if (this -> this_sel){ this -> valid = true; }
        else if (this -> find(&this -> event_dir, this -> this_tree + "." + this -> this_event_name)){ this -> valid = true; }
        else if (this -> find(&this -> graph_dir, this -> this_tree + "." + this -> this_graph_name)){ this -> valid = true; }
        else if (this -> find(&this -> selection_dir, this -> this_tree + "." + this -> this_selection_name)){ this -> valid = true; }
    }
    
    void CyBatch::ApplySettings(const settings_t* inpt)
    {
        this -> this_tree = inpt -> tree; 

        this -> this_event_name = inpt -> eventname; 
        this -> get_event = inpt -> getevent; 

        this -> this_graph_name = inpt -> graphname; 
        this -> get_graph = inpt -> getgraph; 

        this -> this_selection_name = inpt -> selectionname; 
        this -> get_selection = inpt -> getselection; 

        this -> valid = false;  
        this -> Contextualize();
        if (!this -> valid && !inpt -> get_all){ return; }

        const std::vector<std::string>* srch = &(inpt -> search); 
        unsigned int z = srch -> size(); 
        if (!z){ return; }
        
        std::string find; 
        std::vector<std::string> tags; 
        tags = Tools::split(this -> meta -> sample_name, "|"); 
        for (unsigned int x(0); x < z; ++x){
            find = srch -> at(x); 
            if (find == this -> hash){return;}
            for (std::string key : tags){if (key == find){return;}}  
            if (this -> meta -> original_input == find){ return; }
            if (this -> meta -> DatasetName == find){ return; }

            if (this -> this_ev){
                if (this -> this_ev -> event.event_root == find){return;}
                if (this -> this_ev -> event.event_name == find){return;}
            }

            if (this -> this_gr){
                if (this -> this_gr -> graph.event_root == find){return;}
                if (this -> this_gr -> graph.event_name == find){return;}
            }

            if (this -> this_sel){
                if (this -> this_sel -> selection.event_root == find){return;}
                if (this -> this_sel -> selection.event_name == find){return;}
            }
        }

        this -> valid = false; 
    }

    void CyBatch::LinkCode(
                    std::map<std::string, std::string>* inpt,
                    std::map<std::string, Code::CyCode*>* link,
                    const std::map<std::string, Code::CyCode*>* code_h)
    {
        std::map<std::string, std::string>::iterator it; 
        it = inpt -> begin(); 
        for (; it != inpt -> end(); ++it){
            if (!code_h -> count(it -> second)){continue;}
            Code::CyCode* co = code_h -> at(it -> second); 
            (*link)[it -> first] = co;
        }
    }

    void CyBatch::ApplyCodeHash(const std::map<std::string, Code::CyCode*>* code_hash)
    {

        this -> code_link(this -> events, code_hash); 
        this -> code_link(this -> graphs, code_hash); 
        this -> code_link(this -> selections, code_hash); 
        
        std::map<std::string, CyGraphTemplate*>::iterator itg; 
        itg = this -> graphs.begin(); 
        for (; itg != this -> graphs.end(); ++itg){
            CyGraphTemplate* gr_ = itg -> second;
            graph_t* gr = &(gr_ -> graph); 
            if (code_hash -> count(gr -> topo_hash)){
                gr_ -> topo_link = code_hash -> at(gr -> topo_hash);
                continue;
            }
            LinkCode(&(gr -> edge_feature), &(gr_ -> edge_fx), code_hash); 
            LinkCode(&(gr -> node_feature), &(gr_ -> node_fx), code_hash); 
            LinkCode(&(gr -> graph_feature), &(gr_ -> graph_fx), code_hash); 
            LinkCode(&(gr -> pre_sel_feature), &(gr_ -> pre_sel_fx), code_hash); 
        }
        this -> not_code_owner(&this -> graphs); 
    }

    CyROOT::CyROOT(meta_t meta){this -> meta = meta;}

    CyROOT::~CyROOT()
    {
        std::map<std::string, CyBatch*>::iterator it; 
        it = this -> batches.begin(); 
        for (; it != this -> batches.end(); ++it){delete it -> second;}
    }

    void CyROOT::AddEvent(const event_t* event)
    {
        std::map<std::string, event_t> inpt = {}; 
        inpt[event -> event_hash] = *event;  
        this -> ImportBatch(&inpt, &(this -> batches), &(this -> meta)); 
    }

    void CyROOT::AddGraph(const graph_t* graph)
    {
        std::map<std::string, graph_t> inpt = {}; 
        inpt[graph -> event_hash] = *graph;  
        this -> ImportBatch(&inpt, &(this -> batches), &(this -> meta)); 
    }

    void CyROOT::AddSelection(const selection_t* selection)
    {
        std::map<std::string, selection_t> inpt = {}; 
        inpt[selection -> event_hash] = *selection;
        this -> ImportBatch(&inpt, &(this -> batches), &(this -> meta)); 
    }

    void CyROOT::UpdateSampleStats()
    {
        this -> total_hashes = this -> batches.size();
        this -> n_events.clear(); 
        this -> n_graphs.clear(); 
        this -> n_selections.clear(); 
        this -> event_trees.clear(); 

        std::map<std::string, std::string> tree_map; 
        std::map<std::string, CyEventTemplate*>::iterator ite; 
        std::map<std::string, CyGraphTemplate*>::iterator itg; 
        std::map<std::string, CySelectionTemplate*>::iterator its; 

        std::map<std::string, CyBatch*>::iterator bt = this -> batches.begin(); 
        for (; bt != this -> batches.end(); ++bt){
            CyBatch* this_b = bt -> second; 
            ite = this_b -> events.begin();
            itg = this_b -> graphs.begin();
            its = this_b -> selections.begin();

            for (; ite != this_b -> events.end(); ++ite){
                this -> n_events[ite -> first] += 1;
                tree_map[ite -> first] = ite -> second -> event.event_tree;
            }
            for (; itg != this_b -> graphs.end(); ++itg){
                this -> n_graphs[itg -> first] += 1;
                tree_map[itg -> first] = itg -> second -> graph.event_tree;
            }
            for (; its != this_b -> selections.end(); ++its){
                this -> n_selections[its -> first] += 1;
                tree_map[its -> first] = its -> second -> selection.event_tree;
            }
        }
        std::map<std::string, std::string>::iterator its_; 
        its_ = tree_map.begin(); 
        for (; its_ != tree_map.end(); ++its_){this -> event_trees[its_ -> second] += 1;}
    }

    void CyROOT::ReleaseObjects(std::map<std::string, std::vector<CyEventTemplate*>>* out)
    {
        std::map<std::string, std::vector<CyEventTemplate*>> get = {}; 
        this -> ReleaseData(&get); 
        std::map<std::string, std::vector<CyEventTemplate*>>::iterator ite = get.begin(); 
        for (; ite != get.end(); ++ite){
            std::vector<CyEventTemplate*> t = ite -> second;
            (*out)[ite -> first].insert((*out)[ite -> first].end(), t.begin(), t.end()); 
        }
    }

    void CyROOT::ReleaseObjects(std::map<std::string, std::vector<CyGraphTemplate*>>* out)
    {
        std::map<std::string, std::vector<CyGraphTemplate*>> get = {}; 
        this -> ReleaseData(&get); 
        std::map<std::string, std::vector<CyGraphTemplate*>>::iterator ite = get.begin(); 
        for (; ite != get.end(); ++ite){
            std::vector<CyGraphTemplate*> t = ite -> second;
            (*out)[ite -> first].insert((*out)[ite -> first].end(), t.begin(), t.end()); 
        }
    }
 
    void CyROOT::ReleaseObjects(std::map<std::string, std::vector<CySelectionTemplate*>>* out)
    {
        std::map<std::string, std::vector<CySelectionTemplate*>> get = {}; 
        this -> ReleaseData(&get); 
        std::map<std::string, std::vector<CySelectionTemplate*>>::iterator ite = get.begin(); 
        for (; ite != get.end(); ++ite){
            std::vector<CySelectionTemplate*> t = ite -> second;
            (*out)[ite -> first].insert((*out)[ite -> first].end(), t.begin(), t.end()); 
        }
    }
    
    root_t CyROOT::Export()
    {
        root_t output; 
        output.n_events = this -> n_events; 
        output.n_graphs = this -> n_graphs; 
        output.n_selections = this -> n_selections;

        std::map<std::string, CyBatch*>::iterator it;
        it = this -> batches.begin();

        for (; it != this -> batches.end(); ++it){
            CyBatch* exp = it -> second; 
            output.batches[exp -> hash] = batch_t();
            exp -> Export(&output.batches[exp -> hash]);
        }
        return output; 
    }

    void CyROOT::Import(const root_t* inpt)
    {
        std::map<std::string, event_t>::const_iterator itr; 
        std::map<std::string, batch_t>::const_iterator itb; 
        itb = inpt -> batches.begin();  
        for (; itb != inpt -> batches.end(); ++itb)
        {
            const batch_t* b = &(itb -> second); 
            std::string hash = b -> hash; 
            this -> ImportBatch(&(b -> events), &(this -> batches), &(this -> meta)); 
            this -> ImportBatch(&(b -> graphs), &(this -> batches), &(this -> meta)); 
            this -> ImportBatch(&(b -> selections), &(this -> batches), &(this -> meta)); 
        }
    }
}
