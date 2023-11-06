from AnalysisG.Templates import ParticleTemplate
import math

def test_particle_template_assign_var():
    x = ParticleTemplate()
    x.px = "str"
    x.px = 0


def test_particle_template():
    def Px(pt, phi): return pt * math.cos(phi)
    def Py(pt, phi): return pt * math.sin(phi)
    def Pz(pt, eta): return pt * math.sinh(eta)

    class Particle(ParticleTemplate):
        def __init__(self):
            ParticleTemplate.__init__(self)

    x = ParticleTemplate()
    y = ParticleTemplate()
    assert x.hash == y.hash
    assert len(x.hash) == 18

    # Testing setter function
    vals = [207050.75, 0.5622375011444092, 2.262759208679199, 296197.3125]
    val = [Px(vals[0], vals[2]), Py(vals[0], vals[2]), Pz(vals[0], vals[1]), vals[3]]

    t = Particle()
    t.pt = vals[0]
    t.eta = vals[1]
    t.phi = vals[2]
    t.e = vals[3]

    # Assert Setter and Getter Functions
    assert t.pt == vals[0]
    assert t.eta == vals[1]
    assert t.phi == vals[2]
    assert t.e == vals[3]

    # Assert Getter Function with transform to cartesian
    assert t.px == val[0]
    assert t.py == val[1]
    assert t.pz == val[2]

    # Assert the reverse transformation to polar
    t_ = Particle()
    t_.px = val[0]
    t_.py = val[1]
    t_.pz = val[2]
    t_.e = val[3]

    # Assert the Setter of Cartesian
    assert t_.px == val[0]
    assert t_.py == val[1]
    assert t_.pz == val[2]
    assert t_.e == val[3]

    assert t_.pt == vals[0]
    assert t_.eta == vals[1]
    assert t_.phi == vals[2]
    assert t_.e == vals[3]

    # Assert Arithmitic
    t += t_
    assert t.px == val[0] * 2
    assert t.py == val[1] * 2
    assert t.pz == val[2] * 2
    assert t.e == val[3] * 2

    # Bulk Summation
    x = [t_, t_, t_, t_, t_]
    l = len(x)
    k = sum(x)
    assert k.px == t_.px * l
    assert k.py == t_.py * l
    assert k.pz == t_.pz * l
    assert k.e == t_.e * l

    assert k.px == t.px * l / 2
    assert k.py == t.py * l / 2
    assert k.pz == t.pz * l / 2
    assert k.e == t.e * l / 2

    # Check hashing
    assert k.hash != t.hash
    assert t_.hash != t.hash

    # Check if equal
    assert k == k
    assert k != t_
    assert t_ != t

    x = [t, t_, t, t_]
    assert len(set(x)) == 2
    assert x.index(t_) == 1

    # Test the pdgid setter
    t.pdgid = -11
    t.charge = 1

    # Getter
    assert t.pdgid == -11
    assert t.charge == 1
    assert t.symbol == "e"
    assert t.is_lep == True
    assert t.is_nu == False
    assert t.is_add == False

    t.nudef = []
    t.lepdef = []
    assert t.is_lep == False
    assert t.is_nu == False
    assert t.is_add == True

    tp = Particle()
    tp.px = val[0]
    tp.py = val[1]
    tp.pz = val[2]
    tp.e = val[3]

    tc1 = Particle()
    tc1.px = val[0] * 0.25
    tc1.py = val[1] * 0.25
    tc1.pz = val[2] * 0.25
    tc1.e = val[3] * 0.25

    tc2 = Particle()
    tc2.px = val[0] * 0.4
    tc2.py = val[1] * 0.4
    tc2.pz = val[2] * 0.4
    tc2.e = val[3] * 0.4

    tc3 = Particle()
    tc3.px = val[0] * 0.35
    tc3.py = val[1] * 0.35
    tc3.pz = val[2] * 0.35
    tc3.e = val[3] * 0.35

    tp.Children += [tc1]
    tp.Children += [tc2]
    tp.Children.append(tc3)
    tp.Children.append(tc3)
    tc1.Parent.append(tp)
    tc1.Parent.append(tp)
    tc3.Parent.append(tp)

    assert len(tp.Children) == 3
    assert len(tc1.Parent) == 1

    tp.Children[0].px = val[0]
    assert tc1.px == val[0]
    assert tc1 in tp.Children


def test_particle_template_assign():
    class Particle(ParticleTemplate):
        def __init__(self):
            ParticleTemplate.__init__(self)
            self.index = "index"
            self.px = "px"
            self.py = "py"
            self.pz = "pz"
            self.pt = "pt"
            self.eta = "eta"
            self.phi = "phi"
            self.e = "e"
            self.Mass = "Mass"
            self.pdgid = "pdgid"
            self.charge = "charge"
            self.somevar = "somevar"

    class ParticleDerived(Particle):
        def __init__(self):
            Particle.__init__(self)
            self.somevar2 = "somevar2"
            self.Another = []

    P = Particle()
    kdic = P.__getleaves__()
    assert kdic["index"] == "index"
    assert kdic["px"] == "px"
    assert kdic["py"] == "py"
    assert kdic["pz"] == "pz"
    assert kdic["pt"] == "pt"
    assert kdic["eta"] == "eta"
    assert kdic["phi"] == "phi"
    assert kdic["e"] == "e"
    assert kdic["Mass"] == "Mass"
    assert kdic["pdgid"] == "pdgid"
    assert kdic["charge"] == "charge"
    assert kdic["somevar"] == "somevar"

    P2 = ParticleDerived()
    kdic = P2.__getleaves__()
    assert kdic["index"] == "index"
    assert kdic["px"] == "px"
    assert kdic["py"] == "py"
    assert kdic["pz"] == "pz"
    assert kdic["pt"] == "pt"
    assert kdic["eta"] == "eta"
    assert kdic["phi"] == "phi"
    assert kdic["e"] == "e"
    assert kdic["Mass"] == "Mass"
    assert kdic["pdgid"] == "pdgid"
    assert kdic["charge"] == "charge"
    assert kdic["somevar"] == "somevar"
    assert kdic["somevar2"] == "somevar2"

if __name__ == "__main__":
    test_particle_template_assign_var()
    test_particle_template()
    test_particle_template_assign()


