#include "gnn-event.h"

gnn_event::gnn_event(){
    this -> name = "gnn_event"; 

    // ------ observables ------- //
    this -> add_leaf("signal"    , "extra_is_res_score"); 
    this -> add_leaf("ntops"     , "extra_ntops_score"); 
    this -> add_leaf("res_edge"  , "extra_res_edge_score"); 
    this -> add_leaf("top_edge"  , "extra_top_edge_score"); 
    this -> add_leaf("weight"    , "event_weight");
    this -> add_leaf("edge_index", "edge_index");
    this -> add_leaf("num_jets"  , "extra_num_jets");  
    this -> add_leaf("num_bjets" , "extra_num_bjets");  
    this -> add_leaf("num_leps"  , "extra_num_leps"); 
    this -> add_leaf("met"       , "g_i_met");
    this -> add_leaf("phi"       , "g_i_phi");

    // ------ truth features ------ //
    this -> add_leaf("truth_ntops"   , "extra_truth_ntops"   ); 
    this -> add_leaf("truth_signal"  , "extra_truth_signal"  ); 
    this -> add_leaf("truth_res_edge", "extra_truth_res_edge"); 
    this -> add_leaf("truth_top_edge", "extra_truth_top_edge"); 

    this -> trees = {"nominal"}; 
    this -> register_particle(&this -> m_event_particles);
}

gnn_event::~gnn_event(){
    this -> deregister_particle(&this -> m_r_zprime); 
    this -> deregister_particle(&this -> m_t_zprime); 
    this -> deregister_particle(&this -> m_r_tops);
    this -> deregister_particle(&this -> m_t_tops); 
}

event_template* gnn_event::clone(){return (event_template*)new gnn_event();}

void gnn_event::build(element_t* el){
    auto lamb_vvi = [](element_t* el, std::string key, std::vector<std::vector<int>>* out){
        std::vector<std::vector<int>> tmp; 
        if (!el -> get(key, &tmp)){return;}
        out -> assign(2, {}); 
        for (size_t x(0); x < tmp.size(); ++x){
            (*out)[0].push_back(tmp[x][0]); 
            (*out)[1].push_back(tmp[x][1]); 
        }
    };

    reduce_2(el, "weight"      , &this -> weight); 
    lamb_vvi(el, "edge_index"  , &this -> m_edge_index);

    reduce(el, "signal", &this -> signal_scores); 
    read(el, "res_edge", &this -> edge_res_scores); 
    read(el, "top_edge", &this -> edge_top_scores); 
   
    reduce(el, "ntops"      , &this -> ntops_scores); 
    reduce_2(el, "num_jets" , &this -> num_jets); 
    reduce_2(el, "num_leps" , &this -> num_leps); 
    reduce_2(el, "num_bjets", &this -> num_bjets); 

    reduce_2(el, "truth_ntops" , &this -> t_ntops);  
    reduce_2(el, "truth_signal", &this -> t_signal);  

    reduce(el, "truth_res_edge", &this -> t_edge_res); 
    reduce(el, "truth_top_edge", &this -> t_edge_top); 
}

