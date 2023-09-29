is_cuda = True
try:
    from AnalysisG.Events import Event
    from AnalysisG import Analysis
    from conftest import clean_dir
    import torch

    from neutrino_reconstruction.NeutrinoSolutionDeconstruct import *
    import PyC.Transform.Floats as F
    import PyC.Transform.Tensors as T

    import PyC.Physics.Tensors.Cartesian as TC
    import PyC.Physics.Tensors.Polar as TP
    import PyC.Operators.Tensors as TO
    import PyC.NuSol.Tensors as NuT

    import PyC.Transform.CUDA as C
    import PyC.Physics.CUDA.Cartesian as CC
    import PyC.Physics.CUDA.Polar as CP
    import PyC.Operators.CUDA as CO
    import PyC.NuSol.CUDA as NuC

except:
    is_cuda = False

import math
from time import time
from check import *

Files = {
    "./samples/sample1": ["smpl1.root"],
    "./samples/sample2": ["smpl1.root", "smpl2.root", "smpl3.root"],
}


def _MakeSample():
    Ana = Analysis()
    Ana.ProjectName = "NeutrinoProject"
    Ana.InputSample("", Files)
    Ana.Event = Event
    Ana.EventCache = True
    Ana.PurgeCache = True
    Ana.Launch
    return Ana


def _transformation():
    Ana = _MakeSample()

    _cart = []
    _polar = []
    for i in Ana:
        top = i.Tops
        if len(top) != 4:
            continue

        for t in top:
            assert AssertEquivalence(t.px, F.Px(t.pt, t.phi))
            assert AssertEquivalence(t.py, F.Py(t.pt, t.phi))
            assert AssertEquivalence(t.pz, F.Pz(t.pt, t.eta))

            assert AssertEquivalence(t.pt, F.PT(t.px, t.py))
            assert AssertEquivalence(t.eta, F.Eta(t.px, t.py, t.pz))
            assert AssertEquivalence(t.phi, F.Phi(t.px, t.py))

            assert AssertEquivalenceRecursive(
                [t.pt, t.eta, t.phi], F.PtEtaPhi(t.px, t.py, t.pz)
            )

            t_px, t_py, t_pz = MakeTensor(t.px), MakeTensor(t.py), MakeTensor(t.pz)
            t_pt, t_eta, t_phi = MakeTensor(t.pt), MakeTensor(t.eta), MakeTensor(t.phi)

            assert AssertEquivalence(t.pt, T.PT(t_px, t_py))
            assert AssertEquivalence(t.eta, T.Eta(t_px, t_py, t_pz))
            assert AssertEquivalence(t.phi, T.Phi(t_px, t_py))

            lc = [t.px, t.py, t.pz]
            assert AssertEquivalenceList(lc, F.PxPyPz(t.pt, t.eta, t.phi))
            assert AssertEquivalenceList(lc, T.PxPyPz(t_pt, t_eta, t_phi)[0])

            lp = [t.pt, t.eta, t.phi]
            assert AssertEquivalenceList(lp, F.PtEtaPhi(t.px, t.py, t.pz))
            assert AssertEquivalenceList(lp, T.PtEtaPhi(t_px, t_py, t_pz)[0])

            for c in t.Children:
                _polar.append([c.pt, c.eta, c.phi])
                _cart.append([c.px, c.py, c.pz])

            if is_cuda == False:
                continue
            c_pt, c_eta, c_phi = (
                MakeTensor(t.pt, "cuda"),
                MakeTensor(t.eta, "cuda"),
                MakeTensor(t.phi, "cuda"),
            )
            c_px, c_py, c_pz = (
                MakeTensor(t.px, "cuda"),
                MakeTensor(t.py, "cuda"),
                MakeTensor(t.pz, "cuda"),
            )

            assert AssertEquivalence(t.px, C.Px(c_pt, c_phi))
            assert AssertEquivalence(t.py, C.Py(c_pt, c_phi))
            assert AssertEquivalence(t.pz, C.Pz(c_pt, c_eta))

            assert AssertEquivalence(t.pt, C.PT(c_px, c_py)[0])
            assert AssertEquivalence(t.eta, C.Eta(c_px, c_py, c_pz)[0])
            assert AssertEquivalence(t.phi, C.Phi(c_px, c_py)[0])

            assert AssertEquivalenceList(lc, C.PxPyPz(c_pt, c_eta, c_phi)[0])
            assert AssertEquivalenceList(lp, C.PtEtaPhi(c_px, c_py, c_pz)[0])

    clean_dir()
    if is_cuda == False:
        return
    # ===== Test the performance difference ===== #
    CPU = torch.tensor(_polar, device="cpu")
    CUDA = torch.tensor(_cart, device="cuda")
    c_pt, c_eta, c_phi = CUDA[:, 0].clone(), CUDA[:, 1].clone(), CUDA[:, 2].clone()

    t1 = time()
    cpu_r = T.PxPyPz(CPU[:, 0], CPU[:, 1], CPU[:, 2])
    diff1 = time() - t1

    t1 = time()
    cuda_r = C.PxPyPz(c_pt, c_eta, c_phi)
    diff2 = time() - t1
    AssertEquivalenceRecursive(cpu_r, cuda_r)
    print("--- Testing Performance Between C++ and CUDA of PxPyPz ---")
    print("Speed Factor (> 1 is better): ", diff1 / diff2)

    CPU = torch.tensor(_cart, device="cpu")
    CUDA = torch.tensor(_cart, device="cuda")
    c_px, c_py, c_pz = CUDA[:, 0].clone(), CUDA[:, 1].clone(), CUDA[:, 2].clone()

    t1 = time()
    cpu_r = T.PtEtaPhi(CPU[:, 0], CPU[:, 1], CPU[:, 2])
    diff1 = time() - t1

    t1 = time()
    cuda_r = C.PtEtaPhi(c_px, c_py, c_pz)
    diff2 = time() - t1
    AssertEquivalenceRecursive(cpu_r, cuda_r)
    print("--- Testing Performance Between C++ and CUDA of PtEtaPhi ---")
    print("Speed Factor (> 1 is better): ", diff1 / diff2)
    clean_dir()


