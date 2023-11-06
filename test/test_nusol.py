import pyc
import torch
import numpy as np
import math
from neutrino_reconstruction.common import *
from neutrino_reconstruction.nusol import (
        NuSol, intersections_ellipses,
        UnitCircle, SingleNu, DoubleNu
)

mW = 80.385*1000
mT = 172.0*1000
mN = 0

dev = "cuda" if torch.cuda.is_available() else "cpu"
masses = torch.tensor([[mW, mT, mN]], dtype = torch.float64, device = dev)
S2 = torch.tensor([[100, 9], [50, 100]], dtype = torch.float64, device = dev)

# Numerical differences in C++ and Python appear below this number
precision = 10e-10
tolerance = 1e-3

def compare(truth, pred):
    t = truth[truth != 0]
    p = pred[pred != 0]
    x = abs(p - t)/abs(t) > tolerance
    return x.sum(-1).sum(-1).sum(-1) == 0

def compare_list(truth, pred):
    trig = False
    if len(truth) == 0: 
        return len(pred) == 0 
    for pairs_t in truth:
        trig = False
        for pairs_p in pred:
            trig = compare(pairs_t, pairs_p)
            if trig: break
        if not trig: return False
    return trig

def test_nusol_base_cuda():
    x = loadSingle()
    ita = iter(x)
    inpt = {"bq" : [], "lep" : []}
    for i in range(len(x)):
        x_ = next(ita)
        lep, bquark = x_[1], x_[2]
        nu = NuSol(bquark.vec, lep.vec)
        lep_ = pyc.Transform.PxPyPzE(lep.ten)
        bquark_ = pyc.Transform.PxPyPzE(bquark.ten)
        inpt["bq"] += [bquark_]
        inpt["lep"] += [lep_]
        truth = torch.tensor(nu.BaseMatrix).to(device = dev)
        pred = pyc.NuSol.BaseMatrix(bquark_, lep_, masses)
        assert compare(truth, pred)

    multi = 1000
    inpt["bq"] = torch.cat(inpt["bq"], dim = 0)
    inpt["lep"] = torch.cat(inpt["lep"], dim = 0)
    inpt["bq"]  = torch.cat([inpt["bq"] for _ in range(multi)], dim = 0)
    inpt["lep"] = torch.cat([inpt["lep"] for _ in range(multi)], dim = 0)
    nEvents = inpt["lep"].size(0)
    _cu = pyc.NuSol.BaseMatrix(inpt["bq"], inpt["lep"], masses)

def test_nusol_nu_cuda():
    x = loadSingle()
    ita = iter(x)

    lst = []
    inpt = []

    for i in range(len(x)):
        x_ = next(ita)
        ev, lep, bquark = x_[0], x_[1], x_[2]
        nu = NuSol(bquark.vec, lep.vec, ev.vec)
        lst.append(torch.tensor(nu.M).view(-1, 3, 3))

        lep_ = pyc.Transform.PxPyPzE(lep.ten)
        bquark_ = pyc.Transform.PxPyPzE(bquark.ten)
        inpt.append([bquark_, lep_, ev.ten])

    truth = torch.cat(lst, 0)

    bquark_ = torch.cat([i[0] for i in inpt], 0)
    lep_    = torch.cat([i[1] for i in inpt], 0)
    ev_     = torch.cat([i[2] for i in inpt], 0)

    pred = pyc.NuSol.Nu(bquark_, lep_, ev_, masses, S2, -1)
    pred = pred.to(device = "cpu")
    assert compare(truth, pred)

