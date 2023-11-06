from AnalysisG.Templates import ParticleTemplate


class Particle(ParticleTemplate):
    def __init__(self):
        ParticleTemplate.__init__(self)

        self.pt = self.Type + "_pt"
        self.eta = self.Type + "_eta"
        self.phi = self.Type + "_phi"
        self.e = self.Type + "_e"

class Electron(Particle):

    def __init__(self):
        self.Type = "el"
        Particle.__init__(self)
        self.charge = "el_charge"
        self.tight = "el_isTight"
        self.d0sig = "el_d0sig"
        self.delta_z0 = "el_delta_z0_sintheta"
        self.si_d0 = "el_bestmatchSiTrackD0"
        self.si_eta = "el_bestmatchSiTrackEta"
        self.si_phi = "el_bestmatchSiTrackPhi"
        self.si_pt = "el_bestmatchSiTrackPt"


class Muon(Particle):

    def __init__(self):
        self.Type = "mu"
        Particle.__init__(self)
        self.charge = "mu_charge"
        self.tight = "mu_isTight"
        self.d0sig = "mu_d0sig"
        self.delta_z0 = "mu_delta_z0_sintheta"

class Jet(Particle):

    def __init__(self):
        self.Type = "jet"
        Particle.__init__(self)
        self.jvt = "jet_jvt"
        self.width = "jet_Width"

        _tag = "jet_isbtagged_"
        self.dl1_btag_60 = _tag + "DL1dv01_60"
        self.dl1_btag_70 = _tag + "DL1dv01_70"
        self.dl1_btag_77 = _tag + "DL1dv01_77"
        self.dl1_btag_85 = _tag + "DL1dv01_85"

        self.dl1 = "jet_DL1dv01"
        self.dl1_b = "jet_DL1dv01_pb"
        self.dl1_c = "jet_DL1dv01_pc"
        self.dl1_u = "jet_DL1dv01_pu"

        self.gn2_btag_60 = _tag + "GN2v00NewAliasWP_60"
        self.gn2_btag_70 = _tag + "GN2v00NewAliasWP_70"
        self.gn2_btag_77 = _tag + "GN2v00NewAliasWP_77"
        self.gn2_btag_85 = _tag + "GN2v00NewAliasWP_85"

        self.gn2_lgc_btag_60 = _tag + "GN2v00LegacyWP_60"
        self.gn2_lgc_btag_70 = _tag + "GN2v00LegacyWP_70"
        self.gn2_lgc_btag_77 = _tag + "GN2v00LegacyWP_77"
        self.gn2_lgc_btag_85 = _tag + "GN2v00LegacyWP_85"