def _physics():
    Ana = _MakeSample()
    _x, _y, _z, _e = [], [], [], []
    _x1, _y1, _z1, _e1 = [], [], [], []

    pt, eta, phi, e = [], [], [], []
    pt1, eta1, phi1, e1 = [], [], [], []
    deltaR = []
    for event in Ana:
        top = event.Tops[0]
        top2 = event.Tops[1]
        tx, ty, tz, te = ParticleToTorch(top, "cuda" if is_cuda else "cpu")
        top_r = ParticleToVector(top)
        theta_r = top_r.theta
        theta_p = TC.Theta(tx, ty, tz)
        assert AssertEquivalenceRecursive([[theta_r]], theta_p)

        p_r = math.sqrt(top.px**2 + top.py**2 + top.pz**2)
        p_p = TC.P(tx, ty, tz)
        assert AssertEquivalenceRecursive([[p_r]], p_p)

        beta_r = top_r.beta
        beta_p = TC.Beta(tx, ty, tz, te)
        assert AssertEquivalenceRecursive([[beta_r]], beta_p)

        m_r = top_r.M
        m_p = TC.M(tx, ty, tz, te)
        assert AssertEquivalenceRecursive([[m_r]], m_p)

        mt_r = top_r.Mt
        mt_p = TC.Mt(tz, te)
        assert AssertEquivalenceRecursive([[mt_r]], mt_p)

        for k in range(100):
            _x.append([top.px]), _y.append([top.py])
            _z.append([top.pz]), _e.append([top.e])

            _x1.append([top2.px]), _y1.append([top2.py])
            _z1.append([top2.pz]), _e1.append([top2.e])

            pt.append([top.pt]), eta.append([top.eta])
            phi.append([top.phi]), e.append([top.e])

            pt1.append([top2.pt]), eta1.append([top2.eta])
            phi1.append([top2.phi]), e1.append([top2.e])
            deltaR.append([top.DeltaR(top2)])

    clean_dir()
    if is_cuda == False:
        return

    print(" ======= Cartesian stuff ======= ")
    p_x = torch.tensor(_x, device="cuda")
    p_y = torch.tensor(_y, device="cuda")
    p_z = torch.tensor(_z, device="cuda")
    p_e = torch.tensor(_e, device="cuda")

    p_x1 = torch.tensor(_x1, device="cuda")
    p_y1 = torch.tensor(_y1, device="cuda")
    p_z1 = torch.tensor(_z1, device="cuda")
    p_e1 = torch.tensor(_e1, device="cuda")

    PerformanceInpt(TC.P, CC.P, p_x, p_y, p_z)
    PerformanceInpt(TC.P2, CC.P2, p_x, p_y, p_z)
    print("")
    PerformanceInpt(TC.Beta, CC.Beta, p_x, p_y, p_z, p_e)
    PerformanceInpt(TC.Beta2, CC.Beta2, p_x, p_y, p_z, p_e)
    print("")
    PerformanceInpt(TC.M, CC.M, p_x, p_y, p_z, p_e)
    PerformanceInpt(TC.M2, CC.M2, p_x, p_y, p_z, p_e)
    print("")
    PerformanceInpt(TC.Mt, CC.Mt, p_z, p_e)
    PerformanceInpt(TC.Mt2, CC.Mt2, p_z, p_e)
    print("")
    PerformanceInpt(TC.Theta, CC.Theta, p_x, p_y, p_z)
    PerformanceInpt(TC.DeltaR, CC.DeltaR, p_x, p_x1, p_y, p_y1, p_z, p_z1)
    print("")

    print(" ======= Polar stuff ======= ")
    _pt = torch.tensor(pt, device="cuda")
    _eta = torch.tensor(eta, device="cuda")
    _phi = torch.tensor(phi, device="cuda")
    _e = torch.tensor(e, device="cuda")

    _pt2 = torch.tensor(pt1, device="cuda")
    _eta2 = torch.tensor(eta1, device="cuda")
    _phi2 = torch.tensor(phi1, device="cuda")
    _e2 = torch.tensor(e1, device="cuda")
    _dr = torch.tensor(deltaR, device="cuda")

    PerformanceInpt(TP.P, CP.P, _pt, _eta, _phi)
    PerformanceInpt(TP.P2, CP.P2, _pt, _eta, _phi)
    print("")
    PerformanceInpt(TP.Beta, CP.Beta, _pt, _eta, _phi, _e)
    PerformanceInpt(TP.Beta2, CP.Beta2, _pt, _eta, _phi, _e)
    print("")
    PerformanceInpt(TP.M, CP.M, _pt, _eta, _phi, _e)
    PerformanceInpt(TP.M2, CP.M2, _pt, _eta, _phi, _e)
    print("")
    PerformanceInpt(TP.Mt, CP.Mt, _pt, _eta, _phi)
    PerformanceInpt(TP.Mt2, CP.Mt2, _pt, _eta, _phi)
    print("")
    PerformanceInpt(TP.Theta, CP.Theta, _pt, _eta, _phi)
    PerformanceInpt(TP.DeltaR, CP.DeltaR, _eta, _eta2, _phi, _phi2)
    print("")
    assert AssertEquivalenceRecursive(deltaR, TP.DeltaR(_eta, _eta2, _phi, _phi2))
    print("passed")


