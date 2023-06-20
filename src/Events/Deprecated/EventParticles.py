from AnalysisTopGNN.Templates import ParticleTemplate


### Default AnalysisTop particles
class Particle(ParticleTemplate):
    def __init__(self, Type="Particle"):
        ParticleTemplate.__init__(self)

        self.Type = Type
        self.pt = self.Type + "_pt"
        self.eta = self.Type + "_eta"
        self.phi = self.Type + "_phi"
        self.e = self.Type + "_e"


class Lepton(Particle):
    def __init__(self):
        self.charge = self.Type + "_charge"
        self.topoetcone20 = self.Type + "_topoetcone20"
        self.d0sig = self.Type + "_d0sig"
        self.delta_z0_sintheta = self.Type + "_delta_z0_sintheta"
        self.true_type = self.Type + "_true_type"
        self.true_origin = self.Type + "_true_origin"
        self.true_IFFclass = self.Type + "_true_IFFclass"
        self.true_isPrompt = self.Type + "_true_isPrompt"
        Particle.__init__(self, self.Type)


class Electron(Lepton):
    def __init__(self):
        self.Type = "el"
        self.ptvarcone20 = self.Type + "_ptvarcone20"
        self.CL = self.Type + "_CF"
        self.true_firstEgMotherTruthType = self.Type + "_true_firstEgMotherTruthType"
        self.true_firstEgMotherTruthOrigin = (
            self.Type + "_true_firstEgMotherTruthOrigin"
        )
        self.true_firstEgMotherPdgId = self.Type + "_true_firstEgMotherPdgId"
        self.true_isChargeFl = self.Type + "_true_isChargeFl"
        Lepton.__init__(self)


class Muon(Lepton):
    def __init__(self):
        self.Type = "mu"
        self.ptvarcone30 = self.Type + "_ptvarcone30"
        Lepton.__init__(self)


class Jet(Particle):
    def __init__(self):
        self.Type = "jet"
        self.jvt = self.Type + "_jvt"
        self.truthflav = self.Type + "_truthflav"
        self.truthPartonLabel = self.Type + "_truthPartonLabel"
        self.isTrueHS = self.Type + "_isTrueHS"
        self.truthflavExtended = self.Type + "_truthflavExtended"
        self.isbtagged_DL1r_77 = self.Type + "_isbtagged_DL1r_77"
        self.isbtagged_DL1r_70 = self.Type + "_isbtagged_DL1r_70"
        self.isbtagged_DL1r_60 = self.Type + "_isbtagged_DL1r_60"
        self.isbtagged_DL1r_85 = self.Type + "_isbtagged_DL1r_85"
        self.DL1r = self.Type + "_DL1r"
        self.DL1r_pb = self.Type + "_DL1r_pb"
        self.DL1r_pc = self.Type + "_DL1r_pc"
        self.DL1r_pu = self.Type + "_DL1r_pu"

        self.isbtagged_DL1_77 = self.Type + "_isbtagged_DL1_77"
        self.isbtagged_DL1_70 = self.Type + "_isbtagged_DL1_70"
        self.isbtagged_DL1_60 = self.Type + "_isbtagged_DL1_60"
        self.isbtagged_DL1_85 = self.Type + "_isbtagged_DL1_85"
        self.DL1 = self.Type + "_DL1"
        self.DL1_pb = self.Type + "_DL1_pb"
        self.DL1_pc = self.Type + "_DL1_pc"
        self.DL1_pu = self.Type + "_DL1_pu"

        self.JetMapGhost = self.Type + "_map_Ghost"
        self.JetMapTops = self.Type + "_map_Gtops"

        Particle.__init__(self, self.Type)


class TruthJet(Particle):
    def __init__(self):
        self.Type = "truthjet"
        self.pdgid = self.Type + "_pdgid"
        self.GhostTruthJetMap = "GhostTruthJetMap"
        Particle.__init__(self, self.Type)


### Additional custom particle definitions
class TruthTop(Particle):
    def __init__(self):
        self.Type = "truth_top"
        self.FromRes = "truth_top_FromRes"
        Particle.__init__(self, self.Type)


class TopPreFSR(Particle):
    def __init__(self):
        self.Type = "topPreFSR"
        self.charge = self.Type + "_charge"
        self.Status = self.Type + "_status"
        Particle.__init__(self, self.Type)


class TopPostFSR(Particle):
    def __init__(self):
        self.Type = "topPostFSR"
        self.charge = self.Type + "_charge"
        self.FromRes = "Gtop_FromRes"
        Particle.__init__(self, self.Type)


class TruthTopChildren(Particle):
    def __init__(self):
        self.Type = "truth_top_child"
        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"
        Particle.__init__(self, self.Type)


class TopPostFSRChildren(Particle):
    def __init__(self):
        self.Type = "topPostFSRchildren"
        self.charge = self.Type + "_charge"
        self.pdgid = self.Type + "_pdgid"
        Particle.__init__(self, self.Type)