def test_intersection_cuda():
    x = loadSingle()
    ita = iter(x)
    M_container = []
    U_container = []
    res = []

    for i in range(len(x)):
        x_ = next(ita)
        ev, lep, b = x_[0], x_[1], x_[2]
        nu = NuSol(b.vec, lep.vec, ev.vec)
        unit = UnitCircle()
        points, diag = intersections_ellipses(nu.M, unit, precision)

        unit = torch.tensor(unit, device = dev, dtype = torch.float64)
        lep_ = pyc.Transform.PxPyPzE(lep.ten)
        bquark_ = pyc.Transform.PxPyPzE(b.ten)
        M = pyc.NuSol.Nu(bquark_, lep_, ev.ten, masses, S2, -1)
        M_container.append(M)
        U_container.append(unit.view(-1, 3, 3))
        pts, dig = pyc.Intersection(M, unit.view(-1, 3, 3), precision)

        points_t = torch.tensor(np.array(points), device = dev, dtype = torch.float64)
        points_cu = pts.view(-1, 3)
        points_cu = points_cu[points_cu.sum(-1) != 0]
        points_t = points_t.view(-1, 3)
        if len(points_cu) == 0:
            assert len(points_t) == 0
            continue
        res.append(points_t)
        for pairs_t in points_t:
            lim = False
            for pairs in points_cu:
                lim = compare(pairs_t, pairs)
                if not lim: continue
                break

            if not lim:
                print("----->>> Failure <<< ----")
                print("@ -> ", i)
                print(points_t)
                print(points_cu)
                print("-------------------------")
            assert lim
    m = torch.cat(M_container, dim = 0)
    u = torch.cat(U_container, dim = 0)
    res_t = torch.cat(res, dim = 0)
    res_cu, b = pyc.NuSol.Intersection(m, u, precision)
    res_cu = res_cu.clone()
    res_cu = res_cu.view(-1, 3)
    res_cu = res_cu[res_cu.sum(-1) != 0]
    assert compare_list(res_t, res_cu)

    # test speed
    multi = 100
    nEvents = sum([m.size(0) for k in range(multi)])
    m = torch.cat([m for k in range(multi)], dim = 0).clone()
    u = torch.cat([u for k in range(multi)], dim = 0).clone()
    pyc.NuSol.Intersection(m, u, precision)

def test_nu_cuda():

    x = loadSingle()
    ita = iter(x)
    compare = []
    inpts = {"b_cu" : [], "lep_cu" : [], "ev_cu" : [], 
             "m_cu" : [], "s2" : []}
    for i in range(len(x)):
        x_ = next(ita)
        ev, lep, b = x_[0], x_[1], x_[2]
        nu = SingleNu(b.vec, lep.vec, ev.vec)
        nu_t = torch.tensor(np.array(nu.nu), device = "cpu", dtype = torch.float64)

        lep_cu = pyc.Transform.PxPyPzE(lep.ten)
        b_cu   = pyc.Transform.PxPyPzE(b.ten)
        inpts["b_cu"].append(b_cu)
        inpts["lep_cu"].append(lep_cu)
        inpts["m_cu"].append(masses)
        inpts["ev_cu"].append(ev.ten)
        inpts["s2"].append(S2.view(-1, 2, 2))
        _cu  = pyc.NuSol.Nu(b_cu, lep_cu, ev.ten, masses, S2, precision)
        nu_cu = _cu[0].to(device = "cpu").view(-1, 3)
        compare.append(nu_cu)
        if len(nu_cu) == 0:
            assert len(nu_t) == 0
            continue
        assert compare_list(nu_t, nu_cu)

    b_cu = torch.cat(inpts["b_cu"], dim = 0)
    lep_cu = torch.cat(inpts["lep_cu"], dim = 0)
    ev_cu = torch.cat(inpts["ev_cu"], dim = 0)
    mass_cu = torch.cat(inpts["m_cu"], dim = 0)
    s2_cu = torch.cat(inpts["s2"], dim = 0)
    _cu = pyc.NuSol.Nu(b_cu, lep_cu, ev_cu, masses, S2, precision)[0].to(device = "cpu")
    _cu = _cu[_cu.sum(-1) != 0]

    t = torch.cat(compare, dim = 0)
    assert len(t[t - _cu > 1e-8]) == 0

    _cu = pyc.NuSol.Nu(b_cu, lep_cu, ev_cu, mass_cu, s2_cu, precision)[0].to(device = "cpu")
    _cu = _cu[_cu.sum(-1) != 0]
    assert len(t[t - _cu > 1e-8]) == 0

