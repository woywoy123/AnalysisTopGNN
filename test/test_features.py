from AnalysisG.Events import Event
from AnalysisG.Events import GraphTops, GraphChildren, GraphTruthJet, GraphJet
from AnalysisG.Templates import ApplyFeatures
from AnalysisG.Model import ModelWrapper
from AnalysisG import Analysis
import torch

torch.set_printoptions(4, profile="full", linewidth=100000)
from conftest import clean_dir

smpl = "./samples/"
Files = {
    smpl + "sample1": ["smpl1.root"],
    smpl + "sample2": ["smpl1.root", "smpl2.root", "smpl3.root"],
}


def _MakeSample():
    Ana = Analysis()
    Ana.ProjectName = "_Project"
    Ana.InputSample(None, Files)
    Ana.Event = Event
    Ana.EventCache = True
    Ana.Launch
    return Ana


def _MakeGraph(Ana, Graph, mode):
    ApplyFeatures(Ana, mode)
    Ana.EventGraph = Graph
    Ana.EventCache = False
    Ana.DataCache = True
    Ana.Launch
    return Ana


def test_truth_top():
    Ana = _MakeSample()
    res_mass = []
    for i in Ana:
        res = sum([k for k in i.Tops if k.FromRes == 1]).Mass / 1000
        res_mass.append(res)

    Ana = _MakeGraph(Ana, GraphTops, "TruthTops")
    M = ModelWrapper()

    it = 0
    for i in Ana:
        i = i.clone()
        x = M.MassEdgeFeature(i, i.E_T_res_edge.view(-1))
        diff = 100 * abs(res_mass[it] - x.item()) / res_mass[it]
        assert diff < 1

        x = M.MassNodeFeature(i, i.N_T_res_node.view(-1))
        diff = 100 * abs(res_mass[it] - x.item()) / res_mass[it]
        assert diff < 1

        assert i.G_T_ntops
        assert i.G_phi
        assert i.G_met

        it += 1
    assert it > 0
    clean_dir()


def test_truth_children():
    Ana = _MakeSample()
    res_mass = []
    top_mass = []
    edge_lep = []
    n_nus = []
    for i in Ana:
        tops = i.Tops
        children = [c for t in tops for c in t.Children if t.FromRes == 1]
        to = children[0].Parent + children[1].Parent
        res_mass.append(sum(children).Mass / 1000)
        top_mass.append([sum(t.Children).Mass / 1000 for t in tops])
        _leps = [
            int(
                (c1.is_b + c2.is_b)
                * (c1.is_lep + c2.is_lep)
                * (c1.Parent[0] == c2.Parent[0])
                > 0
            )
            for c1 in i.TopChildren
            for c2 in i.TopChildren
        ]
        edge_lep.append(_leps)
        n_nus.append(sum([c.is_nu for c in i.TopChildren]))

    Ana = _MakeGraph(Ana, GraphChildren, "TruthChildren")
    M = ModelWrapper()

    it = 0
    for i in Ana:
        i = i.clone()
        assert i.G_T_signal.item() == 1
        assert i.G_T_ntops.item() == 4
        assert i.G_T_n_nu.item() == n_nus[it]

        x = M.MassEdgeFeature(i, i.E_T_res_edge.view(-1))
        diff = 100 * abs(res_mass[it] - x.item()) / res_mass[it]
        assert diff < 1

        x = M.MassEdgeFeature(i, i.E_T_top_edge.view(-1))
        x = x.tolist()
        x.sort()
        top_mass[it].sort()
        diff = sum(
            [
                abs(top_mass[it][g] - x[g]) / top_mass[it][g] >= 0.1
                for g in range(len(x))
            ]
        )
        assert diff < 1
        assert len(top_mass[it]) == len(x)

        _leps = i.E_T_lep_edge.view(-1).tolist()
        assert len(edge_lep[it]) == len(_leps)
        assert sum([k == j for k, j in zip(_leps, edge_lep[it])]) == len(edge_lep[it])
        it += 1
    assert it > 0
    clean_dir()


