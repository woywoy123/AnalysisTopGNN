

# ================== Kinematics ================ #
def pT(a):
    return float(a.pt)

def eta(a):
    return float(a.eta)

def phi(a):
    return float(a.phi)

def energy(a):
    return float(a.e)

def mass(a):
    return float(a.Mass)

def islepton(a):
    if a.Type == "el" or a.Type == "mu":
        return 1
    return 0

def charge(a):
    if hasattr(a, "charge"):
        return a.charge
    return 0

# ================== Truth ================ #
def Index(a):
    return float(a.Index)

def FromRes(a):
    try:
        return a.FromRes
    except:
        return float(0)

def FromTop(a):
    return 1

def ExpPx(a):
    return float(a.exp_Px)