def test_nunu_cuda():

    x = loadDouble()
    ita = iter(x)

    compare = {"nu1" : [], "nu2" : []}
    inpts = {
                "b1_cu" : [], "b2_cu" : [],
                "l1_cu" : [], "l2_cu" : [],
                "met_xy" : []
    }

    for i in range(len(x)):
        x_ = next(ita)
        ev, l1, l2, b1, b2 = x_
        met_xy = ev.ten
        _b1 = pyc.Transform.PxPyPzE(b1.ten)
        _l1 = pyc.Transform.PxPyPzE(l1.ten)
        _b2 = pyc.Transform.PxPyPzE(b2.ten)
        _l2 = pyc.Transform.PxPyPzE(l2.ten)

        inpts["b1_cu"].append(_b1)
        inpts["b2_cu"].append(_b2)

        inpts["l1_cu"].append(_l1)
        inpts["l2_cu"].append(_l2)

        inpts["met_xy"].append(met_xy)

        nunu_cu = pyc.NuSol.NuNu(_b1, _b2, _l1, _l2, met_xy, masses, precision)
        c_nu, c_nu_ = nunu_cu[0].to(device = "cpu"), nunu_cu[1].to(device = "cpu")
        compare["nu1"].append(c_nu.view(-1, 3))
        compare["nu2"].append(c_nu_.view(-1, 3))

        try: sols = DoubleNu((b1.vec, b2.vec), (l1.vec, l2.vec), ev).nunu_s
        except np.linalg.LinAlgError: sols = []

        t_nu  = torch.tensor(np.array([i for i, _ in sols]), dtype = torch.float64)
        t_nu_ = torch.tensor(np.array([j for _, j in sols]), dtype = torch.float64)
        if len(t_nu) != 0: assert len(c_nu[0]) > 0

        for t_nui, t_nuj in zip(t_nu, t_nu_):
            lim = False
            sum_i_, sum_j_ = 1000, 1000
            for c_nui, c_nuj in zip(c_nu[0], c_nu_[0]):
                sum_i = abs((t_nui - c_nui)/t_nui).sum(-1)
                sum_j = abs((t_nuj - c_nuj)/t_nuj).sum(-1)
                if sum_i_ > sum_i and sum_j_ > sum_j: 
                    sum_i_ = sum_i
                    sum_j_ = sum_j
                if sum_i > 1 or sum_j > 1: continue
                lim = True
                break

            if not lim:
                print("----->>> Failure <<< ----")
                print("@ -> ", i)
                print(t_nui)
                print(t_nuj)
                print("-----")
                print(c_nu[0])
                print(c_nu_[0])
                print("diff")
                print(sum_i_, sum_j_)
                print("-------------------------")
            assert lim

    b1_cu    = torch.cat(inpts["b1_cu"], dim = 0)
    l1_cu    = torch.cat(inpts["l1_cu"], dim = 0)
    b2_cu    = torch.cat(inpts["b2_cu"], dim = 0)
    l2_cu    = torch.cat(inpts["l2_cu"], dim = 0)
    met_cu   = torch.cat(inpts["met_xy"], dim = 0)

    nu1_t = torch.cat(compare["nu1"], dim = 0)
    nu2_t = torch.cat(compare["nu2"], dim = 0)

    msk_t = nu1_t.sum(-1) != 0
    nu1_t = nu1_t[msk_t]
    nu2_t = nu2_t[msk_t]

    _cu = pyc.NuSol.NuNu(b1_cu, b2_cu, l1_cu, l2_cu, met_cu, masses, precision)
    nu1, nu2 = _cu[0].to(device = "cpu"), _cu[1].to(device = "cpu")

    msk = nu1.sum(-1) != 0
    nu1 = nu1[msk]
    nu2 = nu2[msk]

    msk1 = (nu1_t - nu1).sum(-1) != 0
    msk2 = (nu2_t - nu2).sum(-1) != 0
    assert msk1.sum(-1) == 0
    assert msk2.sum(-1) == 0

    # test speed
    multi = 200
    nEvents = sum([b1_cu.size(0) for k in range(multi)])
    b1_cu = torch.cat([b1_cu for k in range(multi)], dim = 0).clone()
    l1_cu = torch.cat([l1_cu for k in range(multi)], dim = 0).clone()
    b2_cu = torch.cat([b2_cu for k in range(multi)], dim = 0).clone()
    l2_cu = torch.cat([l2_cu for k in range(multi)], dim = 0).clone()
    met_cu = torch.cat([met_cu for k in range(multi)], dim = 0).clone()
    _cu = pyc.NuSol.NuNu(b1_cu, b2_cu, l1_cu, l2_cu, met_cu, masses, precision)

