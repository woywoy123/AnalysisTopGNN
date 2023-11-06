#include "../abstractions/cytypes.h"
#include <cmath>

#ifndef EPOCH_H
#define EPOCH_H

struct point_t
{
    float minimum = 0; 
    float maximum = 0; 

    std::vector<float> tmp; 
    float average = 0; 
    float stdev = 0;

    void make(){
        float n = tmp.size(); 
        for (float x : tmp){average += (x / n);}
        for (float x : tmp){stdev += std::pow(average - x, 2)/n;}
        stdev = std::pow(stdev, 0.5); 
        tmp.clear(); 
    }
};

struct roc_t
{
    std::map<int, float> auc; 
    std::vector<std::vector<float>> truth; 
    std::vector<std::vector<float>> pred; 

    std::map<int, std::vector<float>> fpr; 
    std::map<int, std::vector<float>> tpr; 
    std::map<int, std::vector<float>> thre; 
}; 

struct node_t
{
    int max_nodes = -1; 
    std::map<int, int> num_nodes = {}; 

    void make(){
        for (int x(0); x < max_nodes; ++x){num_nodes[x];}
    }
};

struct mass_t
{
    std::map<float, int> mass_truth = {}; 
    std::map<float, int> mass_pred = {}; 
}; 

class CyEpoch
{
    public:
        CyEpoch(); 
        ~CyEpoch(); 
        void add_kfold(int, std::map<std::string, data_t>*); 
        void process_data(); 

        std::map<int, std::map<std::string, data_t>> container;
        std::map<int, std::map<std::string, roc_t>> auc; 

        std::map<int, std::map<std::string, point_t>> accuracy; 
        std::map<int, std::map<std::string, point_t>> loss; 

        std::map<int, std::map<std::string, std::map<int, mass_t>>> masses; 
        std::map<int, node_t> nodes; 
    
        int epoch; 

};

#endif
