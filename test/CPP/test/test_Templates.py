import math

def test_particle_template():

    from AnalysisG.Templates import ParticleTemplate 
    
    def Px(pt, phi): return pt*math.cos(phi)
    def Py(pt, phi): return pt*math.sin(phi)
    def Pz(pt, eta): return pt*math.sinh(eta)

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
    assert t.px == val[0]*2
    assert t.py == val[1]*2
    assert t.pz == val[2]*2
    assert t.e == val[3]*2
   
    # Bulk Summation
    x = [t_, t_, t_, t_, t_]
    l = len(x)
    k = sum(x)
    assert k.px == t_.px*l
    assert k.py == t_.py*l
    assert k.pz == t_.pz*l
    assert k.e  == t_.e*l

    assert k.px == t.px*l/2
    assert k.py == t.py*l/2
    assert k.pz == t.pz*l/2
    assert k.e  == t.e*l/2
    
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
    tc1.px = val[0]*0.25
    tc1.py = val[1]*0.25
    tc1.pz = val[2]*0.25
    tc1.e = val[3]*0.25
 
    tc2 = Particle()
    tc2.px = val[0]*0.4
    tc2.py = val[1]*0.4
    tc2.pz = val[2]*0.4
    tc2.e = val[3]*0.4
 
    tc3 = Particle()
    tc3.px = val[0]*0.35
    tc3.py = val[1]*0.35
    tc3.pz = val[2]*0.35
    tc3.e = val[3]*0.35
    
    tp.Children.append(tc1)
    tp.Children.append(tc2)
    tp.Children.append(tc3)
    tc1.Parent.append(tp)
    tc2.Parent.append(tp)
    tc3.Parent.append(tp)
    
    assert len(tp.Children) == 3
    assert len(tc1.Parent) == 1 
    
    tp.Children[0].px = val[0] 
    assert tc1.px == val[0]
    assert tc1 in tp.Children
    
    # Test for memory leak
    for i in range(100000):
        t_ = Particle()
        t_.px = val[0]
        t_.py = val[1]
        t_.pz = val[2]
        t_.e = val[3]

        t = Particle()
        t.px = val[0]
        t.py = val[1]
        t.pz = val[2]
        t.e = val[3]
        t_.Children.append(t)

def test_particle_template_assign():
    from AnalysisG.Templates import ParticleTemplate 

    class Particle(ParticleTemplate):
        def __init__(self):
            ParticleTemplate.__init__(self)
            self.index  =  "index"
            self.px     =  "px"    
            self.py     =  "py"
            self.pz     =  "pz"
            self.pt     =  "pt"
            self.eta    =  "eta"
            self.phi    =  "phi"
            self.e      =  "e"
            self.Mass   =  "Mass"
            self.pdgid  =  "pdgid"
            self.charge =  "charge"
            self.somevar = "somevar"
    
    class ParticleDerived(Particle):
        def __init__(self):
            Particle.__init__(self)
            self.somevar2 = "somevar2"
    
    P = Particle()
    kdic = P.__interpret__
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
    kdic = P2.__interpret__
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

def test_event_template():
    root1 = "./samples/sample1/smpl1.root"
    from AnalysisG.Templates import EventTemplate

    class Event(EventTemplate):
        def __init__(self):
            EventTemplate.__init__(self)
            self.index = "eventNumber"
            self.weight = "weight_mc"
            self.Trees = ["nominal"]
            self.met_phi = "met_phi"
            self.CommitHash = "..."
            self.Deprecated = False
    
    ev = Event()
    val = ev.__interpret__
    assert "eventNumber" in val["event"]["index"]
    assert "weight_mc" in val["event"]["weight"]
    assert "met_phi" in val["event"]["met_phi"]
    assert "CommitHash" not in val["event"]
    assert "Deprecated" not in val["event"]
    assert "Trees" not in val["event"]
    assert "Branches" not in val["event"]
    assert "Leaves" not in val["event"]
    assert "Objects" not in val["event"]
    
    ev.index = 0
    ev.hash = root1
    assert len(ev.hash) == 18

    ev2 = Event()
    ev2.index = 1
    ev2.hash = root1
    assert ev2 != ev


