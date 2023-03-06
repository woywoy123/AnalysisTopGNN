import torch
#from PathNetOptimizer import *

#AdjM = PathCombinatorial(3, 3, "cpu")
#TestVect = torch.Tensor([[1, 1, 1, 1], [2, 2, 2, 2], [3, 3, 3, 3]], device = "cpu")
#print(AdjM)
#print(TestVect)
#
#for i in AdjM:
#    print("-> ", i)
#
#    print("-----")
#    print(TestVect[i == 1])
#
#print(PathVector(AdjM, TestVect))

#
#from PathNetOptimizerCUDA import *
# from PathNetOptimizerCUDA import PathVectorCUDA, PathMassCUDA, IncomingEdgeVectorCUDA, IncomingEdgeMassCUDA
# from PathNetOptimizerCPU import CombinatorialCPU
#
#
# n = 5
# AdjM = CombinatorialCPU(n, n, "cpu")
# TestVect = torch.tensor([[i+1, i+1, i+1, i+1] for i in range(n)], device = "cpu")
# new = torch.cat([TestVect]*n, dim = 0)
# index = torch.tensor([[i] for i in range(n) for j in range(n)], device = "cpu")
#
# print(AdjM)
# print(new)
# print(index)
#
# import time
# ts_0 = time.time()
# l = []
# for i in range(n):
#     for j in AdjM:
#         l.append(sum(new[i*len(j):(i+1)*len(j)][j == 1]).tolist())
# te_0 = time.time()
# print("------")
#
# ts_1 = time.time()
# v = IncomingEdgeVectorCUDA(AdjM.to(device = "cuda"), new.to(device = "cuda"), index.to(device = "cuda"))
# te_1 = time.time()
#
# print("cpu", te_0 - ts_0, "cuda", te_1 - ts_1)
# for j, i, z in zip(torch.as_tensor(l, dtype=float), v[0], v[1]):
#     j, i = j.tolist(), i.tolist()
#     print(j, i)
#     assert i == j
#
#
# exit()
# from PathNetOptimizerCUDA import *
import time

def Combinatorial(n, k, msk, t = [], v = [], num = 0):

    if n == 0:
        t += [torch.tensor(num).unsqueeze(-1).bitwise_and(msk).ne(0).to(dtype = int).tolist()]
        v += [num]
        return t, v

    if n-1 >= k:
        t, v = Combinatorial(n-1, k, msk, t, v, num)
    if k > 0:
        t, v = Combinatorial(n-1, k -1, msk, t, v, num | ( 1 << (n-1)))

    return t, v

def CombinatorialSlow(n):
    import itertools
    checked_perms = set()
    for combination in itertools.combinations_with_replacement([0, 1], n):
        for perm in itertools.permutations(combination):
            if perm in checked_perms:
                continue
            if (1 - i for i in perm) in checked_perms:
                continue
            checked_perms.add(perm)


nodes = 6
mx = 6


# ts_c = time.time()
# K = PathCombinatorial(nodes, mx)
# te_c = time.time()
# print(K)
msk = torch.pow(2, torch.arange(nodes))
ts = time.time()
p = []
for i in range(mx+1):
    out, num = Combinatorial(nodes, i, msk)
    p += out
print(p)
te = time.time()
print(te-ts)

ts = time.time()
CombinatorialSlow(nodes)
te = time.time()
print(te-ts)

# print(len(K), len(out))
# print("CUDA", te_c - ts_c, "CPU", te - ts)
# K = K.tolist()
# for i in out:
#     if i not in K:
#         print("+>", i)
#
# for i in K:
#     if i not in out:
#         print("->", i)