def test_truthjets():
    Ana = _MakeSample()
    res_edges = []
    top_edges = []
    lep_edges = []

    res_mass = []
    top_mass = []

    for i in Ana:
        particles = i.TruthJets
        particles += [c for c in i.TopChildren if c.is_nu or c.is_lep]
        tmp = []
        for c1 in particles:
            for c2 in particles:
                p1, p2 = [], []
                try:
                    p1 += c1.Parent
                except:
                    pass

                try:
                    p1 += c1.Tops
                except:
                    pass

                try:
                    p2 += c2.Parent
                except:
                    pass

                try:
                    p2 += c2.Tops
                except:
                    pass
                p1, p2 = [p for p in set(p1) if p.FromRes == 1], [
                    p for p in set(p2) if p.FromRes == 1
                ]
                res = len(p1) > 0 and len(p2) > 0
                tmp += [1] if res else [0]
        res_edges.append(tmp)

        tmp, tmp_l = [], []
        for c1 in particles:
            for c2 in particles:
                p1, p2 = [], []
                try:
                    p1 += c1.Parent
                except:
                    pass

                try:
                    p1 += c1.Tops
                except:
                    pass

                try:
                    p2 += c2.Parent
                except:
                    pass

                try:
                    p2 += c2.Tops
                except:
                    pass
                p1, p2 = set(p1), set(p2)
                sc = len([t for t in p1 if t in p2]) > 0
                sc *= len([t for t in p2 if t in p1]) > 0
                tmp += [1] if sc == 1 else [0]
                tmp_l += (
                    [1]
                    if (c1.is_b + c2.is_b) > 0 and (c1.is_lep + c2.is_lep) > 0
                    else [0]
                )
        top_edges.append(tmp)
        lep_edges.append(tmp_l)

        res_tj = []
        for t in i.Tops:
            res_tj += t.TruthJets if t.FromRes == 1 else []
        for l in i.TopChildren:
            if not l.is_lep and not l.is_nu:
                continue
            if len([x for x in l.Parent if x.FromRes == 1]) == 0:
                continue
            res_tj += [l]
        res_mass += [sum(res_tj).Mass / 1000]

        top_d = {}
        for t in i.Tops:
            if t.index not in top_d:
                top_d[t.index] = []
            top_d[t.index] += t.TruthJets
            top_d[t.index] += [c for c in t.Children if c.is_lep or c.is_nu]
            top_d[t.index] = sum(top_d[t.index]).Mass / 1000
        top_mass.append(list(top_d.values()))

    Ana = _MakeGraph(Ana, GraphTruthJet, "TruthJets")
    M = ModelWrapper()
    it = 0
    for i in Ana:
        i = i.clone()
        assert i.G_T_signal.item() == 1
        assert i.G_T_ntops.item() == 4

        dif = [
            1 for e, j in zip(i.E_T_res_edge.view(-1).tolist(), res_edges[it]) if e != j
        ]
        assert len(dif) == 0

        dif = [
            1 for e, j in zip(i.E_T_top_edge.view(-1).tolist(), top_edges[it]) if e != j
        ]
        assert len(dif) == 0

        dif = [
            1 for e, j in zip(i.E_T_lep_edge.view(-1).tolist(), lep_edges[it]) if e != j
        ]
        assert len(dif) == 0

        x = M.MassEdgeFeature(i, i.E_T_res_edge.view(-1)).tolist()
        assert len(x) == 1
        diff = 100 * abs(x[0] - res_mass[it]) / res_mass[it]

        x = M.MassEdgeFeature(i, i.E_T_top_edge.view(-1)).tolist()
        x.sort()
        top_mass[it].sort()

        le = min([len(x), len(top_mass[it])])
        diff = sum(
            [abs(top_mass[it][g] - x[g]) / top_mass[it][g] >= 1 for g in range(le)]
        )
        assert diff < 1

        it += 1
    assert it > 0
    clean_dir()


