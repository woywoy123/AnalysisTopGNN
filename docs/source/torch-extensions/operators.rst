Operators
_________

This module of the extension package is reserved for operators that are commonly associated with matrix manipulation. 
Most of the discussed functions were designed with CUDA in mind however, for completeness C++ wrappers are also written in native torch. 
The native torch implementations allow the user to leverage these operators in a non-CUDA environment.

.. py:function:: pyc.Operators.Dot(vec1, vec2) -> torch.tensor (Entries x 1)
        
    Takes the Dot product of two tensors and sums the entries along the last dimension.
    The output of this operator will yield a tensor with dimensionality (n - entries, 1)

    :params torch.tensor vec1: Expects a tensor with dimensionality N x Features.
    :params torch.tensor vec2: Expects a tensor with dimensionality N x (Features <= vec1).

.. py:function:: pyc.Operators.Mul(vec1, vec2) -> torch.tensor
        
    Takes the dot product of the row vector from vec1 and column from vec2.
    The output tensor will be of dimensionality (n - entries, nodes, features of vec2)

    :params torch.tensor vec1: Expects a tensor with dimensionality n x nodes x features.
    :params torch.tensor vec2: Expects a tensor with dimensionality n x nodes x (features <= vec1).