def test_nusol_base_tensor():
    x = loadSingle()
    ita = iter(x)
    inpt = {"bq" : [], "lep" : []}
    for i in range(len(x)):
        x_ = next(ita)
        lep, bquark = x_[1], x_[2]
        lep.cuda = False
        bquark.cuda = False

        lep_ = pyc.Transform.PxPyPzE(lep.ten)
        bquark_ = pyc.Transform.PxPyPzE(bquark.ten)
        inpt["bq"] += [bquark_]
        inpt["lep"] += [lep_]

        nu = NuSol(bquark.vec, lep.vec)
        truth = torch.tensor(nu.BaseMatrix)

        pred = pyc.NuSol.BaseMatrix(bquark_, lep_, masses.to("cpu"))
        ok = abs(truth - pred)/abs(truth)
        ok = ok > 0.1
        assert ok.sum(-1).sum(-1) == 0

    multi = 5
    inpt["bq"] = torch.cat(inpt["bq"], dim = 0)
    inpt["lep"] = torch.cat(inpt["lep"], dim = 0)
    inpt["bq"]  = torch.cat([inpt["bq"] for _ in range(multi)], dim = 0)
    inpt["lep"] = torch.cat([inpt["lep"] for _ in range(multi)], dim = 0)
    nEvents = inpt["lep"].size(0)
    _cu = pyc.NuSol.BaseMatrix(inpt["bq"], inpt["lep"], masses.to("cpu"))

def test_nusol_nu_tensor():
    x = loadSingle()
    ita = iter(x)

    lst = []
    inpt = []

    for i in range(len(x)):
        x_ = next(ita)
        ev, lep, bquark = x_[0], x_[1], x_[2]
        ev.cuda = False
        lep.cuda = False
        bquark.cuda = False

        nu = NuSol(bquark.vec, lep.vec, ev.vec)
        lst.append(torch.tensor(nu.M).view(-1, 3, 3))

        lep_ = pyc.Transform.PxPyPzE(lep.ten)
        bquark_ = pyc.Transform.PxPyPzE(bquark.ten)
        inpt.append([bquark_, lep_, ev.ten])

    truth = torch.cat(lst, 0)

    bquark_ = torch.cat([i[0] for i in inpt], 0)
    lep_    = torch.cat([i[1] for i in inpt], 0)
    ev_     = torch.cat([i[2] for i in inpt], 0)

    pred = pyc.NuSol.Nu(bquark_, lep_, ev_, masses.to("cpu"), S2.to("cpu"), -1)
    for i in range(len(truth)):
        tru = truth[i][truth[i] != 0]
        pr = pred[i][pred[i] != 0]
        if len(pr) == 0:
            assert len(tru) == 0
            continue
        x = abs(pr - tru)/tru > 1e-3
        assert x.sum(-1).sum(-1).sum(-1) == 0

def test_intersection_tensor():
    x = loadSingle()
    ita = iter(x)
    M_container = []
    U_container = []
    res = []

    for i in range(len(x)):
        x_ = next(ita)
        ev, lep, b = x_[0], x_[1], x_[2]
        ev.cuda = False
        lep.cuda = False
        b.cuda = False

        nu = NuSol(b.vec, lep.vec, ev.vec)
        unit = UnitCircle()
        points, diag = intersections_ellipses(nu.M, unit, precision)

        unit = torch.tensor(unit, device = "cpu", dtype = torch.float64)
        U_container.append(unit.view(-1, 3, 3))
        lep_ = pyc.Transform.PxPyPzE(lep.ten)
        bquark_ = pyc.Transform.PxPyPzE(b.ten)
        M = pyc.NuSol.Nu(bquark_, lep_, ev.ten, masses.to(device = "cpu"), S2.to(device = "cpu"), -1)
        M_container.append(M)

        pts, dig = pyc.Intersection(M, unit.view(-1, 3, 3), precision)
        res.append(pts.view(-1, 3))
        points_t = torch.tensor(np.array(points), device ="cpu", dtype = torch.float64)
        points_cu = pts.view(-1, 3)
        points_cu = points_cu[points_cu.sum(-1) != 0]
        points_t = points_t.view(-1, 3)
        if len(points_cu) == 0: assert len(points_t) == 0

        for pairs_t in points_t:
            lim = False
            for pairs in points_cu:
                sol = abs(pairs - pairs_t)
                sol = sol > 1e-4
                lim = sol.sum(-1).sum(-1) == 0
                if not lim: continue
                break

            if not lim:
                print("----->>> Failure <<< ----")
                print("@ -> ", i)
                print(points_t)
                print(points_cu)
                print("-------------------------")
            assert lim
    m = torch.cat(M_container, dim = 0)
    u = torch.cat(U_container, dim = 0)
    res_t = torch.cat(res, dim = 0)

    res_cu, b = pyc.NuSol.Intersection(m, u, precision)
    res_cu = res_cu.clone().view(-1, 3)
    res_cu = res_cu[res_cu.sum(-1) != 0]
    x = res_cu[res_cu != res_t]
    assert len(x) == 0

    # test speed
    multi = 100
    nEvents = sum([m.size(0) for k in range(multi)])
    m = torch.cat([m for k in range(multi)], dim = 0).clone()
    u = torch.cat([u for k in range(multi)], dim = 0).clone()
    pyc.NuSol.Intersection(m, u, precision)

