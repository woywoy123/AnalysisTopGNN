def eta(a):
    return float(a.eta)

def phi(a):
    return float(a.phi)

def eta(a):
    return float(a.eta)

def energy(a):
    return float(a.e)

def pT(a):
    return float(a.pt)

def charge(a):
    return float(a.charge)

def mass(a):
    return float(a.Mass)

# ---- Truth ---- #
def FromRes(a):
    if "FromRes" in a.__dict__:
        return float(a.FromRes)
    return 0

def FromTop(a):
    return 1 if len(a.Parent) > 0 else 1

def pdgid(a):
    return float(a.pdgid)

def islepton(a):
    return 1 if abs(a.pdgid) in [11, 13, 15] else 0

def isneutrino(a):
    return 1 if abs(a.pdgid) in [12, 14, 16] else 0


