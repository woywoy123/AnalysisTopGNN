#include "../graph/graph.h"

namespace CyTemplate
{
    CyGraphTemplate::CyGraphTemplate(){}
    CyGraphTemplate::~CyGraphTemplate()
    {
        if (!this -> code_owner){return;}
        this -> destroy(&(this -> edge_fx)); 
        this -> destroy(&(this -> node_fx)); 
        this -> destroy(&(this -> graph_fx)); 
        this -> destroy(&(this -> pre_sel_fx)); 
        if (this -> topo_link){ delete this -> topo_link; }
        if (this -> code_link){ delete this -> code_link; }
    }

    bool CyGraphTemplate::operator == (CyGraphTemplate& gr)
    {
        graph_t* gr1 = &(this -> graph); 
        graph_t* gr2 = &(gr.graph); 
        return this -> is_same(gr1, gr2);  
    }

    void CyGraphTemplate::Import(graph_t gr)
    {
        this -> graph = gr; 
        this -> graph.graph = true; 
        this -> is_graph = true;
    }

    void CyGraphTemplate::DeLinkFeatures(
            std::map<std::string, std::string>* fx, 
            std::map<std::string, Code::CyCode*> code_h)
    {
        std::map<std::string, Code::CyCode*>::iterator it; 
        it = code_h.begin(); 
        for (; it != code_h.end(); ++it){
            it -> second -> Hash(); 
            (*fx)[it -> first] = it -> second -> hash; 
        }
        if (!this -> code_link){return;}
        this -> code_link -> AddDependency(code_h); 
    }

    graph_t CyGraphTemplate::Export()
    {
        graph_t gr = this -> graph; 
        this -> DeLinkFeatures(&gr.edge_feature, this -> edge_fx); 
        this -> DeLinkFeatures(&gr.node_feature, this -> node_fx); 
        this -> DeLinkFeatures(&gr.graph_feature, this -> graph_fx); 
        this -> DeLinkFeatures(&gr.pre_sel_feature, this -> pre_sel_fx);
        if (this -> topo_link){
            this -> topo_link -> Hash(); 
            gr.topo_hash = this -> topo_link -> hash;
        }
        if (this -> code_link){
            this -> code_link -> Hash(); 
            gr.code_hash = this -> code_link -> hash;
        }
        gr.graph = true; 
        return gr; 
    }

    std::string CyGraphTemplate::Hash()
    {
        return this -> CyEvent::Hash(&(this -> graph)); 
    }


    void CyGraphTemplate::AddParticle(std::string hash, int p_index)
    {
        this -> graph.hash_particle[hash] = p_index; 
    }

    void CyGraphTemplate::RegisterEvent(const event_t* evnt)
    {
        graph_t* gr = &(this -> graph); 
        this -> set_event_hash(gr, evnt); 
        this -> set_event_tag(gr, evnt); 
        this -> set_event_tree(gr, evnt); 
        this -> set_event_root(gr, evnt); 
        this -> set_event_index(gr, evnt); 
        this -> set_event_weight(gr, evnt); 
    }

    void CyGraphTemplate::FullyConnected()
    {
        std::map<std::string, int>::iterator src; 
        std::map<std::string, int>::iterator dst; 
        std::map<std::string, int>* particles = &(this -> graph.hash_particle); 
        std::map<std::string, std::vector<int>>* topo = &(this -> graph.src_dst); 
        topo -> clear();
        bool self = this -> graph.self_loops; 

        src = particles -> begin(); 
        for (; src != particles -> end(); ++src){
            dst = particles -> begin(); 
            for (; dst != particles -> end(); ++dst){
                int src_ = src -> second; 
                int dst_ = dst -> second; 
                if (src_ == dst_ && !self){continue;}
                (*topo)[src -> first].push_back(dst_); 
            }
        }
    }

    std::string CyGraphTemplate::IndexToHash(int p_index)
    {
        std::string hash = this -> index_to_particle_hash[p_index]; 
        if (hash.size()){ return hash; } 
        std::map<std::string, int>* p_hashes = &(this -> graph.hash_particle); 
        std::map<std::string, int>::iterator it; 
        it = p_hashes -> begin(); 
        for (; it != p_hashes -> end(); ++it){
            if (p_index != it -> second){continue;}
            this -> index_to_particle_hash[p_index] = it -> first; 
            return it -> first; 
        }
        return hash;
    }
}

