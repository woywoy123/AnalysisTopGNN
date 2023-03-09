import math
import PyC.Transform.Floats as Tf

# ================== Kinematics ================ #
def delta_pT(a, b):
    return float(a.pt - b.pt)

def delta_eta(a, b):
    return float(a.eta - b.eta)

def delta_phi(a, b):
    return float(a.phi - b.phi)

def delta_energy(a, b):
    return float(a.energy - b.energy)

def delta_R(a, b):
    return float(a.DeltaR(b))

def mass(a, b):
    m = a.CalculateMass([a, b])
    return float(m.Mass_GeV)


# ================== Truth ================ #
def Index(a, b):
    if a.index == b.index:
        return float(1)
    return float(0)

def Expected_Px(a, b):
    if hasattr(a, "exp_Px") == False:
        a.exp_Px = 0
    
    if a.index != b.index:
        return 
    a.exp_Px += Tf.Px(b.pt, b.phi)
