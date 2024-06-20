#include <container/container.h>


void entry_t::init(){
    this -> m_event = new std::vector<event_template*>(); 
    this -> m_graph = new std::vector<graph_template*>(); 
    this -> m_data  = new std::vector<graph_t*>(); 
}

void entry_t::destroy(){
    this -> destroy(this -> m_event); 
    this -> destroy(this -> m_graph); 
    this -> destroy(this -> m_data); 

    delete this -> m_event; 
    delete this -> m_graph; 
    delete this -> hash; 
}

bool entry_t::has_event(event_template* ev){
    std::string tr   = ev -> tree;
    std::string name = ev -> name; 
     
    for (size_t x(0); x < this -> m_event -> size(); ++x){
        std::string tr_ = this -> m_event -> at(x) -> tree; 
        std::string name_ = this -> m_event -> at(x) -> name; 
        if (tr_ == tr && name_  == name){return true;}
    }
    this -> m_event -> push_back(ev); 
    return false; 
}

bool entry_t::has_graph(graph_template* gr){
    std::string tr   = gr -> tree;
    std::string name = gr -> name; 
     
    for (size_t x(0); x < this -> m_graph -> size(); ++x){
        std::string tr_ = this -> m_graph -> at(x) -> tree; 
        std::string name_ = this -> m_graph -> at(x) -> name; 
        if (tr_ == tr && name_  == name){return true;}
    }
    this -> m_graph -> push_back(gr); 
    return false; 
}

