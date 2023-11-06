.. _beyond-standard-model: https://github.com/woywoy123/BSM4tops-GNN-ntuples


Beyond Standard Model 4 Top Event
*********************************

This event implementation used more granular truth matching samples in which, the individual physics objects can be matched to their truth parent constituent. 
The source code producing relevant samples can be found under this link `beyond-standard-model`_.

Event Attribute Descriptions
____________________________


.. py:class:: AnalysisG.Events import Event

    :ivar weight: "weight_mc"
    :ivar index: "eventNumber"
    :ivar mu: "mu"
    :ivar met: "met_met"
    :ivar met_phi: "met_phi"
    :ivar Tops: A container holding the truth tops of the event (post final state radiation (fsr))
    :ivar TopChildren: A container holding the immediate decay products of the individual tops.
    :ivar TruthJets: A container holding the truth jets of the event.
    :ivar Jets: A container holding the jets of the event.
    :ivar Electrons: A container holding the detector level electron objects.
    :ivar Muons: A container holding the detector level muon objects.
    :ivar DetectorObjects: A cummulated list of jets, electrons and muons. This is the final reconstruction level of the event.

Particle Definitions
____________________

.. py:class:: AnalysisG.Events.Events.bsm_4tops.Particles.Top

    :ivar Type: "top"
    :ivar pt: "top_pt"
    :ivar eta: "top_eta"
    :ivar phi: "top_phi"
    :ivar e: "top_e"
    :ivar index: "top_index" - A unique top index for the set of tops in the event.
    :ivar charge: "top_charge"
    :ivar pdgid: "top_pdgid"
    :ivar FromRes: "top_FromRes" - An integer used to indicate whether the given top originates from a heavy resonance.
    :ivar status: "top_status" - The decay status of the final top quark.
    :ivar TruthJets: A container used to link the top quark with its truth jets
    :ivar Jets: A container used to link the top quark to the jets.
    :ivar Children: A container used to link the truth children to the top quark.

.. py:class:: AnalysisG.Events.Events.bsm_4tops.Particles.Children

    :ivar Type: "children"
    :ivar pt: "children_pt"
    :ivar eta: "children_eta"
    :ivar phi: "children_phi"
    :ivar e: "children_e"
    :ivar index: "children_index" - A unique child index for the set of children in the event.
    :ivar charge: "children_charge"
    :ivar pdgid: "children_pdgid"
    :ivar TopIndex: "children_TopIndex" - An integer based indexing system to match child particle to parent top quark.
    :ivar FromRes: A property which uses the Parent list (tops) to determine whether the child originates from a resonant top.
    :ivar Parent: A list containing the originating top quark.

.. py:class:: AnalysisG.Events.Events.bsm_4tops.Particles.TruthJet

    :ivar Type: "truthjets"
    :ivar pt: "truthjets_pt"
    :ivar eta: "truthjets_eta"
    :ivar phi: "truthjets_phi"
    :ivar e: "truthjets_e"
    :ivar index: "truthjets_index" - A unique truth jet index for the set of truth jets in the event.
    :ivar pdgid: "truthjets_pdgid"
    :ivar TopQuarkCount: "truthjets_topquarkcount"
    :ivar WBosonCount: "truthjets_wbosoncount"
    :ivar TopIndex: "truthjets_TopIndex" - An integer based indexing system to match truth jets to parent top quark(s).
    :ivar FromRes: A property which uses the Parent list (tops) to determine whether the truth jet originates from a resonant top.
    :ivar Tops: Tops contributing to the given truth jet.
    :ivar Partons: Generator level partons matched to the truth jet (Ghost Matching)

.. py:class:: AnalysisG.Events.Events.bsm_4tops.Particles.TruthJetParton

    :ivar Type: "TJparton"
    :ivar pt: "TJparton_pt"
    :ivar eta: "TJparton_eta"
    :ivar phi: "TJparton_phi"
    :ivar e: "TJparton_e"
    :ivar index: "TJparton_index" - A unique truth jet parton index for the set of truth jet partons in the event.
    :ivar TruthJetIndex: "TJparton_TruthJetIndex" - The index of the truth jet this parton matches to.
    :ivar TopChildIndex: "TJparton_ChildIndex" - The index of the truth child this parton matches to.
    :ivar charge: "TJparton_charge"
    :ivar pdgid: "TJparton_pdgid"
 
.. py:class:: AnalysisG.Events.Events.bsm_4tops.Particles.Jet

    :ivar Type: "jet"
    :ivar pt: "jet_pt"
    :ivar eta: "jet_eta"
    :ivar phi: "jet_phi"
    :ivar e: "jet_e"
    :ivar index: "jet_index" - A unique jet index for the set of jets in the event.

    :ivar btag_DL1r_60: "jet_isbtagged_DL1r_60"
    :ivar btag_DL1_60: "jet_isbtagged_DL1_60"

    :ivar btag_DL1r_70: "jet_isbtagged_DL1r_70"
    :ivar btag_DL1_70: "jet_isbtagged_DL1_70"

    :ivar btag_DL1r_77: "jet_isbtagged_DL1r_77"
    :ivar btag_DL1_77: "jet_isbtagged_DL1_77"

    :ivar btag_DL1r_85: "jet_isbtagged_DL1r_85"
    :ivar btag_DL1_85: "jet_isbtagged_DL1_85"

    :ivar DL1_b: "jet_DL1_pb"
    :ivar DL1_c: "jet_DL1_pc"
    :ivar DL1_u: "jet_DL1_pu"

    :ivar DL1r_b: "jet_DL1r_pb"
    :ivar DL1r_c: "jet_DL1r_pc"
    :ivar DL1r_u: "jet_DL1r_pu"

    :ivar TopIndex: "jet_TopIndex" - An integer based indexing system to match jets to parent top quark(s).
    :ivar Parton: A container holding partons matched to the given jet (Ghost Matched). 
    :ivar Tops: A container holding matched top-quark partons.

    :ivar FromRes: A property which uses the Parent list (tops) to determine whether the jet originates from a resonant top.

.. py:class:: AnalysisG.Events.Events.bsm_4tops.Particles.JetParton

    :ivar Type: "Jparton"
    :ivar pt: "Jparton_pt"
    :ivar eta: "Jparton_eta"
    :ivar phi: "Jparton_phi"
    :ivar e: "Jparton_e"
    :ivar index: "Jparton_index" - A unique jet parton index for the set of jet partons in the event.
    :ivar JetIndex: "Jparton_JetIndex" - The index of the jet this parton matches to.
    :ivar TopChildIndex: "TJparton_ChildIndex" - An index of the truth child the parton matches to.
    :ivar charge: "Jparton_charge"
    :ivar pdgid: "Jparton_pdgid"
 
.. py:class:: AnalysisG.Events.Events.bsm4_tops.Particles.Electron

    :ivar Type: "el"
    :ivar pt: "el_pt"
    :ivar eta: "el_eta"
    :ivar phi: "el_phi"
    :ivar e: "el_e"
    :ivar charge: "el_charge"

.. py:class:: AnalysisG.Events.Events.bsm4_tops.Particles.Muon

    :ivar Type: "mu"
    :ivar pt: "mu_pt"
    :ivar eta: "mu_eta"
    :ivar phi: "mu_phi"
    :ivar e: "mu_e"
    :ivar charge: "mu_charge"
