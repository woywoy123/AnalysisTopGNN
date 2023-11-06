#include <transform/cartesian-cuda/cartesian.h>
#include <transform/polar-cuda/polar.h>
#include <physics/physics-cuda/physics.h>
#include <torch/torch.h>
#include <stdio.h>
#include <vector>
#include <map>

#ifndef GRAPH_CUDA_KERNEL_H
#define GRAPH_CUDA_KERNEL_H
#include "graph-kernel.cu"

#define CHECK_CUDA(x) TORCH_CHECK(x.device().is_cuda(), "#x must be on CUDA")
#define CHECK_CONTIGUOUS(x) TORCH_CHECK(x.is_contiguous(), "#x must be contiguous")
#define CHECK_INPUT(x) CHECK_CUDA(x); CHECK_CONTIGUOUS(x)

static const dim3 BLOCKS(const unsigned int threads, const unsigned int len)
{
    const dim3 blocks( (len + threads -1) / threads ); 
    return blocks; 
}

static const dim3 BLOCKS(
    const unsigned int threads, const unsigned int len, const unsigned int dy)
{
    const dim3 blocks( (len + threads -1) / threads, dy); 
    return blocks;
}

static const dim3 BLOCKS(
    const unsigned int threads, const unsigned int len, 
    const unsigned int dy, const unsigned int dz)
{
    const dim3 blocks( (len + threads -1) / threads, dy, dz); 
    return blocks; 
}

static const torch::TensorOptions _MakeOp(torch::Tensor v1)
{
    return torch::TensorOptions().dtype(v1.scalar_type()).device(v1.device()); 
}

std::map<std::string, std::vector<torch::Tensor>> _edge_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor node_feature, const bool include_zero)
{

    std::map<std::string, std::vector<torch::Tensor>> output; 
    const torch::TensorOptions op = _MakeOp(edge_index); 
    const unsigned int max = torch::max(prediction).item<int>()+1; 
    const unsigned int dim_i = node_feature.size(0); 
    const unsigned int dim_j = node_feature.size(1); 
    const unsigned int threads = 1024; 
    std::vector<long> dims = {max, dim_i, dim_i}; 

    torch::Tensor pred, _edge_index; 
    pred = prediction.view({-1}).clone(); 
    const unsigned int pred_l = pred.size(0); 
    const unsigned int x = edge_index.size(0); 
    const unsigned int j = edge_index.size(1); 
    if (x != 2 && j == 2){_edge_index = torch::transpose(edge_index, 0, 1).clone(); }
    else { _edge_index = edge_index.clone(); }

    CHECK_INPUT(pred); 
    CHECK_INPUT(node_feature); 
    torch::Tensor pair_m = torch::ones(dims, op)*-1;  
    torch::Tensor pmu_i = torch::zeros({max, dim_i, dim_j}, op);
    node_feature = node_feature.clone().to(torch::kDouble); 

    const dim3 blk = BLOCKS(threads, pred_l, max); 
    AT_DISPATCH_ALL_TYPES(pair_m.scalar_type(), "PredictionTopology", ([&]
    {
        _PredTopo<scalar_t><<< blk, threads >>>(
                pair_m.packed_accessor32<scalar_t, 3, torch::RestrictPtrTraits>(), 
           _edge_index.packed_accessor32<scalar_t, 2, torch::RestrictPtrTraits>(),
                  pred.packed_accessor32<scalar_t, 1, torch::RestrictPtrTraits>(),  
                pred_l, max, include_zero);
    })); 
    pair_m = std::get<0>(pair_m.sort(-1, true)); 

    const dim3 blk_ = BLOCKS(threads, dim_i, dim_j, max); 
    AT_DISPATCH_ALL_TYPES(pmu_i.scalar_type(), "EdgeSummation", ([&]
    {
        _EdgeSummation<scalar_t><<< blk_, threads >>>(
                 pmu_i.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(),
                pair_m.packed_accessor32<scalar_t, 3, torch::RestrictPtrTraits>(),
            node_feature.packed_accessor64<double, 2, torch::RestrictPtrTraits>(),  
                dim_i, dim_j, max);
    })); 

    pmu_i = pmu_i.to(torch::kFloat); 
    for (signed int i = (include_zero) ? 0 : 1; i < max; ++i)
    {
        std::stringstream x; 
        std::string name; 
        x << i; 
        x >> name; 
    
        std::tuple<torch::Tensor, torch::Tensor, torch::Tensor> id2; 
        id2 = torch::unique_dim(pair_m.index({i}), 0, false, true, false); 
        torch::Tensor clusters = std::get<0>(id2); 
        torch::Tensor revert   = std::get<1>(id2);

        unsigned int dim_ = clusters.size(0); 
        torch::Tensor pmu_u = torch::zeros({1, dim_, dim_j}, op);
        clusters = clusters.view({1, dim_, dim_i}); 
        
        const dim3 blk__ = BLOCKS(threads, dim_, dim_j, 1); 
        AT_DISPATCH_ALL_TYPES(pmu_u.scalar_type(), "EdgeSummation", ([&]
        {
            _EdgeSummation<scalar_t><<< blk__, threads >>>(
                     pmu_u.packed_accessor64<scalar_t, 3, torch::RestrictPtrTraits>(),
                  clusters.packed_accessor32<scalar_t, 3, torch::RestrictPtrTraits>(),
              node_feature.packed_accessor64<double, 2, torch::RestrictPtrTraits>(),  
                    dim_, dim_j, max);
        })); 

        output[name] = {
            clusters.index({0}), pmu_u.index({0}).to(torch::kFloat), 
            revert, pmu_i.index({i}).to(torch::kFloat)
        };  
    }

    return output; 
}