def _operators():
    if is_cuda == False:
        return
    device = "cuda"
    Matrix = [[i * j for i in range(100)] for j in range(10)]
    T_matrix = torch.tensor(Matrix, device=device, dtype=torch.float64)

    t1 = time()
    exp = TO.Dot(T_matrix, T_matrix)
    diff1 = time() - t1

    t1 = time()
    Exp = CO.Dot(T_matrix, T_matrix)
    diff2 = time() - t1

    assert AssertEquivalenceRecursive(Exp.tolist(), exp.tolist())
    print("--- Testing Performance Between C++ and CUDA of DOT ---")
    print("Speed Factor (> 1 is better): ", diff1 / diff2)

    Matrix = [[i for i in range(3)] for j in range(100000)]
    T1_matrix = torch.tensor(Matrix, device=device, dtype=torch.float64)

    Matrix = [[j * i + 1 for i in range(3)] for j in range(100000)]
    T2_matrix = torch.tensor(Matrix, device=device, dtype=torch.float64)

    t1 = time()
    exp = TO.CosTheta(T1_matrix, T2_matrix)
    diff1 = time() - t1

    t1 = time()
    Exp = CO.CosTheta(T1_matrix, T2_matrix)
    diff2 = time() - t1
    print(diff1, diff2)

    assert AssertEquivalenceRecursive(Exp.tolist(), exp.tolist())
    print("--- Testing Performance Between C++ and CUDA of CosTheta ---")
    print("Speed Factor (> 1 is better): ", diff1 / diff2)

    import math

    Matrix = [[math.pi / (j + 1) for i in range(1)] for j in range(100000)]
    T1_matrix = torch.tensor(Matrix, device=device, dtype=torch.float64)

    t1 = time()
    exp = TO.Rx(T1_matrix)
    diff1 = time() - t1

    t1 = time()
    Exp = CO.Rx(T1_matrix)
    diff2 = time() - t1

    print(diff1, diff2)
    assert AssertEquivalenceRecursive(Exp.tolist(), exp.tolist())
    print("--- Testing Performance Between C++ and CUDA of Rx ---")
    print("Speed Factor (> 1 is better): ", diff1 / diff2)

    t1 = time()
    exp = TO.Ry(T1_matrix)
    diff1 = time() - t1

    t1 = time()
    Exp = CO.Ry(T1_matrix)
    diff2 = time() - t1

    assert AssertEquivalenceRecursive(Exp.tolist(), exp.tolist())
    print("--- Testing Performance Between C++ and CUDA of Ry ---")
    print("Speed Factor (> 1 is better): ", diff1 / diff2)

    t1 = time()
    exp = TO.Rz(T1_matrix)
    diff1 = time() - t1

    t1 = time()
    Exp = CO.Rz(T1_matrix)
    diff2 = time() - t1

    assert AssertEquivalenceRecursive(Exp.tolist(), exp.tolist())
    print("--- Testing Performance Between C++ and CUDA of Rz ---")
    print("Speed Factor (> 1 is better): ", diff1 / diff2)

    T1_matrix = torch.tensor(
        [[i for i in range(3)] for j in range(1)], device="cuda", dtype=torch.float64
    )
    x = CO.Rz(T1_matrix)
    y = torch.tensor(
        [[[k for i in range(1)] for k in range(3)] for t in range(1)],
        device="cuda",
        dtype=torch.float64,
    )

    t1 = time()
    c = torch.matmul(x, y)
    diff1 = time() - t1

    t1 = time()
    l = CO.Mul(x, y)
    diff2 = time() - t1

    assert AssertEquivalenceRecursive(c.tolist(), l.tolist())
    print("--- Testing Performance Between C++ and CUDA of Mul ---")
    print("Speed Factor (> 1 is better): ", diff1 / diff2)

    y = torch.tensor(
        [[[k / (1 + t) for i in range(3)] for k in range(3)] for t in range(100)],
        device="cuda",
        dtype=torch.float64,
    )
    x = torch.tensor(
        [[[i * k for i in range(3)] for k in range(3)] for t in range(100)],
        device="cuda",
        dtype=torch.float64,
    )
    diff = [[], []]
    for t in range(10000):
        t1 = time()
        c = torch.matmul(x, y)
        t2 = time()
        diff1 = t2 - t1
        diff[0].append(diff1)

        t1 = time()
        l = CO.Mul(x, y)
        t2 = time()
        diff2 = t2 - t1
        diff[1].append(diff2)

    assert AssertEquivalenceRecursive(c.tolist(), l.tolist())
    print("--- Testing Performance Between C++ and CUDA of MatMul ---")
    print("Speed Factor (> 1 is better): ", (sum(diff[0])) / sum(diff[1]))

    m = torch.tensor(
        [
            [[1 / (i + 1), 4, 7 / (i + 1)], [3, i, 5], [-1 / (i + 1), 9, 1]]
            for i in range(10000)
        ],
        dtype=torch.float64,
        device="cuda",
    )
    diff = [[], []]
    for t in range(10000):
        t1 = time()
        c = torch.inverse(m)
        t2 = time()
        diff1 = t2 - t1
        diff[0].append(diff1)

        t1 = time()
        l = CO.Inv(m)
        t2 = time()
        diff2 = t2 - t1
        diff[1].append(diff2)

    assert AssertEquivalenceRecursive(c.tolist(), l.tolist())
    print("--- Testing Performance Between C++ and CUDA of Inverse ---")
    print("Speed Factor (> 1 is better): ", (sum(diff[0])) / sum(diff[1]))


