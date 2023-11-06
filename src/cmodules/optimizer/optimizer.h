#include "../abstractions/abstractions.h"
#include "../abstractions/cytypes.h"
#include "../epoch/epoch.h"
#include <cmath>

#ifndef OPTIMIZER_H
#define OPTIMIZER_H

namespace Optimizer
{
    class CyFold
    {
        public:
            CyFold(); 
            ~CyFold();
            void Import(const folds_t*); 
            int length(); 
            std::vector<std::vector<std::string>> fetchthis(int batch_size);
            std::vector<std::string> check_this(std::vector<std::string> hashes);
            void flushthis(std::vector<std::string> inpt);
            std::map<std::string, bool> cached_hashes = {}; 
    };

    class CyOptimizer
    {
        public:
            CyOptimizer(); 
            ~CyOptimizer(); 
            void register_fold(const folds_t*);
            std::map<std::string, int> fold_map(); 

            void flush_train(std::vector<std::string>* hashes, int kfold);
            void flush_validation(std::vector<std::string>* hashes, int kfold);
            void flush_evaluation(std::vector<std::string>* hashes);

            std::vector<std::vector<std::string>> fetch_train(int kfold, int batch_size);
            std::vector<std::vector<std::string>> fetch_validation(int kfold, int batch_size);
            std::vector<std::vector<std::string>> fetch_evaluation(int batch_size);
            
            std::vector<std::string> check_train(std::vector<std::string>* hashes, int kfold);
            std::vector<std::string> check_validation(std::vector<std::string>* hashes, int kfold);
            std::vector<std::string> check_evaluation(std::vector<std::string>* hashes);

            void train_epoch_kfold(int epoch, int kfold, std::map<std::string, data_t>* data);
            void validation_epoch_kfold(int epoch, int kfold, std::map<std::string, data_t>* data);
            void evaluation_epoch_kfold(int epoch, int kfold, std::map<std::string, data_t>* data);

            std::map<int, CyFold*> kfold_eval    = {};
            std::map<int, CyFold*> kfold_train   = {};
            std::map<int, CyFold*> leaveout_test = {}; 

            std::map<int, CyEpoch*> epoch_train = {};
            std::map<int, CyEpoch*> epoch_valid  = {};
            std::map<int, CyEpoch*> epoch_test  = {}; 

            std::vector<int> use_folds = {};

        private:
            void flush_data(
                    std::vector<std::string>* hashes, 
                    std::map<int, CyFold*>* folds, int kfold)
            {
                if (!folds -> count(kfold)){return;}
                folds -> at(kfold) -> flushthis(*hashes); 
            };

            std::vector<std::vector<std::string>> fetch_quant(
                    int kfold, int batch_size, 
                    std::map<int, CyFold*>* folds)
            {
                if (!folds -> count(kfold)){ return {}; }
                CyFold* f = folds -> at(kfold); 
                return f -> fetchthis(batch_size); 
            }; 

            std::vector<std::string> check_data(
                    std::vector<std::string>* hashes, 
                    std::map<int, CyFold*>* fold, int kfold)
            {
                if (!fold -> count(kfold)){ return {}; }
                CyFold* f = fold -> at(kfold); 
                return f -> check_this(*hashes); 
            }; 

            CyEpoch* add_epoch(int epoch, std::map<int, CyEpoch*>* inpt)
            {
                if (!inpt -> count(epoch)){
                    (*inpt)[epoch] = new CyEpoch(); 
                    (*inpt)[epoch] -> epoch = epoch; 
                }
                return inpt -> at(epoch); 
            }; 

            template <typename G>
            void delete_folds(std::map<int, G*>* fold)
            {
                typename std::map<int, G*>::iterator itr; 
                itr = fold -> begin(); 
                for (; itr != fold -> end(); ++itr){
                    delete itr -> second; 
                }
            }; 
    }; 

}
#endif
