#include "../event/event.h"

namespace CyTemplate
{
    CyEventTemplate::CyEventTemplate(){}
    CyEventTemplate::~CyEventTemplate(){}
        
    void CyEventTemplate::addleaf(std::string key, std::string leaf)
    {
        this -> leaves[key] = leaf; 
    }

    void CyEventTemplate::addbranch(std::string key, std::string branch)
    {
        this -> branches[key] = branch; 
    }

    void CyEventTemplate::addtree(std::string key, std::string tree)
    {
        this -> trees[key] = tree; 
    }

    event_t CyEventTemplate::Export()
    {
        event_t event = this -> event; 
        event.event = true; 
        return event;  
    }

    std::string CyEventTemplate::Hash()
    {
        return this -> CyEvent::Hash(&(this -> event)); 
    }

    void CyEventTemplate::Import(event_t event)
    {
        this -> event = event; 
        this -> event.event = true;
        this -> is_event = true; 
    }

    bool CyEventTemplate::operator == (CyEventTemplate& ev)
    {
        event_t* ev1 = &(this -> event); 
        event_t* ev2 = &(ev.event); 
        return this -> is_same(ev1, ev2); 
    }
}
