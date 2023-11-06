Graph
_____

An extension module which aims to reduce the need for writing redundant torch.scatter node and edge aggregation.
Each of the functions highlighted below have the same output type and structure.
These are outlined below:

- clusters: 
    The aggregated sum of the 4-vectors 

- unique_sum: 
    A tensor holding the unique cluster masses for the predicted topology. 
    This can be interpreted as the number of particles reconstructed in the particular graph. 
    For instance, if the event contains n-particles, with n-signature masses, then in an ideal situation n-particles would be contained within this tensor, rather than m-constituent particles (children). 

- reverse_sum: 
    A reverse mapping of unique_sum back to each graph node.

- node_sum: 
    A tensor holding the aggregated node's 4-vector.



.. py:module:: pyc.Graph.Base

        .. py:function:: unique_aggregation(clusters, node_features) -> torch.tensor

            An aggregation function used to sum node features without double summing any particular node pairs. 
            Given the complexity of the operation in nominal PyTorch, this function is exclusive to CUDA tensors.

            :params torch.tensor clusters: Cluster indices used to perform the summation over.
            :params torch.tensor node_features: The feature vector of the node to sum.


.. py:module:: pyc.Graph.Cartesian


        .. py:function:: edge(edge_index, prediction, px, py, pz, e, include_zero) -> dict
            :no-index:

            :params torch.tensor edge_index: The graph topology (this is usually known as the edge_index)
            :params torch.tensor prediction: The edge classification prediction of the neural network.
            :params torch.tensor px: The node's cartesian momentum component in the x-direction.
            :params torch.tensor py: The node's cartesian momentum component in the y-direction.
            :params torch.tensor pz: The node's cartesian momentum component in the z-direction.
            :params torch.tensor e: The node's energy.
            :params bool include_zero: Whether to include predictions where the MLP predicts 0. 

            :return dict[torch.tensor]: {
                                            clusters : torch.tensor, unique_sum : torch.tensor, 
                                            reverse_sum : torch.tensor, node_sum : torch.tensor}


        .. py:function:: edge(edge_index, prediction, pmc, include_zero) -> dict

            :params torch.tensor edge_index: The graph topology (this is usually known as the edge_index)
            :params torch.tensor prediction: The edge classification prediction of the neural network.
            :params torch.tensor pmc: A compact version of the particle's 4-vector.
            :params bool include_zero: Whether to include predictions where the MLP predicts 0. 

            :return dict[torch.tensor]: {
                                            clusters : torch.tensor, unique_sum : torch.tensor, 
                                            reverse_sum : torch.tensor, node_sum : torch.tensor}


        .. py:function:: node(edge_index, prediction, px, py, pz, e, include_zero) -> dict
            :no-index:

            :params torch.tensor edge_index: The graph topology (this is usually known as the edge_index)
            :params torch.tensor prediction: The node classification prediction of the neural network.
            :params torch.tensor px: The node's cartesian momentum component in the x-direction.
            :params torch.tensor py: The node's cartesian momentum component in the y-direction.
            :params torch.tensor pz: The node's cartesian momentum component in the z-direction.
            :params torch.tensor e: The node's energy.
            :params bool include_zero: Whether to include predictions where the MLP predicts 0. 

            :return dict[torch.tensor]: {
                                            clusters : torch.tensor, unique_sum : torch.tensor, 
                                            reverse_sum : torch.tensor, node_sum : torch.tensor}


        .. py:function:: node(edge_index, prediction, pmc, include_zero) -> dict

            :params torch.tensor edge_index: The graph topology (this is usually known as the edge_index)
            :params torch.tensor prediction: The node classification prediction of the neural network.
            :params torch.tensor pmc: A compact version of the particle's 4-vector.
            :params bool include_zero: Whether to include predictions where the MLP predicts 0. 

            :return dict[torch.tensor]: {
                                            clusters : torch.tensor, unique_sum : torch.tensor, 
                                            reverse_sum : torch.tensor, node_sum : torch.tensor}
 



.. py:module:: pyc.Graph.Polar


        .. py:function:: edge(edge_index, prediction, pt, eta, phi, e, include_zero) -> dict
            :no-index:

            :params torch.tensor edge_index: The graph topology (this is usually known as the edge_index)
            :params torch.tensor prediction: The edge classification prediction of the neural network.
            :params torch.tensor pt: The particle's transverse momentum
            :params torch.tensor eta: The rapidity of the particle
            :params torch.tensor phi: The azimuthal compnent of the particle node
            :params torch.tensor e: The node's energy.
            :params bool include_zero: Whether to include predictions where the MLP predicts 0. 

            :return dict[torch.tensor]: {
                                            clusters : torch.tensor, unique_sum : torch.tensor, 
                                            reverse_sum : torch.tensor, node_sum : torch.tensor}


        .. py:function:: edge(edge_index, prediction, pmu, include_zero) -> dict

            :params torch.tensor edge_index: The graph topology (this is usually known as the edge_index)
            :params torch.tensor prediction: The edge classification prediction of the neural network.
            :params torch.tensor pmu: A compact version of the particle's 4-vector.
            :params bool include_zero: Whether to include predictions where the MLP predicts 0. 

            :return dict[torch.tensor]: {
                                            clusters : torch.tensor, unique_sum : torch.tensor, 
                                            reverse_sum : torch.tensor, node_sum : torch.tensor}


        .. py:function:: node(edge_index, prediction, pt, eta, phi, e, include_zero) -> dict
            :no-index:

            :params torch.tensor edge_index: The graph topology (this is usually known as the edge_index)
            :params torch.tensor prediction: The node classification prediction of the neural network.
            :params torch.tensor pt: The particle's transverse momentum
            :params torch.tensor eta: The rapidity of the particle
            :params torch.tensor phi: The azimuthal compnent of the particle node
            :params torch.tensor e: The node's energy.
            :params bool include_zero: Whether to include predictions where the MLP predicts 0. 

            :return dict[torch.tensor]: {
                                            clusters : torch.tensor, unique_sum : torch.tensor, 
                                            reverse_sum : torch.tensor, node_sum : torch.tensor}


        .. py:function:: node(edge_index, prediction, pmu, include_zero) -> dict

            :params torch.tensor edge_index: The graph topology (this is usually known as the edge_index)
            :params torch.tensor prediction: The node classification prediction of the neural network.
            :params torch.tensor pmu: A compact version of the particle's 4-vector.
            :params bool include_zero: Whether to include predictions where the MLP predicts 0. 

            :return dict[torch.tensor]: {
                                            clusters : torch.tensor, unique_sum : torch.tensor, 
                                            reverse_sum : torch.tensor, node_sum : torch.tensor}
 



