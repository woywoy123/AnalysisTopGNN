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
        self.index = self.Type + "_index"
        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"
        self.FromRes = self.Type + "_FromRes"
        self.status = self.Type + "_status"
        self.TruthJets = []
        self.Jets = []


class Children(Particle):
    def __init__(self):
        self.Type = "children"
        Particle.__init__(self)

        self.index = self.Type + "_index"
        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"
        self.TopIndex = self.Type + "_TopIndex"

    @property
    def FromRes(self):
        return self.Parent[0].FromRes


class TruthJet(Particle):
    def __init__(self):
        self.Type = "truthjets"
        Particle.__init__(self)

        self.index = self.Type + "_index"
        self.pdgid = self.Type + "_btagged"
        self.TopQuarkCount = self.Type + "_topquarkcount"
        self.WBosonCount = self.Type + "_wbosoncount"
        self.TopIndex = self.Type + "_TopIndex"
        self.Tops = []
        self.Parton = []

    @property
    def FromRes(self):
        return 0 if len(self.Tops) == 0 else self.Tops[0].FromRes


class TruthJetParton(Particle):
    def __init__(self):
        self.Type = "TJparton"
        Particle.__init__(self)

        self.index = self.Type + "_index"
        self.TruthJetIndex = self.Type + "_TruthJetIndex"
        self.TopChildIndex = self.Type + "_ChildIndex"
        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"


class Jet(Particle):
    def __init__(self):
        self.Type = "jet"
        Particle.__init__(self)

        # self.index = self.Type + "_index"
        # self.TopIndex = self.Type + "_TopIndex"
        self.Tops = []

        # self.btag_DL1r_60 = self.Type + "_isbtagged_DL1r_60"
        # self.btag_DL1_60 = self.Type + "_isbtagged_DL1_60"

        # self.btag_DL1r_70 = self.Type + "_isbtagged_DL1r_70"
        # self.btag_DL1_70 = self.Type + "_isbtagged_DL1_70"

        # self.btag_DL1r_77 = self.Type + "_isbtagged_DL1r_77"
        # self.btag_DL1_77 = self.Type + "_isbtagged_DL1_77"

        # self.btag_DL1r_85 = self.Type + "_isbtagged_DL1r_85"
        # self.btag_DL1_85 = self.Type + "_isbtagged_DL1_85"

        # self.DL1_b = self.Type + "_DL1_pb"
        # self.DL1_c = self.Type + "_DL1_pc"
        # self.DL1_u = self.Type + "_DL1_pu"

        # self.DL1r_b = self.Type + "_DL1r_pb"
        # self.DL1r_c = self.Type + "_DL1r_pc"
        # self.DL1r_u = self.Type + "_DL1r_pu"

        self.Parton = []

    @property
    def is_b(self):
        return self.btag_DL1r_77

    @property
    def FromRes(self):
        if len(self.Tops) == 0:
            return False
        return len([t for t in self.Tops if t.FromRes == 1]) > 0


class JetParton(Particle):
    def __init__(self):
        self.Type = "Jparton"
        Particle.__init__(self)

        self.index = self.Type + "_index"
        self.JetIndex = self.Type + "_JetIndex"
        self.TopChildIndex = self.Type + "_ChildIndex"
        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"


class Electron(Particle):
    def __init__(self):
        self.Type = "el"
        Particle.__init__(self)
        self.charge = self.Type + "_charge"
        self.index = []

    @property
    def is_lep(self):
        return True


class Muon(Particle):
    def __init__(self):
        self.Type = "mu"
        Particle.__init__(self)
        self.charge = self.Type + "_charge"
        self.index = []

    @property
    def is_lep(self):
        return True


class Neutrino(ParticleTemplate):
    def __init__(self, px=None, py=None, pz=None):
        self.Type = "nu"
        ParticleTemplate.__init__(self)
        self.px = px
        self.py = py
        self.pz = pz