def test_nu_tensor():

    x = loadSingle()
    ita = iter(x)
    compare = []
    inpts = {
            "b_cu"  : [], "lep_cu" : [],
            "ev_cu" : [], "m_cu"   : [],
            "s2" : []
    }

    for i in range(len(x)):
        x_ = next(ita)
        ev, lep, b = x_[0], x_[1], x_[2]
        ev.cuda = False
        lep.cuda = False
        b.cuda = False

        nu = SingleNu(b.vec, lep.vec, ev.vec)
        nu_t = torch.tensor(np.array(nu.nu), device = "cpu", dtype = torch.float64)

        lep_cu = pyc.Transform.PxPyPzE(lep.ten)
        b_cu   = pyc.Transform.PxPyPzE(b.ten)
        inpts["b_cu"].append(b_cu)
        inpts["lep_cu"].append(lep_cu)
        inpts["m_cu"].append(masses)
        inpts["ev_cu"].append(ev.ten)
        inpts["s2"].append(S2.view(-1, 2, 2))

        _cu, dia  = pyc.NuSol.Nu(
                b_cu, lep_cu, ev.ten,
                masses.to(device = "cpu"),
                S2.to(device = "cpu"), precision)
        nu_cu = _cu[0].to(device = "cpu").view(-1, 3)
        compare.append(nu_cu)
        if len(nu_cu) == 0: assert len(nu_t) == 0
        for pr_t in nu_t:
            lim = False
            for pr_cu in nu_cu:
                s = abs(pr_t - pr_cu)/pr_t > 10e-3
                s = s.sum(-1).sum(-1)
                if s != 0: continue
                lim = True
                break

            if not lim:
                print("----->>> Failure <<< ----")
                print("@ -> ", i)
                print(nu_t)
                print(nu_cu)
                print("-------------------------")
            assert lim

    b_cu = torch.cat(inpts["b_cu"], dim = 0).to(device = "cpu")
    lep_cu = torch.cat(inpts["lep_cu"], dim = 0).to(device = "cpu")
    ev_cu = torch.cat(inpts["ev_cu"], dim = 0).to(device = "cpu")
    mass_cu = torch.cat(inpts["m_cu"], dim = 0).to(device = "cpu")
    s2_cu = torch.cat(inpts["s2"], dim = 0).to(device = "cpu")
    _cu = pyc.NuSol.Nu(b_cu, lep_cu, ev_cu, masses.to(device = "cpu"), S2.to(device = "cpu"), precision)[0]
    _cu = _cu[_cu.sum(-1) != 0]

    t = torch.cat(compare, dim = 0)
    assert len(t[t - _cu > 1e-8]) == 0

    _cu = pyc.NuSol.Nu(b_cu, lep_cu, ev_cu, mass_cu, s2_cu, precision)[0]
    _cu = _cu[_cu.sum(-1) != 0]
    assert len(t[t - _cu > 1e-8]) == 0

