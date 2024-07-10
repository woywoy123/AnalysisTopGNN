#ifndef CHILDRENKINEMATICS_H
#define CHILDRENKINEMATICS_H

#include <bsm_4tops/event.h>
#include <templates/selection_template.h>

class childrenkinematics: public selection_template
{
    public:
        childrenkinematics();
        ~childrenkinematics() override; 
        selection_template* clone() override; 

        bool selection(event_template* ev) override; 
        bool strategy(event_template* ev) override;
        void merge(selection_template* sl) override;

        std::map<std::string, std::vector<float>> res_kinematics = {}; 
        std::map<std::string, std::vector<float>> spec_kinematics = {}; 

        std::map<std::string, std::map<std::string, std::vector<float>>> res_pdgid_kinematics = {}; 
        std::map<std::string, std::map<std::string, std::vector<float>>> spec_pdgid_kinematics = {}; 

        std::map<std::string, std::map<std::string, std::vector<float>>> res_decay_mode = {}; 
        std::map<std::string, std::map<std::string, std::vector<float>>> spec_decay_mode = {}; 

        std::map<std::string, std::vector<float>> mass_clustering = {}; 
        std::map<std::string, std::vector<float>> dr_clustering = {}; 
        std::map<std::string, std::vector<float>> top_pt_clustering = {}; 
        std::map<std::string, std::vector<float>> top_energy_clustering = {}; 
        std::map<std::string, std::vector<float>> top_children_dr = {}; 

        std::map<std::string, std::map<std::string, std::vector<float>>> fractional = {}; 


    private:

        template <typename g>
        std::vector<g*> vectorize(std::map<std::string, g*>* in){
            typename std::vector<g*> out = {}; 
            typename std::map<std::string, g*>::iterator itr = in -> begin(); 
            for (; itr != in -> end(); ++itr){out.push_back(itr -> second);}
            return out; 
        }



        template <typename g>
        void dump_kinematics(std::map<std::string, std::vector<float>>* data, g* p){
            (*data)["pt"].push_back((p -> pt)/1000); 
            (*data)["energy"].push_back((p -> e)/1000); 
            (*data)["eta"].push_back(p -> eta); 
            (*data)["phi"].push_back(p -> phi); 
        }

        template <typename g>
        float sum(std::vector<g*>* ch){
            particle_template* prt = new particle_template(); 
            for (size_t x(0); x < ch -> size(); ++x){prt -> iadd(ch -> at(x));}
            float mass = prt -> mass / 1000; 
            delete prt; 
            return mass; 
        }





};

#endif
