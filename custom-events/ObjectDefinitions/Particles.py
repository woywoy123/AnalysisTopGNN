from AnalysisTopGNN.Templates import ParticleTemplate 

class Particle(ParticleTemplate):

    def __init__(self):
        ParticleTemplate.__init__(self)


class Child(Particle):

    def __init__(self, pdgid=None, TopIndex=None, FromRes=None, Energy=None):
        self.Type = "children"
        Particle.__init__(self)

        self.pdgid = pdgid
        self.TopIndex = TopIndex
        self.FromRes = FromRes
        self.e = Energy

    def __Sel(self, lst):
        return True if abs(self.pdgid) in lst else False

    @property
    def is_lep(self):
        return self.__Sel([11, 13])

    @property
    def is_nu(self):
        return self.__Sel([12, 14])

    @property
    def is_b(self):
        return self.__Sel([5])


class TruthJet(Particle):
    def __init__(self):
        self.Type = "truthjets"
        Particle.__init__(self)

        self.Parton = []


class TruthJetParton(Particle):

    def __init__(self, pdgid=None, TopIndex=None, TopChildIndex=None, FromRes=None, Energy=None):
        self.Type = "TJparton"
        Particle.__init__(self)

        self.pdgid = pdgid
        self.TopIndex = TopIndex
        self.TopChildIndex = TopChildIndex
        self.FromRes = FromRes
        self.e = Energy
    

    

    


