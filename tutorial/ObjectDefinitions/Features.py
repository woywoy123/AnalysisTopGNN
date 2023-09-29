# node feature
def pt(a): return a.pt/1000
def eta(a): return a.eta
def phi(a): return a.phi
def energy(a): return a.e/1000
def Mass(a): return a.Mass/1000

# edge feature
def delta_pt(a, b): return abs(a.pt - b.pt)/1000
def delta_eta(a, b): return abs(a.eta - b.eta)
def delta_phi(a, b): return abs(a.phi - b.phi)
def delta_energy(a, b): return abs(a.e - b.e)/1000
def deltaR(a, b): return a.DeltaR(b)
def EdgeMass(a, b): return (a+b).Mass/1000

# graph feature
def nJets(ev): return len(ev.Out)

# graph truth
def signal(ev): return ev.signal
