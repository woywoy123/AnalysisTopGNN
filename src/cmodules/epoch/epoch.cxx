#include "../epoch/epoch.h"

CyEpoch::CyEpoch(){}
CyEpoch::~CyEpoch(){}

void merge_this(std::vector<std::vector<float>>* in, std::vector<std::vector<float>>* out)
{
    out -> insert(out -> end(), in -> begin(), in -> end()); 
} 

void merge_this(
        std::map<int, std::vector<std::vector<float>>>* in, 
        std::map<int, std::vector<std::vector<float>>>* out)
{
    std::map<int, std::vector<std::vector<float>>>::iterator itr = in -> begin(); 
    for (; itr != in -> end(); ++itr){
        merge_this(&(itr -> second), &(*out)[itr -> first]); 
    }
}

void update_point(std::vector<std::vector<float>>* in, point_t* out)
{
    for (unsigned int i(0); i < in -> size(); ++i){
        for (unsigned int j(0); j < (*in)[i].size(); ++j){
            float val = (*in)[i][j]; 
            if (!out -> tmp.size()){ 
                out -> minimum = val; 
                out -> maximum = val; 
            }
            if (out -> minimum > val){out -> minimum = val;}
            else if (out -> maximum < val){out -> maximum = val;}
            out -> tmp.push_back(val); 
        } 
    }
}

void update_mass(data_t* in, std::map<int, mass_t>* out)
{
    std::map<int, std::vector<std::vector<float>>>::iterator itr; 
    for (itr = in -> mass_pred.begin(); itr != in -> mass_pred.end(); ++itr){
        mass_t* mss = &(*out)[itr -> first]; 
        std::vector<std::vector<float>>* m_pred  = &(in -> mass_pred[itr -> first]); 
        std::vector<std::vector<float>>* m_truth = &(in -> mass_truth[itr -> first]);
        for (unsigned int i(0); i < m_pred -> size(); ++i){
            for (unsigned int j(0); j < (*m_pred)[i].size(); ++j){
                mss -> mass_pred[(*m_pred)[i][j]] += 1; 
            }
        }
        for (unsigned int i(0); i < m_truth -> size(); ++i){
            for (unsigned int j(0); j < (*m_truth)[i].size(); ++j){
                mss -> mass_truth[(*m_truth)[i][j]] += 1; 
            }
        }
    }
}

void update_nodes(std::vector<std::vector<float>>* in, node_t* out)
{
    if (out -> max_nodes != -1){return;}
    for (unsigned int x(0); x < in -> size(); ++x){
        for (unsigned int j(0); j < (*in)[x].size(); ++j){
            out -> num_nodes[(*in)[x][j]] += 1; 
            if (out -> max_nodes > (*in)[x][j]){continue;}
            out -> max_nodes = (*in)[x][j]; 
        }
    }
    out -> make(); 
}


void CyEpoch::add_kfold(int kfold, std::map<std::string, data_t>* data)
{
    std::map<std::string, data_t>::iterator itr = data -> begin(); 
    for (; itr != data -> end(); ++itr){
        std::string name = itr -> first; 
        data_t* prc = &(this -> container[kfold][name]); 

        merge_this(&(itr -> second.truth), &(prc -> truth)); 
        itr -> second.truth.clear();

        merge_this(&(itr -> second.pred), &(prc -> pred)); 
        itr -> second.pred.clear(); 

        merge_this(&(itr -> second.accuracy), &(prc -> accuracy)); 
        itr -> second.accuracy.clear();
        
        merge_this(&(itr -> second.loss), &(prc -> loss)); 
        itr -> second.loss.clear();

        merge_this(&(itr -> second.mass_truth),  &(prc -> mass_truth)); 
        itr -> second.mass_truth.clear(); 

        merge_this(&(itr -> second.mass_pred),  &(prc -> mass_pred));  
        itr -> second.mass_pred.clear(); 

        merge_this(&(itr -> second.nodes),  &(prc -> nodes));  
        itr -> second.nodes.clear(); 

        merge_this(&(itr -> second.index),  &(prc -> index));  
        itr -> second.index.clear(); 
    } 
}

void CyEpoch::process_data()
{
    std::map<int, std::map<std::string, data_t>>::iterator itx; 
    for (itx = this -> container.begin(); itx != this -> container.end(); ++itx){
        std::map<std::string, data_t>::iterator itr = itx -> second.begin(); 
        for (; itr != itx -> second.end(); ++itr){
            std::string name = itr -> first; 
            int kfold = itx -> first; 

            roc_t* rc = &(this -> auc[kfold][name]); 
            merge_this(&(itr -> second.truth), &(rc -> truth)); 
            itr -> second.truth.clear();

            merge_this(&(itr -> second.pred), &(rc -> pred)); 
            itr -> second.pred.clear(); 

            point_t* acc = &(this -> accuracy[kfold][name]); 
            update_point(&(itr -> second.accuracy), acc); 
            itr -> second.accuracy.clear();
            acc -> make(); 
            
            point_t* lss = &(this -> loss[kfold][name]); 
            update_point(&(itr -> second.loss), lss); 
            itr -> second.loss.clear();
            lss -> make();

            update_mass(&(itr -> second), &(this -> masses[kfold][name]));  
            itr -> second.mass_truth.clear(); 
            itr -> second.mass_pred.clear(); 

            update_nodes(&(itr -> second.nodes), &(this -> nodes[kfold])); 
            itr -> second.nodes.clear(); 
            this -> nodes[kfold].make(); 
        }
    }
    this -> container.clear(); 
}
