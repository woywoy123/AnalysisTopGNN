#ifndef H_GRAPH_TENSOR 
#define H_GRAPH_CUDA
#include <torch/torch.h>

std::map<std::string, std::vector<torch::Tensor>> _edge_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor node_feature, const bool include_zero); 

std::map<std::string, std::vector<torch::Tensor>> _node_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor node_feature, const bool include_zero); 

torch::Tensor _unique_aggregation(torch::Tensor cluster_map, torch::Tensor features); 

std::map<std::string, std::vector<torch::Tensor>> _polar_edge_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor pmu, const bool include_zero); 

std::map<std::string, std::vector<torch::Tensor>> _polar_edge_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction,
                torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  
                const bool include_zero); 

std::map<std::string, std::vector<torch::Tensor>> _polar_node_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor pmu, const bool include_zero); 

std::map<std::string, std::vector<torch::Tensor>> _polar_node_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction,
                torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  
                const bool include_zero); 

std::map<std::string, std::vector<torch::Tensor>> _cartesian_edge_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor pmc, const bool include_zero); 

std::map<std::string, std::vector<torch::Tensor>> _cartesian_edge_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction,
                torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  
                const bool include_zero); 

std::map<std::string, std::vector<torch::Tensor>> _cartesian_node_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor pmc, const bool include_zero); 

std::map<std::string, std::vector<torch::Tensor>> _cartesian_node_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction,
                torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  
                const bool include_zero);
namespace Graph
{
    namespace CUDA
    {
        inline std::map<std::string, std::vector<torch::Tensor>> edge_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor node_feature, const bool include_zero)
        {
            return _edge_aggregation(edge_index, prediction, node_feature, include_zero); 

        }

        inline std::map<std::string, std::vector<torch::Tensor>> node_aggregation(
                torch::Tensor edge_index, torch::Tensor prediction, 
                torch::Tensor node_feature, const bool include_zero)
        {
            return _node_aggregation(edge_index, prediction, node_feature, include_zero); 
        }


        inline torch::Tensor unique_aggregation(torch::Tensor cluster_map, torch::Tensor features)
        {
            return _unique_aggregation(cluster_map, features); 
        }



        namespace Polar
        {
            inline std::map<std::string, std::vector<torch::Tensor>> edge_pmu(
                    torch::Tensor edge_index, torch::Tensor prediction, 
                    torch::Tensor pmu, const bool include_zero)
            {
                return _polar_edge_aggregation(edge_index, prediction, pmu, include_zero); 
            }

            inline std::map<std::string, std::vector<torch::Tensor>> edge_pmu(
                    torch::Tensor edge_index, torch::Tensor prediction, 
                    torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  
                    const bool include_zero)
            {
                return _polar_edge_aggregation(edge_index, prediction, pt, eta, phi, e, include_zero); 
            }

            inline std::map<std::string, std::vector<torch::Tensor>> node_pmu(
                    torch::Tensor edge_index, torch::Tensor prediction, 
                    torch::Tensor pmu, const bool include_zero)
            {
                return _polar_node_aggregation(edge_index, prediction, pmu, include_zero); 
            }

            inline std::map<std::string, std::vector<torch::Tensor>> node_pmu(
                    torch::Tensor edge_index, torch::Tensor prediction, 
                    torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e,  
                    const bool include_zero)
            {
                return _polar_node_aggregation(edge_index, prediction, pt, eta, phi, e, include_zero); 
            }
        }

        namespace Cartesian
        {

            inline std::map<std::string, std::vector<torch::Tensor>> edge_pmc(
                    torch::Tensor edge_index, torch::Tensor prediction, 
                    torch::Tensor pmc, const bool include_zero)
            {
                return _cartesian_edge_aggregation(edge_index, prediction, pmc, include_zero); 
            }

            inline std::map<std::string, std::vector<torch::Tensor>> edge_pmc(
                    torch::Tensor edge_index, torch::Tensor prediction, 
                    torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  
                    const bool include_zero)
            {
                return _cartesian_edge_aggregation(edge_index, prediction, px, py, pz, e, include_zero); 
            }

            inline std::map<std::string, std::vector<torch::Tensor>> node_pmc(
                    torch::Tensor edge_index, torch::Tensor prediction, 
                    torch::Tensor pmc, const bool include_zero)
            {
                return _cartesian_node_aggregation(edge_index, prediction, pmc, include_zero); 
            }

            inline std::map<std::string, std::vector<torch::Tensor>> node_pmc(
                    torch::Tensor edge_index, torch::Tensor prediction, 
                    torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e,  
                    const bool include_zero)
            {
                return _cartesian_node_aggregation(edge_index, prediction, px, py, pz, e, include_zero); 
            }
        }
    }
}


#endif