void gnn_event::CompileEvent(){

    auto cluster = [this](
            std::map<int, std::map<std::string, particle_gnn*>>* clust, 
            std::map<std::string, std::vector<particle_gnn*>>* out,
            std::map<std::string, float>* bin_out,
            std::map<int, std::map<int, float>>* bin_data
    ){

        std::map<int, float> PR; 
        size_t n_nodes = clust -> size(); 
        std::map<int, std::map<int, float>> Mij; 
        for (size_t x(0); x < n_nodes; ++x){
            float wij_n = 0; 
            PR[x] = 1 / float(n_nodes); 
            if (!bin_data){continue;}
            for (size_t y(0); y < clust -> size(); ++y){
                Mij[x][y] = (*bin_data)[x][y]; 
                wij_n += (*bin_data)[x][y]; 
            }

            if (wij_n == 0){continue;} 
            wij_n = 1 / wij_n;
            for (size_t y(0); y < n_nodes; ++y){Mij[x][y] = Mij[x][y] * wij_n;}
        }

        int t_out = 0; 
        float norm_ = 0; 
        std::map<int, std::map<std::string, particle_gnn*>>::iterator itr;
        while (bin_data && t_out < n_nodes){
            float norm = 0; 
            std::map<int, float> pr_;
            for (size_t p(0); p < PR.size(); ++p){norm += PR[p];}

            if (!norm + !std::abs(norm_ - norm)){break;}
            for (size_t p(0); p < PR.size(); ++p){PR[p] = PR[p]/norm;}
            for (itr = clust -> begin(); itr != clust -> end(); ++itr){
                int src = itr -> first; 
                for (size_t x(0); x < n_nodes; ++x){
                    if (!Mij[x][src] + (x == src)){continue;}
                    float out_s = (*clust)[x].size(); 
                    pr_[src] += PR[x]*Mij[x][src]; 
                }
            }
            PR = pr_; 
            norm_ = norm; 
            ++t_out; 
        }

        tools tl = tools(); 
        for (itr = clust -> begin(); itr != clust -> end(); ++itr){
            int src = itr -> first; 
            if (!PR[src] && bin_data){continue;}
            std::map<std::string, particle_gnn*> tmp; 
            std::map<std::string, particle_gnn*>::iterator itp; 
            for (itp = itr -> second.begin(); itp != itr -> second.end(); ++itp){
                int p_node = itp -> second -> index; 
                if (bin_data && !(*bin_data)[src][p_node]){continue;}
                tmp[itp -> second -> hash] = itp -> second;
            }
            if (tmp.size() <= 2){continue;}
            std::string hash = ""; 
            for (itp = tmp.begin(); itp != tmp.end(); ++itp){hash = tl.hash(hash + itp -> first);}
            if (out -> count(hash)){continue;}
            this -> vectorize(&tmp, &(*out)[hash]); 
            if (!bin_out){continue;}
            for (itp = tmp.begin(); itp != tmp.end(); ++itp){(*bin_out)[hash] += PR[itp -> second -> index];}
        } 
    }; 


    std::map<int, particle_gnn*> particle = this -> sort_by_index(&this -> m_event_particles);
    this -> p_signal = this -> signal_scores[0] < this -> signal_scores[1];  
    this -> s_signal = this -> signal_scores[1]; 
    this -> s_ntops  = this -> max(&this -> ntops_scores); 

    for (size_t x(0); x < 5; ++x){
        if (this -> s_ntops != this -> ntops_scores[x]){continue;}
        this -> p_ntops = int(x);
        break; 
    }


    std::map<int, std::map<int, float>> bin_top, bin_zprime; 
    std::map<int, std::map<std::string, particle_gnn*>> real_tops; 
    std::map<int, std::map<std::string, particle_gnn*>> real_zprime; 

    std::map<int, std::map<std::string, particle_gnn*>> reco_tops; 
    std::map<int, std::map<std::string, particle_gnn*>> reco_zprime; 

    std::vector<int> src = this -> m_edge_index[0]; 
    std::vector<int> dst = this -> m_edge_index[1]; 
    for (size_t x(0); x < src.size(); ++x){
        int top_ij = (this -> edge_top_scores[x][0] < this -> edge_top_scores[x][1]); 
        int res_ij = (this -> edge_res_scores[x][0] < this -> edge_res_scores[x][1]); 
        if (top_ij){bin_top[src[x]][dst[x]]    = this -> edge_top_scores[x][1];}
        if (res_ij){bin_zprime[src[x]][dst[x]] = this -> edge_res_scores[x][1];}

        std::string hx = particle[dst[x]] -> hash; 
        reco_tops[src[x]][hx]   = particle[dst[x]];
        reco_zprime[src[x]][hx] = particle[dst[x]];
        
        if (this -> t_edge_top[x]){real_tops[src[x]][hx]   = particle[dst[x]];}
        if (this -> t_edge_res[x]){real_zprime[src[x]][hx] = particle[dst[x]];}
    }

    std::map<std::string, std::vector<particle_gnn*>>::iterator it;

    // ---- truth --- //
    std::map<std::string, std::vector<particle_gnn*>> c_real_tops;
    cluster(&real_tops  , &c_real_tops, nullptr, nullptr); 
    for (it = c_real_tops.begin(); it != c_real_tops.end(); ++it){
        top* t = nullptr;
        this -> sum(&it -> second, &t);  
        this -> m_t_tops[t -> hash] = t; 

        std::map<std::string, particle_template*> ch = t -> children; 
        std::map<std::string, particle_template*>::iterator itc = ch.begin(); 
        for (; itc != ch.end(); ++itc){t -> n_leps += ((particle_gnn*)itc -> second) -> lep;}
        t -> n_nodes = ch.size(); 
    }

    std::map<std::string, std::vector<particle_gnn*>> c_real_zprime;
    cluster(&real_zprime, &c_real_zprime, nullptr, nullptr); 
    for (it = c_real_zprime.begin(); it != c_real_zprime.end(); ++it){
        zprime* t = nullptr;
        this -> sum(&it -> second, &t);  
        this -> m_t_zprime[t -> hash] = t; 

        std::map<std::string, particle_template*> ch = t -> children; 
        std::map<std::string, particle_template*>::iterator itc = ch.begin(); 
        for (; itc != ch.end(); ++itc){t -> n_leps += ((particle_gnn*)itc -> second) -> lep;}
        t -> n_nodes = ch.size(); 
    }

 
    // ---- reco ---- //
    std::map<std::string, float> c_reco_tops_bin; 
    std::map<std::string, std::vector<particle_gnn*>> c_reco_tops;
    cluster(&reco_tops  , &c_reco_tops, &c_reco_tops_bin, &bin_top); 
    for (it = c_reco_tops.begin(); it != c_reco_tops.end(); ++it){
        top* t = nullptr;
        this -> sum(&it -> second, &t);  
        t -> av_score = c_reco_tops_bin[it -> first]; 
        this -> m_r_tops[t -> hash] = t;

        std::map<std::string, particle_template*> ch = t -> children; 
        std::map<std::string, particle_template*>::iterator itc = ch.begin(); 
        for (; itc != ch.end(); ++itc){t -> n_leps += ((particle_gnn*)itc -> second) -> lep;}
        t -> n_nodes = ch.size(); 
    }

    std::map<std::string, float> c_reco_zprime_bin; 
    std::map<std::string, std::vector<particle_gnn*>> c_reco_zprime;
    cluster(&reco_zprime, &c_reco_zprime, &c_reco_zprime_bin, &bin_zprime);
    for (it = c_reco_zprime.begin(); it != c_reco_zprime.end(); ++it){
        zprime* t = nullptr;
        this -> sum(&it -> second, &t);  
        t -> av_score = c_reco_zprime_bin[it -> first]; 
        this -> m_r_zprime[t -> hash] = t; 

        std::map<std::string, particle_template*> ch = t -> children; 
        std::map<std::string, particle_template*>::iterator itc = ch.begin(); 
        for (; itc != ch.end(); ++itc){t -> n_leps += ((particle_gnn*)itc -> second) -> lep;}
        t -> n_nodes = ch.size(); 
     }

    // ----- vectorize the output particles ------ //
    this -> vectorize(&this -> m_r_zprime, &this -> r_zprime); 
    this -> vectorize(&this -> m_t_zprime, &this -> t_zprime); 

    this -> vectorize(&this -> m_r_tops, &this -> r_tops); 
    this -> vectorize(&this -> m_t_tops, &this -> t_tops); 
    this -> vectorize(&this -> m_event_particles, &this -> event_particles); 

    this -> m_edge_index = {}; 
}
