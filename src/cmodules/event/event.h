#include "../abstractions/abstractions.h"
#include "../abstractions/cytypes.h"

#ifndef EVENT_H
#define EVENT_H

namespace CyTemplate
{
    class CyEventTemplate : public Abstraction::CyEvent
    {
        public: 
            CyEventTemplate(); 
            ~CyEventTemplate();

            event_t Export(); 
            std::string Hash();
            void Import(event_t); 
            
            void addleaf(std::string key, std::string leaf); 
            void addbranch(std::string key, std::string branch); 
            void addtree(std::string key, std::string tree); 
            
            bool operator == (CyEventTemplate& ev);
       
            std::map<std::string, std::string> leaves = {}; 
            std::map<std::string, std::string> branches = {};  
            std::map<std::string, std::string> trees = {}; 
    }; 
}
#endif
