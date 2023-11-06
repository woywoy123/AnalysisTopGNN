#include "graph.h"

torch::TensorOptions Graph::Tensors::MakeOp(torch::Tensor x)
{
    torch::TensorOptions op = torch::TensorOptions().device(x.device()).dtype(x.dtype()); 
    return op; 
}

std::map<std::string, std::vector<torch::Tensor>> Graph::Tensors::edge_aggregation(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor node_feature, const bool include_zero)
{
    std::map<std::string, std::vector<torch::Tensor>> output; 
    const unsigned int max = torch::max(prediction).item<int>()+1; 
    const unsigned int dim_i = node_feature.size(0);   
    const unsigned int dim_j = node_feature.size(1); 

    const unsigned int src_dst = edge_index.size(0); 
    const unsigned int len = edge_index.size(1); 
    
    torch::Tensor _edge_index = edge_index.clone(); 
    if (src_dst != 2 && len == 2){ _edge_index = torch::transpose(_edge_index, 0, 1); }

    const torch::TensorOptions op = Graph::Tensors::MakeOp(prediction); 
    torch::Tensor e_i = _edge_index.index({0, torch::indexing::Slice()}); 
    torch::Tensor e_j = _edge_index.index({1, torch::indexing::Slice()}); 
    torch::Tensor pair_m = -torch::ones({dim_i, dim_i}, op.dtype(torch::kLong)); 
    torch::Tensor msk_self = e_i != e_j; 
    torch::Tensor pred = prediction.view({-1}).clone(); 
    torch::Tensor pmu = torch::zeros({dim_i, dim_j}, op); 
     
    // Add self loops to graph 
    pair_m.index_put_({e_i, e_i}, e_i);
    for (signed int i(0); i < max; ++i)
    {
        if (i == 0 && !include_zero){continue;}
        std::stringstream x; 
        std::string name; 
        x << i; 
        x >> name; 

        // Filter all predictions based on classification
        torch::Tensor msk = (pred == i)*msk_self;  

        // remove edges that do not meet the classification 
        torch::Tensor e_i_p = e_i.index({msk}); 
        torch::Tensor e_j_p = e_j.index({msk});
       
        // record the matrix associated with the classification 
        torch::Tensor pair_m_p = pair_m.clone(); 
        pair_m_p.index_put_({e_i_p, e_j_p}, e_j_p); 
       
        pair_m_p = std::get<0>(pair_m_p.sort(-1, true)); 

        // aggregate edge nodes
        torch::Tensor pmu_i = pmu.clone();  
        for (signed int k(0); k < dim_i; ++k)
        {
            torch::Tensor this_pair, node; 
            this_pair = pair_m_p.index({k}); 
            this_pair = this_pair.index({this_pair > -1}); 
            node = node_feature.index({this_pair, torch::indexing::Slice()}).sum(0);  
            pmu_i.index_put_({k}, node); 
        }

        // find the unique node aggregations
        torch::Tensor pmu_u, clusters, revert; 
        std::tuple<torch::Tensor, torch::Tensor, torch::Tensor> id2; 
        id2 = torch::unique_dim(pair_m_p, 0, false, true, false); 
        clusters = std::get<0>(id2); 
        revert = std::get<1>(id2); 
        pmu_u = torch::zeros({clusters.size(0), dim_j}, op); 
        
        for (signed int k(0); k < clusters.size(0); ++k)
        {
            torch::Tensor this_pair, node; 
            this_pair = clusters.index({k}); 
            this_pair = this_pair.index({this_pair > -1}); 
            node = node_feature.index({this_pair, torch::indexing::Slice()}).sum(0);  
            pmu_u.index_put_({k}, node); 
        }

        output[name] = {clusters, pmu_u.to(torch::kFloat), revert, pmu_i.to(torch::kFloat)};  
    }
    return output; 
}

std::map<std::string, std::vector<torch::Tensor>> Graph::Tensors::node_aggregation(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor node_feature, const bool include_zero)
{
    const unsigned int src_dst = edge_index.size(0); 
    const unsigned int len = edge_index.size(1); 
    
    torch::Tensor _edge_index = edge_index.clone(); 
    if (src_dst != 2 && len == 2){ _edge_index = torch::transpose(_edge_index, 0, 1); }

    torch::Tensor e_i = _edge_index.index({0, torch::indexing::Slice()}); 
    torch::Tensor pred = prediction.index({e_i}).clone(); 

    return Graph::Tensors::edge_aggregation(edge_index, pred, node_feature, include_zero);  
}

// --------------------- Interfaces ------------------------ //
std::map<std::string, std::vector<torch::Tensor>> Graph::Tensors::Polar::edge_pmu(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor pmu, const bool include_zero)
{
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pmu); 
    return Graph::Tensors::edge_aggregation(edge_index, prediction, pmc, include_zero); 
}

std::map<std::string, std::vector<torch::Tensor>> Graph::Tensors::Polar::edge_pmu(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  
        const bool include_zero)
{ 
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pt, eta, phi, e); 
    return Graph::Tensors::edge_aggregation(edge_index, prediction, pmc, include_zero); 
}

std::map<std::string, std::vector<torch::Tensor>> Graph::Tensors::Polar::node_pmu(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor pmu, const bool include_zero)
{ 
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pmu); 
    return Graph::Tensors::node_aggregation(edge_index, prediction, pmc, include_zero); 
}

std::map<std::string, std::vector<torch::Tensor>> Graph::Tensors::Polar::node_pmu(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  
        const bool include_zero)
{ 
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pt, eta, phi, e); 
    return Graph::Tensors::node_aggregation(edge_index, prediction, pmc, include_zero); 
}

std::map<std::string, std::vector<torch::Tensor>> Graph::Tensors::Cartesian::edge_pmc(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor pmc, const bool include_zero)
{
    return Graph::Tensors::edge_aggregation(edge_index, prediction, pmc, include_zero); 
}

std::map<std::string, std::vector<torch::Tensor>> Graph::Tensors::Cartesian::edge_pmc(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  
        const bool include_zero)
{

    std::vector<signed long> d = {-1, 1};
    std::vector<torch::Tensor> pmc = {px.view(d), py.view(d), pz.view(d), e.view(d)}; 
    return Graph::Tensors::edge_aggregation(edge_index, prediction, torch::cat(pmc, -1), include_zero); 
}

std::map<std::string, std::vector<torch::Tensor>> Graph::Tensors::Cartesian::node_pmc(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor pmc, const bool include_zero)
{
    return Graph::Tensors::node_aggregation(edge_index, prediction, pmc, include_zero); 
}

std::map<std::string, std::vector<torch::Tensor>> Graph::Tensors::Cartesian::node_pmc(
        torch::Tensor edge_index, torch::Tensor prediction, 
        torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  
        const bool include_zero)
{
    std::vector<signed long> d = {-1, 1};
    std::vector<torch::Tensor> pmc = {px.view(d), py.view(d), pz.view(d), e.view(d)}; 
    return Graph::Tensors::node_aggregation(edge_index, prediction, torch::cat(pmc, -1), include_zero); 
}
