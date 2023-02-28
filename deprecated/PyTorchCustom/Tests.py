import torch
import LorentzVector as LV
import math

from skhep.math.vectors import LorentzVector 

# Test Four vector
# pt, eta, phi, energy
v = [139742/1000, -1.49, -2, 326400/1000]

# ===== Test if device works ===== #
x_cuda = LV.ToPxPyPzE(v[0], v[1], v[2], v[3], "cuda")
x_cpu  = LV.ToPxPyPzE(v[0], v[1], v[2], v[3], "cpu")

assert str(x_cuda.device) == "cuda:0"
assert str(x_cpu.device) == "cpu"

# ===== Test if the implementation reproduces the px, py, pz, energy vector 
p = LorentzVector()
p.setptetaphie(v[0], v[1], v[2], v[3])

p_cpu = torch.round(x_cpu, decimals = 0).tolist()
try:
    assert p_cpu[0] == round(p.px)
    assert p_cpu[1] == round(p.py)
    assert p_cpu[2] == round(p.pz)
    assert p_cpu[3] == round(p.e)

except:
    print("----> Failed!")
    print(p_cpu)
    print([p.px, p.py, p.pz, p.e])

m_ref = round(p.mass)
assert torch.round(LV.MassFromPxPyPzE(x_cpu), decimals = 0) == m_ref
assert LV.MassFromPtEtaPhiE(torch.tensor(v, device = "cpu")).round(decimals = 0).tolist()[0][0] == float(m_ref)

v_s = []
v_s.append(v)
v_s.append(v)
v_s.append(v)
x_list = LV.ListToPxPyPzE(v_s, "cuda")

for i in x_list.round(decimals = 0).tolist():
    assert i[0] == round(p.px)
    assert i[1] == round(p.py)
    assert i[2] == round(p.pz)
    assert i[3] == round(p.e)

assert len(x_list.round(decimals = 0).tolist()) == len(v_s)

# This will be a performance test now
import time 

iterator = 1
V_L = []
for i in range(int(iterator)):
    V_L.append(v) 


print("==== Testing the speed between CPU and CUDA in calculating the invariant mass from PxPyPzE ====")
V_CUDA = LV.ListToPxPyPzE(V_L, "cuda")
V_CPU = LV.ListToPxPyPzE(V_L, "cpu")

t_s = time.time()
out_cpu = LV.MassFromPxPyPzE(V_CPU)
t_e = time.time()
t_cpu = t_e - t_s

t_s = time.time()
out_cpu = LV.MassFromPxPyPzE(V_CUDA)
t_e = time.time()
t_cuda = t_e - t_s

print("Time of CPU: ", t_cpu, " Time of CUDA: ", t_cuda)
print("Time/Vector of CPU: ", t_cpu/iterator, " Time/Vector of CUDA: ", t_cuda/iterator)

print("==== Testing the speed between CPU and CUDA in calculating the invariant mass from PtEtaPhiE ====")
t_s = time.time()
CPU = torch.tensor(V_L, device = "cpu")
t_e = time.time()
tl_cpu = t_e - t_s

t_s = time.time()
CUDA = torch.tensor(V_L, device = "cuda")
t_e = time.time()
tl_cuda = t_e - t_s


t_s = time.time()
out_cpu = LV.MassFromPtEtaPhiE(CPU)
t_e = time.time()
t_cpu = t_e - t_s

t_s = time.time()
out_cuda = LV.MassFromPtEtaPhiE(CUDA)
t_e = time.time()
t_cuda = t_e - t_s

print("Time of loading to memory ->  CPU: ", tl_cpu, " CUDA: ", tl_cuda)
print("Time of calculation ->  CPU: ", t_cpu, " CUDA: ", t_cuda)

cartesian = LV.ToPxPyPzE(v[0], v[1], v[2], v[3], "cpu"); 
rapidity = LV.TensorToPtEtaPhiE(cartesian)
for i, j in zip(v, rapidity.tolist()[0]):
    assert round(i, 3) == round(j, 3)









