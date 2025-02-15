#include <generators/optimizer.h>

optimizer::optimizer(){
    this -> prefix = "optimizer"; 
    this -> metric = new metrics(); 
}

optimizer::~optimizer(){
    delete this -> metric; 
    std::map<int, model_template*>::iterator itx = this -> kfold_sessions.begin(); 
    for (; itx != this -> kfold_sessions.end(); ++itx){delete itx -> second;}
}

void optimizer::import_dataloader(dataloader* dl){
    this -> metric -> m_settings = this -> m_settings; 
    this -> loader = dl;
}

void optimizer::import_model_sessions(std::tuple<model_template*, optimizer_params_t*>* models){
    model_template*       base = std::get<0>(*models); 
    optimizer_params_t* config = std::get<1>(*models); 

    base -> shush = true; 
    base -> set_optimizer(config -> optimizer); 
    
    model_settings_t settings;
    base -> clone_settings(&settings); 

    this -> info("_____ TESTING IMPORTED MODEL WITH OPTIMIZER PARAMS _____"); 
    model_template* model_k = base -> clone(); 
    model_k -> set_optimizer(config -> optimizer); 
    model_k -> import_settings(&settings); 
    model_k -> initialize(config); 
    std::vector<graph_t*> rnd = this -> loader -> get_random(this -> m_settings.num_examples); 
    for (size_t x(0); x < rnd.size(); ++x){
        if (x){model_k -> shush = true;} 
        model_k -> check_features(rnd[x]);
    }
    delete model_k; 
    this -> success("_____ PASSED TESTS AND CONFIGURATION _____"); 
}

void optimizer::training_loop(int k, int epoch){
    std::vector<graph_t*>* smpl = this -> loader -> get_k_train_set(k); 
    model_template* model = this -> kfold_sessions[k]; 
    model -> evaluation_mode(false);
    model -> epoch = epoch+1; 

    model_report* mr = this -> reports[this -> m_settings.run_name + std::to_string(k)]; 
    mr -> mode = "training";
    mr -> epoch = epoch;  

    bool batched = this -> m_settings.batch_size > 1;
    if (batched){smpl = this -> loader -> build_batch(smpl, model, mr);}
    int l = smpl -> size(); 

    torch::AutoGradMode grd(true); 
    for (int x(0); x < l; ++x){
        graph_t* gr = (*smpl)[x]; 
        model -> forward(gr, true);
        mr -> progress = float(x+1)/float(l); 
        this -> metric -> capture(mode_enum::training, k, epoch, l); 
        if (!batched){continue;}
        gr -> _purge_all(); 
        delete gr; 
        (*smpl)[x] = nullptr; 
    }
    model -> save_state(); 
    if (batched){delete smpl;}
    
    #ifdef PYC_CUDA
    c10::cuda::CUDACachingAllocator::emptyCache();
    #endif
}

void optimizer::validation_loop(int k, int epoch){
    model_template* model = this -> kfold_sessions[k]; 
    model -> evaluation_mode(true); 

    model_report* mr = this -> reports[this -> m_settings.run_name + std::to_string(k)]; 
    mr -> mode = "validation"; 

    std::vector<graph_t*>* smpl = this -> loader -> get_k_validation_set(k); 
    bool batched = this -> m_settings.batch_size > 1;
    if (batched){smpl = this -> loader -> build_batch(smpl, model, mr);}

    torch::NoGradGuard no_grd;  
    int l = smpl -> size(); 
    for (int x(0); x < l; ++x){
        graph_t* gr = (*smpl)[x]; 
        model -> forward(gr, false);
        mr -> progress = float(x+1)/float(l);
        this -> metric -> capture(mode_enum::validation, k, epoch, l); 
    }
}

void optimizer::evaluation_loop(int k, int epoch){
    model_template* model = this -> kfold_sessions[k]; 
    model -> evaluation_mode(true); 
    model_report* mr = this -> reports[this -> m_settings.run_name + std::to_string(k)]; 
    mr -> mode = "evaluation"; 

    std::vector<graph_t*>* smpl = this -> loader -> get_test_set(); 
    bool batched = this -> m_settings.batch_size > 1;
    if (batched){smpl = this -> loader -> build_batch(smpl, model, mr);}

    torch::NoGradGuard no_grd;  
    int l = smpl -> size(); 
    for (int x(0); x < l; ++x){
        graph_t* gr = (*smpl)[x]; 
        model -> forward(gr, false);
        this -> metric -> capture(mode_enum::evaluation, k, epoch, l); 
        mr -> progress = float(x+1)/float(l); 
    }
}

void optimizer::launch_model(int k){

    for (int ep(0); ep < this -> m_settings.epochs; ++ep){

        model_template* model = this -> kfold_sessions[k]; 
        if (model -> epoch > ep){continue;}
        if (this -> m_settings.training){this -> training_loop(k, ep);}
        if (this -> m_settings.validation){this -> validation_loop(k, ep);}
        if (this -> m_settings.evaluation){this -> evaluation_loop(k, ep);}
        if (this -> m_settings.debug_mode){this -> metric -> dump_plots(k);}

        model_report* mr = this -> reports[this -> m_settings.run_name + std::to_string(k)]; 
        mr -> waiting_plot = this -> metric; 
        if (this -> m_settings.debug_mode){this -> metric -> dump_plots(k); continue;}
        while (mr -> waiting_plot){std::this_thread::sleep_for(std::chrono::microseconds(10));}
    }

    model_report* mr = this -> reports[this -> m_settings.run_name + std::to_string(k)]; 
    mr -> is_complete = true; 
}

