#ifndef NODES_FEATURES_BSM_4TOPS_H
#define NODES_FEATURES_BSM_4TOPS_H

// --------------------- Node Truth --------------------- //
void static res_node(int* o, particle_template* p){
    std::string type = p -> type; 
    if (type == "top"){*o = ((top*)p) -> from_res;}
    else if (type == "children"){*o = ((top_children*)p) -> from_res;}
    else if (type == "truthjets"){*o = ((truthjet*)p) -> from_res;}
    else if (type == "jet"){*o = ((jet*)p) -> from_res;}
    else {*o = 0;} 
}; 

void static top_node(int* o, particle_template* p){
    std::string type = p -> type; 
    if (type == "top"){*o = ((top*)p) -> index;}
    else if (type == "children"){*o = ((top_children*)p) -> top_index;}
    else if (type == "truthjets"){
        truthjet* tx = (truthjet*)p; 
        if (!tx -> top_index.size()){*o = -1;}
        else {*o = tx -> top_index[0];}
    }

    else if (type == "jet"){
        jet* tx = (jet*)p; 
        if (!tx -> top_index.size()){*o = -1;}
        else {*o = tx -> top_index[0];}
    }

    else if (type == "mu"){
        muon* tx = (muon*)p; 
        *o = tx -> index; 
    }

    else if (type == "el"){
        electron* tx = (electron*)p; 
        *o = tx -> index; 
    }
    else {*o = -1;} 
}; 

// --------------------- Node Observables --------------------- //
void static pt(double* o, particle_template* p){*o = p -> pt;} 
void static eta(double* o, particle_template* p){*o = p -> eta;} 
void static phi(double* o, particle_template* p){*o = p -> phi;} 
void static energy(double* o, particle_template* p){*o = p -> e;}

void static is_lepton(int* o, particle_template* p){*o = (p -> is_lep && !p -> is_nu);}
void static is_bquark(int* o, particle_template* p){*o = p -> is_b;}
void static is_neutrino(int* o, particle_template* p){*o = p -> is_nu;}
#endif
