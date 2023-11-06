from AnalysisG import Analysis
from AnalysisG.Templates import ApplyFeatures
from AnalysisG.Events import GraphChildren, GraphTruthJet, GraphJet
from AnalysisG.Events import Event
import pyc.Graph.Polar as graph
import pyc.Physics.Cartesian as physics
import torch
import os

ev = os.environ["Samples"]

ana_children = Analysis()
ana_children.InputSample(None, ev + "ttZ-1000/DAOD_TOPQ1.21955717._000007.root")
ana_children.Event = Event
ana_children.Graph = GraphChildren
ana_children.EventStop = 10
ApplyFeatures(ana_children, "TruthChildren")
x = False
for i in ana_children:
    m_t = [sum(x.Children).Mass/1000 for x in i.Tops]
    pmu = torch.cat([i.N_pT, i.N_eta, i.N_phi, i.N_energy], -1)
    pmc = graph.edge(i.edge_index, i.E_T_top_edge.view(-1)*1, pmu, True)[1]["node_sum"]
    m = (physics.M(pmc)/1000).view(-1).tolist()
    m = {round(k, 2):None for k in m}
    m_t = {round(k, 2):None for k in m_t}
    assert len([x for x in m_t if x in m])

    m_Zt = sum(sum([x.Children for x in i.Tops if x.FromRes], []))
    pmc = graph.edge(i.edge_index, i.E_T_res_edge.view(-1), pmu, True)[1]
    pmc = pmc["unique_sum"][(pmc["clusters"] > -1).sum(-1) > 1]
    m_Z = (physics.M(pmc)).view(-1).tolist()[0]
    assert round(m_Zt.Mass/1000) == round(m_Z/1000)
    x = True
assert x

ana_truthjets = Analysis()
ana_truthjets.InputSample(None, ev + "ttZ-1000/DAOD_TOPQ1.21955717._000007.root")
ana_truthjets.Event = Event
ana_truthjets.Graph = GraphTruthJet
ana_truthjets.EventStop = 10
ApplyFeatures(ana_truthjets, "TruthJets")
ana_truthjets.Launch()
x = False
for i in ana_truthjets:
    m_t = []
    m_Zt = []
    for t in i.Tops:
        x = t.TruthJets + [k for k in t.Children if k.is_nu or k.is_lep]
        m_t.append(sum(x).Mass/1000)
        if t.FromRes: m_Zt += x
    pmu = torch.cat([i.N_pT, i.N_eta, i.N_phi, i.N_energy], -1)
    pmc = graph.edge(i.edge_index, i.E_T_top_edge.view(-1)*1, pmu, True)[1]
    pmc = pmc["unique_sum"][(pmc["clusters"] > -1).sum(-1) > 1]/1000
    m = physics.M(pmc).view(-1).tolist()
    m = {round(k, 2):None for k in m}
    m_t = {round(k, 2):None for k in m_t}
    assert len([x for x in m_t if x in m])

    m_Zt = sum(m_Zt).Mass/1000
    pmc = graph.edge(i.edge_index, i.E_T_res_edge.view(-1), pmu, True)[1]
    pmc = pmc["unique_sum"][(pmc["clusters"] > -1).sum(-1) > 1]
    m_Z = (physics.M(pmc)).view(-1).tolist()[0]
    assert abs(round(m_Zt) - round(m_Z/1000))/(m_Zt)*100 < 2
    x = True
assert x


ana_jets = Analysis()
ana_jets.InputSample(None, ev + "ttZ-1000/DAOD_TOPQ1.21955717._000007.root")
ana_jets.Event = Event
ana_jets.Graph = GraphJet
ana_jets.EventStop = 10
ApplyFeatures(ana_jets, "Jets")
ana_jets.Launch()
x = False
for i in ana_jets:
    m_t = []
    m_Zt = []
    for t in i.Tops:
        x = t.Jets + [k for k in t.Children if k.is_nu or k.is_lep]
        m_t.append(sum(x).Mass/1000)
        if t.FromRes: m_Zt += x
    pmu = torch.cat([i.N_pT, i.N_eta, i.N_phi, i.N_energy], -1)
    pmc = graph.edge(i.edge_index, i.E_T_top_edge.view(-1)*1, pmu, True)[1]
    pmc = pmc["unique_sum"][(pmc["clusters"] > -1).sum(-1) > 1]/1000
    m = physics.M(pmc).view(-1).tolist()
    m = {round(k, 2):None for k in m}
    m_t = {round(k, 2):None for k in m_t}
    assert len([x for x in m_t if x in m])

    m_Zt = sum(m_Zt).Mass/1000
    pmc = graph.edge(i.edge_index, i.E_T_res_edge.view(-1), pmu, True)[1]
    pmc = pmc["unique_sum"][(pmc["clusters"] > -1).sum(-1) > 1]
    m_Z = (physics.M(pmc)).view(-1).tolist()[0]/1000
    assert (abs(round(m_Zt) - round(m_Z))/(m_Zt))*100 < 2
    x = True
assert x