def _single_nu():
    Ana = Analysis()
    Ana.InputSample("SingleLepton", "./samples/single_lepton")
    Ana.Event = Event
    Ana.EventCache = True
    Ana.PurgeCache = True
    Ana.Verbose = 2
    Ana.Launch

    out = {"b": [], "nu": [], "lep": [], "metx": [], "mety": [], "t": []}
    it = 0
    for i in Ana:
        lep = [x for x in i.Tops if x.LeptonicDecay]
        if len(lep) == 1:
            children = {abs(c.pdgid): c for c in lep[0].Children}
            b = children[5]
            nu = [children[c] for c in children if c in [12, 14, 16]][0]
            lep_ = [children[c] for c in children if c in [11, 13, 15]][0]
            out["b"].append(b)
            out["nu"].append(nu)
            out["lep"].append(lep_)
            out["t"].append(lep[0])
            out["metx"].append(F.Px(i.met, i.met_phi))
            out["mety"].append(F.Py(i.met, i.met_phi))
            it += 1

    Ana.rm("UNTITLED")
    for i in range(it):
        failed = False
        b, nu, lep, t, metx, mety = [
            out[key][i] for key in ["b", "nu", "lep", "t", "metx", "mety"]
        ]
        bv, lepv = ParticleToVector(b), ParticleToVector(lep)

        sol = singleNeutrinoSolution(
            bv,
            lepv,
            (metx, mety),
            [[100, 0], [0, 100]],
            (nu + lep).Mass ** 2,
            t.Mass**2,
        )
        try:
            failed = sol.nu
        except IndexError:
            failed = True

        skip, solT, chi2, other = NuT.NuDoublePxPyPzE(
            b.px,
            b.py,
            b.pz,
            b.e,
            lep.px,
            lep.py,
            lep.pz,
            lep.e,
            metx,
            mety,
            100,
            0,
            0,
            100,
            t.Mass,
            (nu + lep).Mass,
            0,
            1e-8,
        )
        if isinstance(failed, bool) and failed == True:
            continue
        elif sum(solT.tolist()[0]) == 0 and not isinstance(failed, bool):
            print("->", failed, solT.tolist()[0])
            continue
        if not AssertEquivalenceList(solT.tolist()[0], failed):
            other = other.tolist()[0]
            alternative = len([True for s in other if AssertEquivalenceList(failed, s)])
            assert alternative > 0
            continue
        assert AssertEquivalenceList(solT.tolist()[0], failed)


def _double_nu():
    if is_cuda == False:
        return

    Ana = Analysis()
    Ana.InputSample("Dilepton", "./samples/dilepton")
    Ana.Event = Event
    Ana.EventCache = True
    Ana.PurgeCache = True
    Ana.Verbose = 2
    Ana.Launch

    out = {"b": [], "nu": [], "lep": [], "metx": [], "mety": [], "t": []}
    it = 0
    for i in Ana:
        lep = [x for x in i.Tops if x.LeptonicDecay]
        if len(lep) == 2:
            children = [{abs(c.pdgid): c for c in t.Children} for t in lep]
            b, b_ = children[0][5], children[1][5]
            nu, nu_ = [
                children[t][p]
                for t in range(len(children))
                for p in children[t]
                if p in [12, 14, 16]
            ]
            l, l_ = [
                children[t][p]
                for t in range(len(children))
                for p in children[t]
                if p in [11, 13, 15]
            ]
            out["b"].append([b, b_])
            out["nu"].append([nu, nu_])
            out["lep"].append([l, l_])
            out["t"].append([lep[0], lep[1]])
            out["metx"].append(F.Px(i.met, i.met_phi))
            out["mety"].append(F.Py(i.met, i.met_phi))
            it += 1

    clean_dir()
    errorMargin = 2  # Allow for a 2% delta between the original and new implementation
    for i in range(it):
        failed = False
        metx, mety = [out[key][i] for key in ["metx", "mety"]]
        b, nu, lep, t = [out[key][i][0] for key in ["b", "nu", "lep", "t"]]
        b_, nu_, lep_, t_ = [out[key][i][1] for key in ["b", "nu", "lep", "t"]]

        bv, lepv = ParticleToVector(b), ParticleToVector(lep)
        bv_, lepv_ = ParticleToVector(b_), ParticleToVector(lep_)

        try:
            sol = doubleNeutrinoSolutions(
                (bv, bv_),
                (lepv, lepv_),
                (metx, mety),
                (nu + lep).Mass ** 2,
                t.Mass**2,
            )
            failed = sol.nunu_s
            leasq = sol.lsq
        except IndexError:
            failed = True
        except:
            failed = True

        bv, lepv = ParticleToTensor(b), ParticleToTensor(lep)
        bv_, lepv_ = ParticleToTensor(b_), ParticleToTensor(lep_)
        metx, mety = MakeTensor(metx, "cuda"), MakeTensor(mety, "cuda")
        mW, mT, mNu = (
            MakeTensor((nu + lep).Mass, "cuda"),
            MakeTensor(t.Mass, "cuda"),
            MakeTensor(0, "cuda"),
        )

        val = NuT.NuNuPxPyPzE(bv, bv_, lepv, lepv_, metx, mety, mT, mW, mNu, 1e-8)

        if len(val) == 3 and isinstance(failed, bool):
            continue
        skip, solT1, solT2, _, _, _, _, _ = val
        skip, solT1, solT2 = skip.tolist()[0], solT1.tolist()[0], solT2.tolist()[0]

        if skip and isinstance(failed, bool):
            continue
        sol1, sol2 = [s.tolist() for s, _ in failed], [s.tolist() for _, s in failed]
        solT1, solT2 = [k for k in solT1 if sum(k) != 0], [
            k for k in solT2 if sum(k) != 0
        ]

        try_ = True
        for s1, s2 in zip(sol1, sol2):
            for sT1, sT2 in zip(solT1, solT2):
                if not AssertEquivalenceList(
                    s1, sT1, errorMargin
                ) or not AssertEquivalenceList(s2, sT2, errorMargin):
                    continue
                try_ = False
                break
            if try_ == False:
                break
        if not try_:
            continue
        if leasq:
            continue
        assert False