def test_jets():
    Ana = _MakeSample()
    res_edges = []
    top_edges = []
    lep_edges = []

    res_mass = []
    top_mass = []

    for i in Ana:
        particles = i.Jets
        particles += [c for c in i.TopChildren if c.is_nu or c.is_lep]
        tmp = []
        for c1 in particles:
            for c2 in particles:
                p1, p2 = [], []
                try:
                    p1 += c1.Parent
                except:
                    pass

                try:
                    p1 += c1.Tops
                except:
                    pass

                try:
                    p2 += c2.Parent
                except:
                    pass

                try:
                    p2 += c2.Tops
                except:
                    pass
                p1, p2 = [p for p in set(p1) if p.FromRes == 1], [
                    p for p in set(p2) if p.FromRes == 1
                ]
                res = len(p1) > 0 and len(p2) > 0
                tmp += [1] if res else [0]
        res_edges.append(tmp)

        tmp, tmp_l = [], []
        for c1 in particles:
            for c2 in particles:
                p1, p2 = [], []
                try:
                    p1 += c1.Parent
                except:
                    pass

                try:
                    p1 += c1.Tops
                except:
                    pass

                try:
                    p2 += c2.Parent
                except:
                    pass

                try:
                    p2 += c2.Tops
                except:
                    pass
                p1, p2 = set(p1), set(p2)
                sc = len([t for t in p1 if t in p2]) > 0
                sc *= len([t for t in p2 if t in p1]) > 0
                tmp += [1] if sc == 1 else [0]
                tmp_l += (
                    [1]
                    if (c1.is_b + c2.is_b) > 0 and (c1.is_lep + c2.is_lep) > 0
                    else [0]
                )
        top_edges.append(tmp)
        lep_edges.append(tmp_l)

        res_tj = []
        for t in i.Tops:
            res_tj += t.Jets if t.FromRes == 1 else []
        for l in i.TopChildren:
            if not l.is_lep and not l.is_nu:
                continue
            if len([x for x in l.Parent if x.FromRes == 1]) == 0:
                continue
            res_tj += [l]
        res_mass += [sum(res_tj).Mass / 1000]

        top_d = {}
        for t in i.Tops:
            top = []
            top += t.Jets
            top += [c for c in t.Children if c.is_lep or c.is_nu]
            if len(top) < 3:
                continue
            top_d[t.index] = sum(top).Mass / 1000
        top_mass.append(list(top_d.values()))

    Ana = _MakeGraph(Ana, GraphJet, "Jets")
    M = ModelWrapper()
    it = 0
    for i in Ana:
        i = i.clone()
        assert i.G_T_signal.item() == 1
        assert i.G_T_ntops.item() == 4

        dif = [
            1 for e, j in zip(i.E_T_res_edge.view(-1).tolist(), res_edges[it]) if e != j
        ]
        assert len(dif) == 0

        dif = [
            1 for e, j in zip(i.E_T_top_edge.view(-1).tolist(), top_edges[it]) if e != j
        ]
        assert len(dif) == 0

        dif = [
            1 for e, j in zip(i.E_T_lep_edge.view(-1).tolist(), lep_edges[it]) if e != j
        ]
        assert len(dif) == 0

        x = M.MassEdgeFeature(i, i.E_T_res_edge.view(-1)).tolist()
        assert len(x) == 1
        diff = 100 * abs(x[0] - res_mass[it]) / res_mass[it]

        x = M.MassEdgeFeature(i, i.E_T_top_edge.view(-1)).tolist()
        top_mass[it].sort()

        chi = {abs(x_i - x_j): [x_i, x_j] for x_i in x for x_j in top_mass[it]}
        low = list(chi)
        low.sort()
        found = []
        for l in low:
            x_i, x_j = chi[l]
            if x_j in found:
                continue
            found.append(x_j)
        assert len(found) == len(top_mass[it])
        found.sort()

        le = min([len(x), len(top_mass[it])])
        diff = sum(
            [abs(top_mass[it][g] - found[g]) / top_mass[it][g] >= 1 for g in range(le)]
        )
        assert diff < 1

        it += 1
    assert it > 0
    clean_dir()


if __name__ == "__main__":
    test_truth_top()
    test_truth_children()
    test_truthjets()
    test_jets()

    pass