def test_event_particle_template():
    from AnalysisG.Templates import EventTemplate
    from AnalysisG.Templates import ParticleTemplate
    
    class Particle(ParticleTemplate):
        def __init__(self):
            ParticleTemplate.__init__(self)
            self.pt = self.Type + "_pt"
            self.eta = self.Type + "_eta"
            self.phi = self.Type + "_phi"
            self.e = self.Type + "_e"
    
    class Top(Particle):
        
        def __init__(self):
            self.Type = "top"
            Particle.__init__(self) 
             
    class Children(Particle):
        
        def __init__(self):
            self.Type = "children"
            Particle.__init__(self) 
             
    class Event(EventTemplate):
        def __init__(self):
            EventTemplate.__init__(self)
            self.Objects = {
                    "top" : Top, 
                    "Children" : Children()
            }
            self.index = "eventNumber"
            self.weight = "weight_mc"
            self.Trees = ["nominal"]
            self.met_phi = "met_phi"
            self.CommitHash = "..."
            self.Deprecated = False
    
    ev = Event()
    vals = ev.__interpret__
    assert "eventNumber" == vals["event"]["index"]
    assert "weight_mc" == vals["event"]["weight"]
    assert "met_phi" == vals["event"]["met_phi"]

    assert "top_pt" == vals["top"]["pt"]
    assert "top_phi" == vals["top"]["phi"]
    assert "top_eta" == vals["top"]["eta"]
    assert "top_e" == vals["top"]["e"]

    assert "children_pt" == vals["Children"]["pt"]
    assert "children_phi" == vals["Children"]["phi"]
    assert "children_eta" == vals["Children"]["eta"]
    assert "children_e" == vals["Children"]["e"]

    assert len(ev.Leaves) == 22

def test_event_particle_template_populate():
    root1 = "./samples/sample1/smpl1.root"
    from AnalysisG.IO import UpROOT
    from AnalysisG.Templates import EventTemplate
    from AnalysisG.Templates import ParticleTemplate
    
    class Particle(ParticleTemplate):
        def __init__(self):
            ParticleTemplate.__init__(self)
            self.pt = self.Type + "_pt"
            self.eta = self.Type + "_eta"
            self.phi = self.Type + "_phi"
            self.e = self.Type + "_e"
 
    class Top(Particle):
        
        def __init__(self):
            self.Type = "top"
            Particle.__init__(self) 

    class Children(Particle):
        
        def __init__(self):
            self.Type = "children"
            Particle.__init__(self) 
            
    class Event(EventTemplate):
        def __init__(self):
            EventTemplate.__init__(self)
            self.Objects = {
                    "top" : Top(), 
                    "Children" : Children,  
            }
            self.index = "eventNumber"
            self.weight = "weight_mc"
            self.Trees = ["nominal", "truth"]
            self.met_phi = "met_phi"
            self.CommitHash = "..."
            self.Deprecated = False

    ev = Event()
    ev.__interpret__
    
    io = UpROOT(root1)
    io.Trees = ev.Trees
    io.Leaves = ev.Leaves

    lst, lstc, lstt = [], [], []
    n_children = 0
    n_tops = 0
    for i in io:
        x = ev.clone
        x.__compiler__(i)
        assert len([k.Tree for k in x.Trees]) == 2
        assert sum([sum([k.index >= 0, k.weight != 0]) for k in x.Trees]) == 4
        
        t1, t2 = x.Trees
        t1.hash, t2.hash = root1, root1
        
        n_children += len(x.Children)
        n_tops += len(x.top)

        lst.append(x)
        lstc += [t for t in x.Children.values()]

        lstt += [t for t in x.top.values()]
        assert len(x.hash) == 18
        assert t1 != t2
    
    n_events = len(lst)
    assert n_events != 0
    assert n_children != 0
    assert n_tops != 0
    assert n_events == len(set(lst))
    assert n_children == len(set(lstc))
    assert n_tops == len(set(lstt))

def test_root_tracer():
    pass


if __name__ == "__main__":
    test_particle_template()
    test_particle_template_assign()
    test_event_template()
    test_event_particle_template()
    test_event_particle_template_populate() 
    test_root_tracer()

    pass