def _speed():
    if is_cuda == False:
        return

    Ana = Analysis()
    Ana.InputSample("DiLepton", "./samples/dilepton")
    Ana.Event = Event
    Ana.EventCache = True
    Ana.PurgeCache = True
    Ana.Verbose = 2
    Ana.Launch
    its = 1
    it = 0

    vl = {"b": [], "lep": [], "nu": [], "ev": [], "t": []}
    for ev in Ana:
        tops = [t for t in ev.Tops if t.LeptonicDecay]

        if len(tops) == 2:
            k = ParticleCollectors(ev)
            vl["b"].append([k[0][0], k[1][0]])
            vl["lep"].append([k[0][1], k[1][1]])
            vl["nu"].append([k[0][2], k[1][2]])
            vl["t"].append([k[0][3], k[1][3]])
            vl["ev"].append(ev)
            it += 1

    clean_dir()
    T = SampleTensor(
        vl["b"], vl["lep"], vl["ev"], vl["t"], "cuda", [[100, 0], [0, 100]]
    )
    R = SampleVector(vl["b"], vl["lep"], vl["ev"], vl["t"])
    print(
        "======================= Testing Speed of Single Neutrino Reconstruction ==================="
    )
    diff = [[], [], []]
    for i in range(its):
        t1 = time()
        for r, t in zip(R, T):
            b, mu = r[0], r[1]
            met_x, met_y = r[4], r[5]
            mT, mW, mNu = r[6], r[7], r[8]
            try:
                sol = singleNeutrinoSolution(
                    b, mu, (met_x, met_y), [[100, 0], [0, 100]], mW**2, mT**2
                )
                sol.nu
            except:
                continue
        t2 = time()
        diff[0].append(t2 - t1)

    for t in range(its):
        t1 = time()
        t_sol = NuT.NuPtEtaPhiE(
            T.b, T.mu, T.met, T.phi, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12
        )
        t2 = time()
        diff1 = t2 - t1
        diff[1].append(diff1)

    for t in range(its):
        t1 = time()
        t_solC = NuC.NuPtEtaPhiE(
            T.b, T.mu, T.met, T.phi, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12
        )
        t2 = time()
        diff2 = t2 - t1
        diff[2].append(diff2)

    print(sum(diff[0]), sum(diff[1]))
    print("--- Testing Performance Between Original and C++ of Nu ---")
    print("Speed Factor (> 1 is better): ", (sum(diff[0])) / sum(diff[1]))

    print(sum(diff[0]), sum(diff[2]))
    print("--- Testing Performance Between Original and CUDA of Nu ---")
    print("Speed Factor (> 1 is better): ", (sum(diff[0])) / sum(diff[2]))

    print(sum(diff[1]), sum(diff[2]))
    print("--- Testing Performance Between C++ and CUDA of Nu ---")
    print("Speed Factor (> 1 is better): ", (sum(diff[1])) / sum(diff[2]))

    print(
        "======================= Testing Speed of Double Neutrino Reconstruction ==================="
    )
    diff = [[], [], []]
    for i in range(its):
        t1 = time()
        for r, t in zip(R, T):
            b, mu = r[0], r[1]
            _b, _mu = r[2], r[3]
            met_x, met_y = r[4], r[5]
            mT, mW, mNu = r[6], r[7], r[8]
            try:
                sol = doubleNeutrinoSolutions(
                    (_b, b), (_mu, mu), (met_x, met_y), mW**2, mT**2
                )
                sol.nunu_s
            except:
                continue
        t2 = time()
        diff[0].append(t2 - t1)

    b = torch.cat([T.b for i in range(its)], 0)
    b_ = torch.cat([T.b_ for i in range(its)], 0)
    mu = torch.cat([T.mu for i in range(its)], 0)
    mu_ = torch.cat([T.mu_ for i in range(its)], 0)
    met = torch.cat([T.met for i in range(its)], 0)
    phi = torch.cat([T.phi for i in range(its)], 0)
    mT = torch.cat([T.mT for i in range(its)], 0)
    mW = torch.cat([T.mW for i in range(its)], 0)
    mN = torch.cat([T.mN for i in range(its)], 0)

    t1 = time()
    t_sol = NuT.NuNuPtEtaPhiE(b, b_, mu, mu_, met, phi, mT, mW, mN, 1e-12)
    t2 = time()
    diff1 = t2 - t1
    diff[1].append(diff1)

    t1 = time()
    t_solC = NuC.NuNuPtEtaPhiE(b, b_, mu, mu_, met, phi, mT, mW, mN, 1e-12)
    t2 = time()
    diff2 = t2 - t1
    diff[2].append(diff2)

    print(sum(diff[0]), sum(diff[1]))
    print("--- Testing Performance Between Original and C++ of NuNu ---")
    print("Speed Factor (> 1 is better): ", (sum(diff[0])) / sum(diff[1]))

    print("--- Testing Performance Between Original and CUDA of NuNu ---")
    print("Speed Factor (> 1 is better): ", (sum(diff[0])) / sum(diff[2]))

    print("--- Testing Performance Between C++ and CUDA of NuNu ---")
    print("Speed Factor (> 1 is better): ", (sum(diff[1])) / sum(diff[2]))


