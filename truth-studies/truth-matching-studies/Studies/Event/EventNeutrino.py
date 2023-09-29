from AnalysisG.Templates import SelectionTemplate

class EventNuNuSolutions(SelectionTemplate):
    
    def __init__(self):
        SelectionTemplate.__init__(self)
        self.NuNuSolutions = {"No-Rotation" : [], "Rotation" : []}
        self.TopMassDelta = {"No-Rotation" : {}, "Rotation" : {}}
        self.Truth_MET_NuNu_Delta = {"No-Rotation" : [], "Rotation" : []}
        self.Truth_MET_xy_Delta = {
                "No-Rotation-x" : [], "No-Rotation-y" : [],  
                "Rotation-x" : [], "Rotation-y" : []
        }
   
    def Selection(self, event):
        if sum([1 for i in event.Tops if i.LeptonicDecay]) != 2: return False
        t1, t2 = [i for i in event.Tops if i.LeptonicDecay]
        c1, c2 = t1.Children, t2.Children
        if len(c1) != 3 or len(c2) != 3: return False
        if len([1 for c in c1 if c.is_b]) == 0: return False
        if len([1 for c in c2 if c.is_b]) == 0: return False
        return True

    def Rotation(self, particle, angle):
        import math
        px_, py_, pz_ = particle.px, particle.py, particle.pz
        py = py_*math.cos(angle) - pz_*math.sin(angle)
        pz = py_*math.sin(angle) + pz_*math.cos(angle)
        particle.px = px_
        particle.py = py
        particle.pz = pz
        particle.pt = None
        return particle 

    def RotationP(self, particle, angle):
        return self.Rotation(particle, -angle)

    def Strategy(self, event):
        import math
        def Nu(top): return [i for i in top.Children if abs(i.pdgid) in [12, 14, 16]][0]
        def Lep(top): return [i for i in top.Children if abs(i.pdgid) in [11, 13, 15]][0]
        def BQuark(top): return [i for i in top.Children if i.is_b][0]

        t1, t2 = [i for i in event.Tops if i.LeptonicDecay]
        nu1, nu2 = Nu(t1), Nu(t2)
        lep1, lep2 = Lep(t1), Lep(t2)
        b1, b2 = BQuark(t1), BQuark(t2)
        met, phi = event.met, event.met_phi
        met_x, met_y = self.Px(event.met, event.met_phi), self.Py(event.met, event.met_phi),  
  
        # ====================== Not Rotated ========================== #
        t_Mass = (t1.Mass + t2.Mass)/2
        W_Mass = ((nu1 + lep1).Mass + (nu2 + lep2).Mass)/2
        sols = self.NuNu(b1, b2, lep1, lep2, event, t_Mass, W_Mass)

        n_sols, nu_sum = len(sols), (nu1 + nu2)
        self.NuNuSolutions["No-Rotation"].append(n_sols)
        self.Truth_MET_NuNu_Delta["No-Rotation"] += [abs(nu_sum.pt/met)]
        self.Truth_MET_xy_Delta["No-Rotation-x"] += [(met_x - nu_sum.px)/1000]
        self.Truth_MET_xy_Delta["No-Rotation-y"] += [(met_y - nu_sum.py)/1000]

        if n_sols not in self.TopMassDelta["No-Rotation"] and n_sols != 0:
            self.TopMassDelta["No-Rotation"][n_sols] = []
        for i in sols:
            self.TopMassDelta["No-Rotation"][n_sols] += [(i[0] + lep1 + b1).Mass/1000 - t1.Mass/1000, (i[1] + lep2 + b2).Mass/1000 - t2.Mass/1000]
 
        # ====================== Rotated ========================== #
        t4 = sum(event.Tops)
        angle = math.atan2(t4.pt, t4.pz)
        self.RotationP(t1, angle),   self.RotationP(t2, angle)
        self.RotationP(nu1, angle),  self.RotationP(nu2, angle)
        self.RotationP(lep1, angle), self.RotationP(lep2, angle)
        self.RotationP(b1, angle),   self.RotationP(b2, angle)

        t_Mass = (t1.Mass + t2.Mass)/2
        W_Mass = ((nu1 + lep1).Mass + (nu2 + lep2).Mass)/2
        sols = self.NuNu(b1, b2, lep1, lep2, event, t_Mass, W_Mass)

        n_sols, nu_sum = len(sols), (nu1 + nu2)
        self.NuNuSolutions["Rotation"].append(n_sols)
        self.Truth_MET_NuNu_Delta["Rotation"] += [abs(nu_sum.pt/met)]
        self.Truth_MET_xy_Delta["Rotation-x"] += [(met_x - nu_sum.px)/1000]
        self.Truth_MET_xy_Delta["Rotation-y"] += [(met_y - nu_sum.py)/1000]

        if n_sols not in self.TopMassDelta["Rotation"] and n_sols != 0:
            self.TopMassDelta["Rotation"][n_sols] = []
        for i in sols:
            self.TopMassDelta["Rotation"][n_sols] += [(i[0] + lep1 + b1).Mass/1000 - t1.Mass/1000, (i[1] + lep2 + b2).Mass/1000 - t2.Mass/1000]
 
