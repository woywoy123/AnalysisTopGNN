#include "../abstractions/abstractions.h"
#include "../optimizer/optimizer.h"

namespace Optimizer
{
    CyFold::CyFold(){}
    CyFold::~CyFold(){}
    int CyFold::length(){return this -> cached_hashes.size();}
    void CyFold::Import(const folds_t* in){this -> cached_hashes[in -> event_hash] = false;}

    std::vector<std::vector<std::string>> CyFold::fetchthis(int batch_size)
    {
        std::vector<std::string> output = {}; 
        std::map<std::string, bool>* cached = &(this -> cached_hashes);
        std::map<std::string, bool>::iterator itr = cached -> begin();
        for (; itr != cached -> end(); ++itr){output.push_back(itr -> first);}
        return Tools::Quantize(output, batch_size); 
    }

    void CyFold::flushthis(std::vector<std::string> inpt)
    {
        std::map<std::string, bool>* cached = &(this -> cached_hashes); 
        for (std::string hash : inpt){(*cached)[hash] = false;}
    }

    std::vector<std::string> CyFold::check_this(std::vector<std::string> hashes)
    {
        std::vector<std::string> output; 
        std::map<std::string, bool>* cached = &(this -> cached_hashes); 
        for (std::string hash : hashes){
            if (cached -> at(hash)){ continue; }
            output.push_back(hash);
            (*cached)[hash] = true;
        }        
        return output; 
    }


    CyOptimizer::CyOptimizer(){}
    CyOptimizer::~CyOptimizer()
    {
        this -> delete_folds(&(this -> leaveout_test)); 
        this -> delete_folds(&(this -> kfold_eval)); 
        this -> delete_folds(&(this -> kfold_train)); 

        this -> delete_folds(&(this -> epoch_train)); 
        this -> delete_folds(&(this -> epoch_valid)); 
        this -> delete_folds(&(this -> epoch_test)); 
    }

    void CyOptimizer::register_fold(const folds_t* inpt)
    {
        std::map<int, CyFold*>* fold; 
        if (inpt -> test){ fold = &(this -> leaveout_test); }
        else if (inpt -> train){ fold = &(this -> kfold_train); }
        else if (inpt -> evaluation){ fold = &(this -> kfold_eval); }
        else {return;}

        if (fold -> count(inpt -> kfold)){}
        else { (*fold)[inpt -> kfold] = new CyFold(); }
        CyFold* this_fold = fold -> at(inpt -> kfold);
        this_fold -> Import(inpt);
    }

    std::map<std::string, int> CyOptimizer::fold_map()
    {
        std::map<std::string, int> output = {}; 
        std::map<int, CyFold*>* test = &(this -> leaveout_test); 
        std::map<int, CyFold*>::iterator itr; 
        for (itr = test -> begin(); itr != test -> end(); ++itr){
            std::string key = "leave-out" + Tools::ToString(itr -> first); 
            output[key] += itr -> second -> length();  
        } 

        std::map<int, CyFold*>* eval = &(this -> kfold_eval); 
        for (itr = eval -> begin(); itr != eval -> end(); ++itr){
            std::string key = "eval-k" + Tools::ToString(itr -> first); 
            output[key] += itr -> second -> length();  
        } 

        std::map<int, CyFold*>* train = &(this -> kfold_train); 
        for (itr = train -> begin(); itr != train -> end(); ++itr){
            std::string key = "train-k" + Tools::ToString(itr -> first); 
            output[key] += itr -> second -> length();  
        }
        return output;  
    }  

    std::vector<std::vector<std::string>> CyOptimizer::fetch_train(int kfold, int batch_size)
    {
        return this -> fetch_quant(kfold, batch_size, &(this -> kfold_train)); 
    }

    void CyOptimizer::flush_train(std::vector<std::string>* hashes, int kfold)
    {
        this -> flush_data(hashes, &(this -> kfold_train), kfold); 
    }

    std::vector<std::string> CyOptimizer::check_train(std::vector<std::string>* hashes, int kfold)
    {
        return this -> check_data(hashes, &(this -> kfold_train), kfold);
    }

    std::vector<std::vector<std::string>> CyOptimizer::fetch_validation(int kfold, int batch_size)
    {
        return this -> fetch_quant(kfold, batch_size, &(this -> kfold_eval)); 
    }

    void CyOptimizer::flush_validation(std::vector<std::string>* hashes, int kfold)
    {
        this -> flush_data(hashes, &(this -> kfold_eval), kfold); 
    }

    std::vector<std::string> CyOptimizer::check_validation(std::vector<std::string>* hashes, int kfold)
    {
        return this -> check_data(hashes, &(this -> kfold_eval), kfold);
    }

    std::vector<std::vector<std::string>> CyOptimizer::fetch_evaluation(int batch_size)
    {
        return this -> fetch_quant(-1, batch_size, &(this -> leaveout_test)); 
    }

    void CyOptimizer::flush_evaluation(std::vector<std::string>* hashes)
    {
        this -> flush_data(hashes, &(this -> leaveout_test), -1); 
    }

    std::vector<std::string> CyOptimizer::check_evaluation(std::vector<std::string>* hashes)
    {
        return this -> check_data(hashes, &(this -> leaveout_test), -1);
    }

    void CyOptimizer::train_epoch_kfold(int epoch, int kfold, std::map<std::string, data_t>* data)
    {
        CyEpoch* ep = this -> add_epoch(epoch, &(this -> epoch_train)); 
        ep -> add_kfold(kfold, data); 
    }

    void CyOptimizer::validation_epoch_kfold(int epoch, int kfold, std::map<std::string, data_t>* data)
    {
        CyEpoch* ep = this -> add_epoch(epoch, &(this -> epoch_valid)); 
        ep -> add_kfold(kfold, data); 
    }

    void CyOptimizer::evaluation_epoch_kfold(int epoch, int kfold, std::map<std::string, data_t>* data)
    {
        CyEpoch* ep = this -> add_epoch(epoch, &(this -> epoch_test)); 
        ep -> add_kfold(kfold, data); 
    }

}

