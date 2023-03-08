

# ================== Kinematics ================ #
def mu(ev):
    return float(ev.mu)

def met(ev):
    return float(ev.met)

def met_phi(ev):
    return float(ev.met_phi)

def pileup(ev):
    return float(ev.pileup)

def nJets(ev):
    return float(len(ev.Jets))

def nTruthJets(ev):
    return float(len(ev.TruthJets))

def nLeptons(ev):
    return len(ev.Leptons)


# ================== Truth ================ #
def mu_actual(ev):
    return float(ev.mu_actual)

def nTops(ev):
    return float(len(ev.Tops))

def SignalSample(ev):
    if len(ev.Tops) == 4:
        return 1
    else:
        return 0