def test_nunu_tensor():

    x = loadDouble()
    ita = iter(x)

    compare = {"nu1" : [], "nu2" : []}
    inpts = {
                "b1_cu" : [], "b2_cu" : [],
                "l1_cu" : [], "l2_cu" : [],
                "met_xy" : []
    }

    for i in range(len(x)):
        x_ = next(ita)
        ev, l1, l2, b1, b2 = x_
        ev.cuda = False
        l1.cuda = False
        l2.cuda = False
        b1.cuda = False
        b2.cuda = False



        metxy = ev.ten
        _b1 = pyc.Transform.PxPyPzE(b1.ten)
        _l1 = pyc.Transform.PxPyPzE(l1.ten)
        _b2 = pyc.Transform.PxPyPzE(b2.ten)
        _l2 = pyc.Transform.PxPyPzE(l2.ten)

        inpts["b1_cu"].append(_b1)
        inpts["b2_cu"].append(_b2)

        inpts["l1_cu"].append(_l1)
        inpts["l2_cu"].append(_l2)

        inpts["met_xy"].append(metxy)

        nunu_cu = pyc.NuSol.NuNu(_b1, _b2, _l1, _l2, metxy, masses.to(device = "cpu"), precision)
        c_nu, c_nu_ = nunu_cu[0], nunu_cu[1]
        compare["nu1"].append(c_nu.view(-1, 3))
        compare["nu2"].append(c_nu_.view(-1, 3))
        try: sols = DoubleNu((b1.vec, b2.vec), (l1.vec, l2.vec), ev).nunu_s
        except np.linalg.LinAlgError: sols = []

        t_nu  = torch.tensor(np.array([i for i, _ in sols]), dtype = torch.float64)
        t_nu_ = torch.tensor(np.array([j for _, j in sols]), dtype = torch.float64)
        if len(t_nu) != 0: assert len(c_nu[0]) > 0

        for t_nui, t_nuj in zip(t_nu, t_nu_):
            lim = False
            for c_nui, c_nuj in zip(c_nu[0], c_nu_[0]):
                sum_i = abs((t_nui - c_nui)/t_nui) > 0.1
                sum_j = abs((t_nuj - c_nuj)/t_nuj) > 0.1
                sum_i, sum_j = sum_i.sum(-1).sum(-1), sum_j.sum(-1).sum(-1)
                if sum_i != 0 or sum_j != 0: continue
                lim = True
                break

            if not lim:
                print("----->>> Failure <<< ----")
                print("@ -> ", i)
                print(t_nui)
                print(t_nuj)
                print("-----")
                print(c_nu[0])
                print(c_nu_[0])
                print("-------------------------")
            assert lim

    b1_cu    = torch.cat(inpts["b1_cu"], dim = 0)
    l1_cu    = torch.cat(inpts["l1_cu"], dim = 0)
    b2_cu    = torch.cat(inpts["b2_cu"], dim = 0)
    l2_cu    = torch.cat(inpts["l2_cu"], dim = 0)
    met_cu    = torch.cat(inpts["met_xy"], dim = 0)

    nu1_t = torch.cat(compare["nu1"], dim = 0)
    nu2_t = torch.cat(compare["nu2"], dim = 0)

    _cu = pyc.NuSol.NuNu(b1_cu, b2_cu, l1_cu, l2_cu, met_cu, masses.to(device = "cpu"), precision)
    nu1, nu2 = _cu[0], _cu[1]
    msk = nu1.sum(-1) != 0
    nu1 = nu1[msk]
    nu2 = nu2[msk]

    nu1_t = nu1_t[nu1_t.sum(-1) != 0]
    nu2_t = nu2_t[nu2_t.sum(-1) != 0]

    msk1 = (nu1_t - nu1).sum(-1) != 0
    msk2 = (nu2_t - nu2).sum(-1) != 0
    assert msk1.sum(-1) == 0
    assert msk2.sum(-1) == 0

    # test memory
    multi = 200
    nEvents = sum([b1_cu.size(0) for k in range(multi)])
    b1_cu = torch.cat([b1_cu for k in range(multi)], dim = 0).clone()
    l1_cu = torch.cat([l1_cu for k in range(multi)], dim = 0).clone()

    b2_cu = torch.cat([b2_cu for k in range(multi)], dim = 0).clone()
    l2_cu = torch.cat([l2_cu for k in range(multi)], dim = 0).clone()

    met_cu = torch.cat([met_cu for k in range(multi)], dim = 0).clone()
    _cu = pyc.NuSol.NuNu(b1_cu, b2_cu, l1_cu, l2_cu, met_cu, masses.to(device = "cpu"), precision)

if __name__ == "__main__":
    test_nusol_base_cuda()
    test_nusol_nu_cuda()
    test_intersection_cuda()
    test_nu_cuda()
    test_nunu_cuda()

    test_nusol_base_tensor()
    test_nusol_nu_tensor()
    test_intersection_tensor()
    test_nu_tensor()
    test_nunu_tensor()
    pass