def _version_consistency():
    if is_cuda == False:
        return

    Ana = Analysis()
    Ana.InputSample("DiLepton", "./samples/dilepton")
    Ana.Event = Event
    Ana.EventCache = True
    Ana.PurgeCache = True
    Ana.Verbose = 2
    Ana.Launch

    it = 0
    vl = {"b": [], "lep": [], "nu": [], "ev": [], "t": []}
    for ev in Ana:
        tops = [t for t in ev.Tops if t.LeptonicDecay]
        if len(tops) != 2:
            continue
        k = ParticleCollectors(ev)
        vl["b"].append([k[0][0], k[1][0]])
        vl["lep"].append([k[0][1], k[1][1]])
        vl["nu"].append([k[0][2], k[1][2]])
        vl["t"].append([k[0][3], k[1][3]])
        vl["ev"].append(ev)
        it += 1

    clean_dir()
    b1c = MakeTensor_(vl["b"], 0)
    b2c = MakeTensor_(vl["b"], 1)
    mu1c = MakeTensor_(vl["lep"], 0)
    mu2c = MakeTensor_(vl["lep"], 1)

    metx = torch.tensor(
        [[F.Px(i.met, i.met_phi) / 1000] for i in vl["ev"]],
        dtype=torch.float64,
        device="cuda",
    )
    mety = torch.tensor(
        [[F.Py(i.met, i.met_phi) / 1000] for i in vl["ev"]],
        dtype=torch.float64,
        device="cuda",
    )
    T = SampleTensor(
        vl["b"], vl["lep"], vl["ev"], vl["t"], "cuda", [[100, 0], [0, 100]]
    )

    # ------------------ Single Neutrino Reconstruction -------------------------- #
    sol_tP = NuC.NuPtEtaPhiE(
        T.b, T.mu, T.met, T.phi, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12
    )
    sol_tC = NuC.NuPxPyPzE(
        b1c, mu1c, metx, mety, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12
    )
    AssertEquivalenceRecursive(sol_tC[1].tolist(), sol_tP[1].tolist(), 0.01)

    Pb_l, Pmu_l, Pmet_l = [], [], []
    Cb_l, Cmu_l, Cmet_l = [], [], []
    met_lS, mass_l = [], []

    for i in range(len(sol_tP[0])):
        b, mu, ev = vl["b"][i][0], vl["lep"][i][0], vl["ev"][i]
        _solP = NuC.NuDoublePtEtaPhiE(
            b.pt / 1000,
            b.eta,
            b.phi,
            b.e / 1000,
            mu.pt / 1000,
            mu.eta,
            mu.phi,
            mu.e / 1000,
            ev.met / 1000,
            ev.met_phi,
            100,
            0,
            0,
            100,
            vl["t"][i][0].Mass / 1000,
            80.385,
            0,
            1e-12,
        )

        _solC = NuC.NuDoublePxPyPzE(
            b.px / 1000,
            b.py / 1000,
            b.pz / 1000,
            b.e / 1000,
            mu.px / 1000,
            mu.py / 1000,
            mu.pz / 1000,
            mu.e / 1000,
            F.Px(ev.met, ev.met_phi) / 1000,
            F.Py(ev.met, ev.met_phi) / 1000,
            100,
            0,
            0,
            100,
            vl["t"][i][0].Mass / 1000,
            80.385,
            0,
            1e-12,
        )
        assert AssertEquivalenceRecursive(_solP[1].tolist(), _solC[1].tolist(), 0.01)

        Pb_l.append([b.pt / 1000, b.eta, b.phi, b.e / 1000])
        Pmu_l.append([mu.pt / 1000, mu.eta, mu.phi, mu.e / 1000])
        Pmet_l.append([ev.met / 1000, ev.met_phi])

        Cb_l.append([b.px / 1000, b.py / 1000, b.pz / 1000, b.e / 1000])
        Cmu_l.append([mu.px / 1000, mu.py / 1000, mu.pz / 1000, mu.e / 1000])
        Cmet_l.append(
            [F.Px(ev.met, ev.met_phi) / 1000, F.Py(ev.met, ev.met_phi) / 1000]
        )

        met_lS.append([100, 0, 0, 100])
        mass_l.append([vl["t"][i][0].Mass / 1000, 80.385, 0])

    _solPL = NuC.NuListPtEtaPhiE(Pb_l, Pmu_l, Pmet_l, met_lS, mass_l, 1e-12)
    _solCL = NuC.NuListPxPyPzE(Cb_l, Cmu_l, Cmet_l, met_lS, mass_l, 1e-12)

    assert AssertEquivalenceRecursive(sol_tP[1].tolist(), _solCL[1].tolist(), 0.1)
    assert AssertEquivalenceRecursive(_solPL[1].tolist(), _solCL[1].tolist(), 0.1)

    # ------------------ Double Neutrino Reconstruction -------------------------- #
    sol_tP = NuC.NuNuPtEtaPhiE(
        T.b, T.b_, T.mu, T.mu_, T.met, T.phi, T.mT, T.mW, T.mN, 1e-12
    )
    sol_tC = NuC.NuNuPxPyPzE(b1c, b2c, mu1c, mu2c, metx, mety, T.mT, T.mW, T.mN, 1e-12)
    for i, j in zip(sol_tC[3], sol_tP[3]):
        assert AssertSimilarSets(i.tolist(), j.tolist(), 1)
    for i, j in zip(sol_tC[4], sol_tP[4]):
        assert AssertSimilarSets(i.tolist(), j.tolist(), 1)

    Pb, Pmu, Pmet = [], [], []
    Pb_, Pmu_ = [], []

    Cb, Cmu, Cmet = [], [], []
    Cb_, Cmu_ = [], []

    it = 0
    for i in range(len(sol_tP[0])):
        b, mu, ev = vl["b"][i][0], vl["lep"][i][0], vl["ev"][i]
        b_, mu_ = vl["b"][i][1], vl["lep"][i][1]

        Pb.append([b.pt / 1000, b.eta, b.phi, b.e / 1000])
        Pb_.append([b_.pt / 1000, b_.eta, b_.phi, b_.e / 1000])

        Pmu.append([mu.pt / 1000, mu.eta, mu.phi, mu.e / 1000])
        Pmu_.append([mu_.pt / 1000, mu_.eta, mu_.phi, mu_.e / 1000])

        Pmet.append([ev.met / 1000, ev.met_phi])

        Cb.append([b.px / 1000, b.py / 1000, b.pz / 1000, b.e / 1000])
        Cb_.append([b_.px / 1000, b_.py / 1000, b_.pz / 1000, b_.e / 1000])

        Cmu.append([mu.px / 1000, mu.py / 1000, mu.pz / 1000, mu.e / 1000])
        Cmu_.append([mu_.px / 1000, mu_.py / 1000, mu_.pz / 1000, mu_.e / 1000])

        Cmet.append([F.Px(ev.met, ev.met_phi) / 1000, F.Py(ev.met, ev.met_phi) / 1000])

        _solP = NuC.NuNuDoublePtEtaPhiE(
            Pb[-1][0],
            Pb[-1][1],
            Pb[-1][2],
            Pb[-1][3],
            Pb_[-1][0],
            Pb_[-1][1],
            Pb_[-1][2],
            Pb_[-1][3],
            Pmu[-1][0],
            Pmu[-1][1],
            Pmu[-1][2],
            Pmu[-1][3],
            Pmu_[-1][0],
            Pmu_[-1][1],
            Pmu_[-1][2],
            Pmu_[-1][3],
            Pmet[-1][0],
            Pmet[-1][1],
            mass_l[i][0],
            mass_l[i][1],
            mass_l[i][2],
            1e-12,
        )
        if _solP[0]:
            continue
        assert AssertSimilarSets(sol_tP[3][it].tolist(), _solP[3][0].tolist(), 1)
        it += 1

        _solC = NuC.NuNuDoublePxPyPzE(
            Cb[-1][0],
            Cb[-1][1],
            Cb[-1][2],
            Cb[-1][3],
            Cb_[-1][0],
            Cb_[-1][1],
            Cb_[-1][2],
            Cb_[-1][3],
            Cmu[-1][0],
            Cmu[-1][1],
            Cmu[-1][2],
            Cmu[-1][3],
            Cmu_[-1][0],
            Cmu_[-1][1],
            Cmu_[-1][2],
            Cmu_[-1][3],
            Cmet[-1][0],
            Cmet[-1][1],
            mass_l[i][0],
            mass_l[i][1],
            mass_l[i][2],
            1e-12,
        )
        assert AssertSimilarSets(_solC[3][0].tolist(), _solP[3][0].tolist(), 1)

    sol_tP = NuC.NuNuListPtEtaPhiE(Pb, Pb_, Pmu, Pmu_, Pmet, mass_l, 1e-12)
    sol_tC = NuC.NuNuListPxPyPzE(Cb, Cb_, Cmu, Cmu_, Cmet, mass_l, 1e-12)
    for i, j in zip(sol_tC[3], sol_tP[3]):
        assert AssertSimilarSets(i.tolist(), j.tolist(), 1)
    for i, j in zip(sol_tC[4], sol_tP[4]):
        assert AssertSimilarSets(i.tolist(), j.tolist(), 1)

    b1c = MakeTensor_(vl["b"], 0)
    b2c = MakeTensor_(vl["b"], 1)
    mu1c = MakeTensor_(vl["lep"], 0)
    mu2c = MakeTensor_(vl["lep"], 1)

    metx = torch.tensor(
        [[F.Px(i.met, i.met_phi) / 1000] for i in vl["ev"]],
        dtype=torch.float64,
        device="cuda",
    )
    mety = torch.tensor(
        [[F.Py(i.met, i.met_phi) / 1000] for i in vl["ev"]],
        dtype=torch.float64,
        device="cuda",
    )
    T = SampleTensor(
        vl["b"], vl["lep"], vl["ev"], vl["t"], "cuda", [[100, 0], [0, 100]]
    )

    # ------------------ Single Neutrino Reconstruction -------------------------- #
    sol_tP = NuC.NuPtEtaPhiE(
        T.b, T.mu, T.met, T.phi, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12
    )
    sol_tC = NuC.NuPxPyPzE(
        b1c, mu1c, metx, mety, T.Sxx, T.Sxy, T.Syx, T.Syy, T.mT, T.mW, T.mN, 1e-12
    )
    assert AssertEquivalenceRecursive(sol_tC[1].tolist(), sol_tP[1].tolist(), 0.01)

    Pb_l, Pmu_l, Pmet_l = [], [], []
    Cb_l, Cmu_l, Cmet_l = [], [], []
    met_lS, mass_l = [], []

    for i in range(len(sol_tP[0])):
        b, mu, ev = vl["b"][i][0], vl["lep"][i][0], vl["ev"][i]
        _solP = NuC.NuDoublePtEtaPhiE(
            b.pt / 1000,
            b.eta,
            b.phi,
            b.e / 1000,
            mu.pt / 1000,
            mu.eta,
            mu.phi,
            mu.e / 1000,
            ev.met / 1000,
            ev.met_phi,
            100,
            0,
            0,
            100,
            vl["t"][i][0].Mass / 1000,
            80.385,
            0,
            1e-12,
        )

        _solC = NuC.NuDoublePxPyPzE(
            b.px / 1000,
            b.py / 1000,
            b.pz / 1000,
            b.e / 1000,
            mu.px / 1000,
            mu.py / 1000,
            mu.pz / 1000,
            mu.e / 1000,
            F.Px(ev.met, ev.met_phi) / 1000,
            F.Py(ev.met, ev.met_phi) / 1000,
            100,
            0,
            0,
            100,
            vl["t"][i][0].Mass / 1000,
            80.385,
            0,
            1e-12,
        )
        assert AssertEquivalenceRecursive(_solP[1].tolist(), _solC[1].tolist(), 0.05)

        Pb_l.append([b.pt / 1000, b.eta, b.phi, b.e / 1000])
        Pmu_l.append([mu.pt / 1000, mu.eta, mu.phi, mu.e / 1000])
        Pmet_l.append([ev.met / 1000, ev.met_phi])

        Cb_l.append([b.px / 1000, b.py / 1000, b.pz / 1000, b.e / 1000])
        Cmu_l.append([mu.px / 1000, mu.py / 1000, mu.pz / 1000, mu.e / 1000])
        Cmet_l.append(
            [F.Px(ev.met, ev.met_phi) / 1000, F.Py(ev.met, ev.met_phi) / 1000]
        )

        met_lS.append([100, 0, 0, 100])
        mass_l.append([vl["t"][i][0].Mass / 1000, 80.385, 0])

    _solPL = NuC.NuListPtEtaPhiE(Pb_l, Pmu_l, Pmet_l, met_lS, mass_l, 1e-12)
    _solCL = NuC.NuListPxPyPzE(Cb_l, Cmu_l, Cmet_l, met_lS, mass_l, 1e-12)

    assert AssertEquivalenceRecursive(sol_tP[1].tolist(), _solCL[1].tolist(), 0.05)
    assert AssertEquivalenceRecursive(_solPL[1].tolist(), _solCL[1].tolist(), 0.05)

    # ------------------ Double Neutrino Reconstruction -------------------------- #
    sol_tP = NuC.NuNuPtEtaPhiE(
        T.b, T.b_, T.mu, T.mu_, T.met, T.phi, T.mT, T.mW, T.mN, 1e-12
    )
    sol_tC = NuC.NuNuPxPyPzE(b1c, b2c, mu1c, mu2c, metx, mety, T.mT, T.mW, T.mN, 1e-12)
    for i, j in zip(sol_tC[3], sol_tP[3]):
        assert AssertSimilarSets(i.tolist(), j.tolist(), 1)
    for i, j in zip(sol_tC[4], sol_tP[4]):
        assert AssertSimilarSets(i.tolist(), j.tolist(), 1)

    Pb, Pmu, Pmet = [], [], []
    Pb_, Pmu_ = [], []

    Cb, Cmu, Cmet = [], [], []
    Cb_, Cmu_ = [], []

    it = 0
    for i in range(len(sol_tP[0])):
        b, mu, ev = vl["b"][i][0], vl["lep"][i][0], vl["ev"][i]
        b_, mu_ = vl["b"][i][1], vl["lep"][i][1]

        Pb.append([b.pt / 1000, b.eta, b.phi, b.e / 1000])
        Pb_.append([b_.pt / 1000, b_.eta, b_.phi, b_.e / 1000])

        Pmu.append([mu.pt / 1000, mu.eta, mu.phi, mu.e / 1000])
        Pmu_.append([mu_.pt / 1000, mu_.eta, mu_.phi, mu_.e / 1000])

        Pmet.append([ev.met / 1000, ev.met_phi])

        Cb.append([b.px / 1000, b.py / 1000, b.pz / 1000, b.e / 1000])
        Cb_.append([b_.px / 1000, b_.py / 1000, b_.pz / 1000, b_.e / 1000])

        Cmu.append([mu.px / 1000, mu.py / 1000, mu.pz / 1000, mu.e / 1000])
        Cmu_.append([mu_.px / 1000, mu_.py / 1000, mu_.pz / 1000, mu_.e / 1000])

        Cmet.append([F.Px(ev.met, ev.met_phi) / 1000, F.Py(ev.met, ev.met_phi) / 1000])

        _solP = NuC.NuNuDoublePtEtaPhiE(
            Pb[-1][0],
            Pb[-1][1],
            Pb[-1][2],
            Pb[-1][3],
            Pb_[-1][0],
            Pb_[-1][1],
            Pb_[-1][2],
            Pb_[-1][3],
            Pmu[-1][0],
            Pmu[-1][1],
            Pmu[-1][2],
            Pmu[-1][3],
            Pmu_[-1][0],
            Pmu_[-1][1],
            Pmu_[-1][2],
            Pmu_[-1][3],
            Pmet[-1][0],
            Pmet[-1][1],
            mass_l[i][0],
            mass_l[i][1],
            mass_l[i][2],
            1e-12,
        )
        if _solP[0]:
            continue
        assert AssertSimilarSets(sol_tP[3][it].tolist(), _solP[3][0].tolist(), 1)
        it += 1

        _solC = NuC.NuNuDoublePxPyPzE(
            Cb[-1][0],
            Cb[-1][1],
            Cb[-1][2],
            Cb[-1][3],
            Cb_[-1][0],
            Cb_[-1][1],
            Cb_[-1][2],
            Cb_[-1][3],
            Cmu[-1][0],
            Cmu[-1][1],
            Cmu[-1][2],
            Cmu[-1][3],
            Cmu_[-1][0],
            Cmu_[-1][1],
            Cmu_[-1][2],
            Cmu_[-1][3],
            Cmet[-1][0],
            Cmet[-1][1],
            mass_l[i][0],
            mass_l[i][1],
            mass_l[i][2],
            1e-12,
        )

        assert AssertSimilarSets(_solC[3][0].tolist(), _solP[3][0].tolist(), 1)

    sol_tP = NuC.NuNuListPtEtaPhiE(Pb, Pb_, Pmu, Pmu_, Pmet, mass_l, 1e-12)
    sol_tC = NuC.NuNuListPxPyPzE(Cb, Cb_, Cmu, Cmu_, Cmet, mass_l, 1e-12)
    for i, j in zip(sol_tC[3], sol_tP[3]):
        assert AssertSimilarSets(i.tolist(), j.tolist(), 1)
    for i, j in zip(sol_tC[4], sol_tP[4]):
        assert AssertSimilarSets(i.tolist(), j.tolist(), 1)


if __name__ == "__main__":
    # test_transformation()
    # test_physics()
    # test_operators()
    # test_single_nu()
    #test_double_nu()
    # test_speed()
    # test_version_consistency()
    pass