std::map<std::string, std::vector<torch::Tensor>> _node_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor node_feature, const bool include_zero)
{
    torch::Tensor pred, e_i; 
    const unsigned int x = edge_index.size(0); 
    const unsigned int j = edge_index.size(1); 
    if (x != 2 && j == 2){e_i = torch::transpose(edge_index, 0, 1);}
    else {e_i = edge_index;}

    e_i = e_i.index({0, torch::indexing::Slice()});
    pred = prediction.index({e_i}).clone(); 
    return _edge_aggregation(edge_index, pred, node_feature, include_zero); 
}


torch::Tensor _unique_aggregation(torch::Tensor cluster_map, torch::Tensor features)
{
    CHECK_INPUT(cluster_map); 
    CHECK_INPUT(features); 
    cluster_map = cluster_map.to(torch::kLong);
    const unsigned int n_nodes = cluster_map.size(0);
    const unsigned int ij_node = cluster_map.size(1); 
    const unsigned int n_feat  = features.size(1); 
    const unsigned int threads = 1024; 

    const torch::TensorOptions op = _MakeOp(features); 
    const torch::TensorOptions op_ = _MakeOp(cluster_map); 

    torch::Tensor output = torch::zeros({n_nodes, n_feat}, op); 
    const dim3 blk = BLOCKS(threads, n_nodes, n_feat); 

    torch::Tensor uniq = -1*torch::ones({n_nodes, ij_node}, op).to(torch::kLong); 
    const dim3 blk_ = BLOCKS(threads, n_nodes, ij_node, ij_node); 
    AT_DISPATCH_ALL_TYPES(features.scalar_type(), "unique_sum", ([&]
    {
   
        _fast_unique<scalar_t><<< blk_, threads >>>(
                   uniq.packed_accessor32<long, 2, torch::RestrictPtrTraits>(),
            cluster_map.packed_accessor32<long, 2, torch::RestrictPtrTraits>(), 
                n_nodes, ij_node, ij_node);

        _unique_sum<scalar_t><<< blk, threads >>>(
                 output.packed_accessor32<scalar_t, 2, torch::RestrictPtrTraits>(),
                   uniq.packed_accessor32<long, 2, torch::RestrictPtrTraits>(), 
               features.packed_accessor32<scalar_t, 2, torch::RestrictPtrTraits>(),
                n_nodes, ij_node, n_feat);
    })); 
    return output; 
}





// --------------------- Interfaces ------------------------ //
std::map<std::string, std::vector<torch::Tensor>> _polar_edge_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor pmu, const bool include_zero)
{
    torch::Tensor pmc = Transform::CUDA::PxPyPzE(pmu.to(torch::kFloat64)); 
    return _edge_aggregation(edge_index, prediction, pmc, include_zero); 
}


std::map<std::string, std::vector<torch::Tensor>> _polar_edge_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction,
                torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  
                const bool include_zero)
{
    std::vector<signed long> d = {-1, 1};
    std::vector<torch::Tensor> pmu = {pt.view(d), eta.view(d), phi.view(d), e.view(d)}; 
    torch::Tensor pmc = Transform::CUDA::PxPyPzE(torch::cat(pmu, -1).to(torch::kFloat64)); 
    return _edge_aggregation(edge_index, prediction, pmc, include_zero); 
}

std::map<std::string, std::vector<torch::Tensor>> _polar_node_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor pmu, const bool include_zero)
{
    torch::Tensor pmc = Transform::CUDA::PxPyPzE(pmu.to(torch::kFloat64)); 
    return _node_aggregation(edge_index, prediction, pmc, include_zero); 
}


std::map<std::string, std::vector<torch::Tensor>> _polar_node_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction,
                torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  
                const bool include_zero)
{
    std::vector<signed long> d = {-1, 1};
    std::vector<torch::Tensor> pmu = {pt.view(d), eta.view(d), phi.view(d), e.view(d)}; 
    torch::Tensor pmc = Transform::CUDA::PxPyPzE(torch::cat(pmu, -1).to(torch::kFloat64)); 
    return _node_aggregation(edge_index, prediction, pmc, include_zero); 
}

std::map<std::string, std::vector<torch::Tensor>> _cartesian_edge_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor pmc, const bool include_zero)
{
    return _edge_aggregation(edge_index, prediction, pmc, include_zero); 
}


std::map<std::string, std::vector<torch::Tensor>> _cartesian_edge_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction,
                torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  
                const bool include_zero)
{
    std::vector<signed long> d = {-1, 1};
    std::vector<torch::Tensor> pmc = {px.view(d), py.view(d), pz.view(d), e.view(d)}; 
    return _edge_aggregation(edge_index, prediction, torch::cat(pmc, -1), include_zero); 
}

std::map<std::string, std::vector<torch::Tensor>> _cartesian_node_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor pmc, const bool include_zero)
{
    return _node_aggregation(edge_index, prediction, pmc, include_zero); 
}

std::map<std::string, std::vector<torch::Tensor>> _cartesian_node_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction,
                torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  
                const bool include_zero)
{
    std::vector<signed long> d = {-1, 1};
    std::vector<torch::Tensor> pmc = {px.view(d), py.view(d), pz.view(d), e.view(d)}; 
    return _node_aggregation(edge_index, prediction, torch::cat(pmc, -1), include_zero); 
}

#endif
