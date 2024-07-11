#ifndef SELECTION_TEMPLATE_H
#define SELECTION_TEMPLATE_H

#include <templates/particle_template.h>
#include <templates/event_template.h>

#include <structs/property.h>
#include <structs/event.h>

#include <tools/merge_cast.h>
#include <tools/tools.h>

class container; 

class selection_template: public tools
{
    public:
        selection_template(); 
        virtual ~selection_template(); 

        cproperty<std::string, selection_template> name; 
        void static set_name(std::string*, selection_template*); 
        void static get_name(std::string*, selection_template*);

        cproperty<std::string, selection_template> hash; 
        void static set_hash(std::string*, selection_template*); 
        void static get_hash(std::string*, selection_template*); 

        cproperty<std::string, selection_template> tree;  
        void static get_tree(std::string*, selection_template*); 

        cproperty<double, selection_template> weight;
        void static set_weight(double*, selection_template*); 

        cproperty<long, selection_template> index; 
        void static set_index(long*, selection_template*); 
   
        virtual selection_template* clone(); 
        virtual bool selection(event_template* ev);
        virtual bool strategy(event_template* ev);
        virtual void merge(selection_template* sel); 

        void CompileEvent(); 
        selection_template* build(event_template* ev); 
        bool operator == (selection_template& p); 

        std::string filename = ""; 
        event_t data; 

        friend container;

    private:
        event_template* m_event = nullptr; 
        void merger(selection_template* sl2); 

}; 


#endif
