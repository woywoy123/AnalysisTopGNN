import torch
import PyC.Operators.Tensors as T
import PyC.Operators.CUDA as C
from Checks import * 
from time import time 

device = "cuda"
Matrix = [[i*j for i in range(100)] for j in range(10)]
T_matrix = torch.tensor(Matrix, device = device, dtype = torch.float64)

t1 = time()
exp = T.Dot(T_matrix, T_matrix)
diff1 = time() - t1 

t1 = time()
Exp = C.Dot(T_matrix, T_matrix)
diff2 = time() - t1

AssertEquivalenceRecursive(Exp.tolist(), exp.tolist())
print("--- Testing Performance Between C++ and CUDA of DOT ---")
print("Speed Factor (> 1 is better): ", diff1 / diff2)

Matrix = [[i for i in range(3)] for j in range(100000)]
T1_matrix = torch.tensor(Matrix, device = device, dtype = torch.float64)

Matrix = [[j*i + 1 for i in range(3)] for j in range(100000)]
T2_matrix = torch.tensor(Matrix, device = device, dtype = torch.float64)

t1 = time()
exp = T.CosTheta(T1_matrix, T2_matrix)
diff1 = time() - t1 

t1 = time()
Exp = C.CosTheta(T1_matrix, T2_matrix)
diff2 = time() - t1
print(diff1, diff2)

print(AssertEquivalenceRecursive(Exp.tolist(), exp.tolist()))
print("--- Testing Performance Between C++ and CUDA of CosTheta ---")
print("Speed Factor (> 1 is better): ", diff1 / diff2)

import math
Matrix = [[math.pi/(j+1) for i in range(1)] for j in range(100000)]
T1_matrix = torch.tensor(Matrix, device = device, dtype = torch.float64)

t1 = time()
exp = T.Rx(T1_matrix)
diff1 = time() - t1 

t1 = time()
Exp = C.Rx(T1_matrix)
diff2 = time() - t1

print(diff1, diff2)
print(AssertEquivalenceRecursive(Exp.tolist(), exp.tolist()))
print("--- Testing Performance Between C++ and CUDA of Rx ---")
print("Speed Factor (> 1 is better): ", diff1 / diff2)

t1 = time()
exp = T.Ry(T1_matrix)
diff1 = time() - t1 

t1 = time()
Exp = C.Ry(T1_matrix)
diff2 = time() - t1

print(AssertEquivalenceRecursive(Exp.tolist(), exp.tolist()))
print("--- Testing Performance Between C++ and CUDA of Ry ---")
print("Speed Factor (> 1 is better): ", diff1 / diff2)

t1 = time()
exp = T.Rz(T1_matrix)
diff1 = time() - t1 

t1 = time()
Exp = C.Rz(T1_matrix)
diff2 = time() - t1

print(AssertEquivalenceRecursive(Exp.tolist(), exp.tolist()))
print("--- Testing Performance Between C++ and CUDA of Rz ---")
print("Speed Factor (> 1 is better): ", diff1 / diff2)

T1_matrix = torch.tensor([[i for i in range(3)] for j in range(1)], device = "cuda", dtype = torch.float64)
x = C.Rz(T1_matrix)
y = torch.tensor([[[k for i in range(1)] for k in range(3)] for t in range(1)], device = "cuda", dtype = torch.float64)

t1 = time()
c = torch.matmul(x, y)
diff1 = time() - t1 

t1 = time()
l = C.Mul(x, y)
diff2 = time() - t1

print(AssertEquivalenceRecursive(c.tolist(), l.tolist()))
print("--- Testing Performance Between C++ and CUDA of Mul ---")
print("Speed Factor (> 1 is better): ", diff1 / diff2)

y = torch.tensor([[[k/(1+t) for i in range(3)] for k in range(3)] for t in range(100)], device = "cuda", dtype = torch.float64)
x = torch.tensor([[[i*k for i in range(3)] for k in range(3)] for t in range(100)], device = "cuda", dtype = torch.float64)
diff = [[], []]
for t in range(10000):
    t1 = time()
    c = torch.matmul(x, y)
    t2 = time()
    diff1 = t2 - t1 
    diff[0].append(diff1)
    
    t1 = time()
    l = C.Mul(x, y)
    t2 = time()
    diff2 = t2 - t1
    diff[1].append(diff2)

print(AssertEquivalenceRecursive(c.tolist(), l.tolist()))
print("--- Testing Performance Between C++ and CUDA of MatMul ---")
print("Speed Factor (> 1 is better): ", (sum(diff[0])) / sum(diff[1]))

m = torch.tensor([[[1/(i+1), 4, 7/(i+1)], [3, i, 5], [-1/(i+1), 9, 1]] for i in range(10000)], dtype = torch.float64, device = "cuda")
diff = [[], []]
for t in range(10000):
    t1 = time()
    c = torch.inverse(m)
    t2 = time()
    diff1 = t2 - t1 
    diff[0].append(diff1)
    
    t1 = time()
    l = C.Inv(m)
    t2 = time()
    diff2 = t2 - t1
    diff[1].append(diff2)
print(AssertEquivalenceRecursive(c.tolist(), l.tolist()))
print("--- Testing Performance Between C++ and CUDA of Inverse ---")
print("Speed Factor (> 1 is better): ", (sum(diff[0])) / sum(diff[1]))

