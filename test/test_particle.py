from AnalysisTopGNN.Templates import ParticleTemplate

class Particle(ParticleTemplate):

    def __init__(self):
        ParticleTemplate.__init__(self)

def test_particle_vector():
    # Pt, Eta, Phi, E
    t = Particle()
    t.pt, t.eta, t.phi, t.e = 207050.75, 0.5622375011444092, 2.262759208679199, 296197.3125

    _c1 = Particle()
    _c1.pt, _c1.eta, _c1.phi, _c1.e = 151159.578125, 0.7653300762176514, 2.182579517364502, 197688.265625
 
    _c2 = Particle()
    _c2.pt, _c2.eta, _c2.phi, _c2.e = 44224.68359375, -0.3411894738674164, -2.8015549182891846, 46823.85546875
   
    _c3 = Particle()
    _c3.pt, _c3.eta, _c3.phi, _c3.e = 50563.35546875, 0.2102622389793396, 1.6420748233795166, 51685.19140625

    px = sum([_c1.px, _c2.px, _c3.px])
    py = sum([_c1.py, _c2.py, _c3.py])
    pz = sum([_c1.pz, _c2.pz, _c3.pz])
    e  = sum([_c1.e , _c2.e , _c3.e ])

    # test if the vector calculation is approximately correct.
    assert abs(t.px - px)/abs(t.px) < 1e-6
    assert abs(t.py - py)/abs(t.py) < 1e-6
    assert abs(t.pz - pz)/abs(t.pz) < 1e-6
    assert abs(t.e  - e)/abs(t.e )  < 1e-6
    
    # test magic function.
    _t = sum([_c3, _c1, _c2])
    assert abs(_t.px - px) < 1e-6
    assert abs(_t.py - py) < 1e-6
    assert abs(_t.pz - pz) < 1e-6
    assert abs(_t.e - e) < 1e-6
    
    # test the polar calculation 
    assert abs(t.pt  - _t.pt )/abs(t.pt ) < 1e-6 
    assert abs(t.eta - _t.eta)/abs(t.eta) < 1e-6 
    assert abs(t.phi - _t.phi)/abs(t.phi) < 1e-6 
    assert abs(t.e   - _t.e  )/abs(t.e  ) < 1e-6 
    assert abs(t.Mass   - _t.Mass  )/abs(t.Mass) < 1e-6 
    
    # test setter functions 
    _t.pt, _t.eta, _t.phi, _t.e = t.pt, t.eta, t.phi, t.e
    assert abs(_t.pt - t.pt)/t.pt < 1e-7
    assert abs(_t.eta - t.eta) < 1e-7
    assert abs(_t.phi - t.phi) < 1e-7
    assert abs(_t.e - t.e) < 1e-7

    _t.px, _t.py, _t.pz, _t.e = t.px, t.py, t.pz, t.e
    assert abs(_t.px - t.px)/abs(t.px) < 1e-7
    assert abs(_t.py - t.py)/abs(t.py) < 1e-7
    assert abs(_t.pz - t.pz)/abs(t.pz) < 1e-7
    assert abs(_t.e - t.e)/abs(t.e) < 1e-7

def test_particle_hashing():
    t = Particle()
    t.pt, t.eta, t.phi, t.e = 207050.75, 0.5622375011444092, 2.262759208679199, 296197.3125
    t.pdgid = 1

    z = Particle()
    z.pt, z.eta, z.phi, z.e = 207050.75, 0.5622375011444092, 2.262759208679199, 296197.3125
    z.pdgid = 1
    
    assert t == z

    t = Particle()
    t.pt, t.eta, t.phi, t.e = 207050.75, 0.5622375011444092, 2.262759208679199, 296197.
    t.pdgid = 3

    z = Particle()
    z.pt, z.eta, z.phi, z.e = 207050.75, 0.5622375011444092, 2.262759208679199, 296197.3125
    z.pdgid = 1
    
    assert z in [t, z] 
    assert [t, z].index(z) == 1
    
    x = list(set([t, t, t, t, t, t, z]))
    assert len(x) == 2
    assert t in x
    assert z in x
    assert x[0].pt == t.pt


test_particle_vector()
