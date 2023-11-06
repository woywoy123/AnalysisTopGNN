import sys
sys.path.append("../../test/neutrino_reconstruction/")
from nusol import (SingleNu, DoubleNu)
from AnalysisG.Templates import SelectionTemplate

class NeutrinoReconstruction(SelectionTemplate):

    def __init__(self):
        SelectionTemplate.__init__(self)
        self.num_sols = {"mev" : [], "gev" : []}

        self.top_mass_r2l = {"mev" : [], "gev" : []}
        self.top_mass_r1l = {"mev" : [], "gev" : []}
        self.H_mass_r2l = {"mev" : [], "gev" : []}

        self.top_mass_t1l = {"children" : []}
        self.top_mass_t2l = {"children" : []}
        self.H_mass_t2l = {"children" : []}

        self.top_kin_r2l = {
                "mev" : {"px" : [], "py" : [], "pz" : [], "e" : []},
                "gev" : {"px" : [], "py" : [], "pz" : [], "e" : []},
        }

        self.top_kin_r1l = {
                "mev" : {"px" : [], "py" : [], "pz" : [], "e" : []},
                "gev" : {"px" : [], "py" : [], "pz" : [], "e" : []},
        }

    def Selection(self, event):
        self.leps = len([1 for t in event.Tops if t.LeptonicDecay])
        if self.leps > 2 and self.leps > 0: return False
        return True

    def kinCollector(self, dic, key, reco, truth):
        dic[key]["px"].append( abs((truth.px - reco.px)/reco.px)*100 )
        dic[key]["py"].append( abs((truth.py - reco.py)/reco.py)*100 )
        dic[key]["pz"].append( abs((truth.pz - reco.pz)/reco.pz)*100 )
        dic[key]["e" ].append( abs((truth.e  - reco.e )/reco.e )*100 )

    def SingleNeutrino(self, event, t1):
        b1  = [c for c in t1.Children if c.is_b][0]
        l1  = [c for c in t1.Children if c.is_lep][0]
        nu1 = [c for c in t1.Children if c.is_nu][0]

        mT = (b1+l1+nu1).Mass
        mW = (l1 + nu1).Mass
        tvl = [nu+b1+l1 for nu in self.Nu(b1, l1, event, mT = mT, mW = mW)]
        self.num_sols["mev"] += [len(tvl)]
        for t in tvl:
            self.top_mass_r1l["mev"] += [t.Mass/1000]
            self.kinCollector(self.top_kin_r1l, "mev", t, t1)

        tvl = [nu+b1+l1 for nu in self.Nu(b1, l1, event, mT = mT, mW = mW, gev = True)]
        self.num_sols["gev"] += [len(tvl)]
        for t in tvl:
            self.top_mass_r1l["gev"] += [t.Mass/1000]
            self.kinCollector(self.top_kin_r1l, "gev", t, t1)

        self.top_mass_t1l["children"].append((b1+l1+nu1).Mass/1000)
        return

    def DileptonNeutrino(self, event, t1, t2):
        b1  = [c for c in t1.Children if c.is_b][0]
        l1  = [c for c in t1.Children if c.is_lep][0]
        nu1 = [c for c in t1.Children if c.is_nu][0]

        b2  = [c for c in t2.Children if c.is_b][0]
        l2  = [c for c in t2.Children if c.is_lep][0]
        nu2 = [c for c in t2.Children if c.is_nu][0]

        from_res = t1.FromRes == t2.FromRes == 1
        if from_res:
            H = (b1 + b2 + l1 + l2 + nu1 + nu2)
            self.H_mass_t2l["children"].append(H.Mass/1000)
        self.top_mass_t2l["children"] += [(b1+l1+nu1).Mass/1000, (b2+l2+nu2).Mass/1000]

        mT = (b1+l1+nu1).Mass
        mW = (l1 + nu1).Mass

        nus = self.NuNu(b1, b2, l1, l2, event, mT = mT, mW = mW, gev = False)
        self.num_sols["mev"] += [len(nus)]
        for nu_p in nus:
            tvl  = nu_p[0] + b1 + l1
            tvl_ = nu_p[1] + b2 + l2

            self.top_mass_r2l["mev"] += [ tvl.Mass/1000]
            self.top_mass_r2l["mev"] += [tvl_.Mass/1000]
            if from_res: self.H_mass_r2l["mev"] += [(tvl + tvl_).Mass/1000]

            self.kinCollector(self.top_kin_r2l, "mev", tvl , t1)
            self.kinCollector(self.top_kin_r2l, "mev", tvl_, t2)

        nus = self.NuNu(b1, b2, l1, l2, event, mT = mT, mW = mW, gev = True)
        self.num_sols["gev"] += [len(nus)]
        for nu_p in nus:
            tvl  = nu_p[0] + b1 + l1
            tvl_ = nu_p[1] + b2 + l2

            self.top_mass_r2l["gev"] += [ tvl.Mass/1000]
            self.top_mass_r2l["gev"] += [tvl_.Mass/1000]
            if from_res: self.H_mass_r2l["gev"] += [(tvl + tvl_).Mass/1000]

            self.kinCollector(self.top_kin_r2l, "gev", tvl, t1)
            self.kinCollector(self.top_kin_r2l, "gev", tvl_, t2)

    def Strategy(self, event):
        leptops = [t for t in event.Tops if t.LeptonicDecay]
        if self.leps == 2:
            t1, t2 = leptops
            self.DileptonNeutrino(event, t1, t2)
        else:
            self.SingleNeutrino(event, leptops[0])





