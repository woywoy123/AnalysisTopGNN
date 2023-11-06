.. _common-framework: https://gitlab.cern.ch/atlas-phys/exot/hqt/ana-exot-2022-44/common-framework

Same Sign Multi-Lepton Event
****************************

Event implementation is made to be compatible with samples produced using the AnalysisTop based **common-framework**.
The project can be found under this link `common-framework`_.

Event Attribute Descriptions
____________________________

This section aims to list all the attributes of the event implementation and how these are matched to the ROOT strings. Particle implementations will be listed later.
Within the repository, relevant scripts can be found under; /src/Events/Events/ssml/

.. py:class:: AnalysisG.Events import SSML

    :ivar index: "eventNumber"
    :ivar is_mc: "mcChannelNumber" - This could be used to indicate whether the given samples are data or mc, since these would be assigned a null or integer value respectively.
    :ivar met: "met_met"
    :ivar phi: "met_phi"
    :ivar Electrons: A container for the event electrons
    :ivar Muons: A container for the event muons
    :ivar Jets: A container for the event jets
    :ivar Detector: A list of all event particles.



Particle Definitions
____________________

This section highlights the attributes associated with the different event particles.

.. py:class:: AnalysisG.Events.Events.ssml.Particles.Electron

    :ivar Type: "el"
    :ivar pt: "el_pt"
    :ivar eta: "el_eta"
    :ivar phi: "el_phi"
    :ivar e: "el_e"
    :ivar charge: "el_charge"
    :ivar tight: "el_isTight"
    :ivar d0sig: "el_d0sig"
    :ivar delta_z0: "el_delta_z0_sintheta"
    :ivar delta_z0: "el_delta_z0_sintheta"
    :ivar si_d0: "el_bestmatchSiTrackD0"
    :ivar si_eta: "el_bestmatchSiTrackEta"
    :ivar si_phi: "el_bestmatchSiTrackPhi"
    :ivar si_pt: "el_bestmatchSiTrackPt"


.. py:class:: AnalysisG.Events.Events.ssml.Particles.Muon

    :ivar Type: "mu"
    :ivar pt: "mu_pt"
    :ivar eta: "mu_eta"
    :ivar phi: "mu_phi"
    :ivar e: "mu_e"
    :ivar charge: "mu_charge"
    :ivar tight: "mu_isTight"
    :ivar d0sig: "mu_d0sig"
    :ivar delta_z0: "mu_delta_z0_sintheta"

.. py:class:: AnalysisG.Events.Events.ssml.Particles.Jet

    :ivar Type: "jet"
    :ivar pt: "jet_pt"
    :ivar eta: "jet_eta"
    :ivar phi: "jet_phi"
    :ivar e: "jet_e"

    :ivar jvt: "jet_jvt"
    :ivar width: "jet_Width"

    :ivar dl1_btag_60: "jet_isbtagged_DL1dv01_60"
    :ivar dl1_btag_70: "jet_isbtagged_DL1dv01_70"
    :ivar dl1_btag_77: "jet_isbtagged_DL1dv01_77"
    :ivar dl1_btag_85: "jet_isbtagged_DL1dv01_85"

    :ivar dl1:   "jet_DL1dv01"
    :ivar dl1_b: "jet_DL1dv01_pb"
    :ivar dl1_c: "jet_DL1dv01_pc"
    :ivar dl1_u: "jet_DL1dv01_pu"

    :ivar gn2_btag_60: "jet_isbtagged_GN2v00NewAliasWP_60"
    :ivar gn2_btag_70: "jet_isbtagged_GN2v00NewAliasWP_70"
    :ivar gn2_btag_77: "jet_isbtagged_GN2v00NewAliasWP_77"
    :ivar gn2_btag_85: "jet_isbtagged_GN2v00NewAliasWP_85"

    :ivar gn2_lgc_btag_60: "jet_isbtagged_GN2v00LegacyWP_60"
    :ivar gn2_lgc_btag_70: "jet_isbtagged_GN2v00LegacyWP_70"
    :ivar gn2_lgc_btag_77: "jet_isbtagged_GN2v00LegacyWP_77"
    :ivar gn2_lgc_btag_85: "jet_isbtagged_GN2v00LegacyWP_85"


