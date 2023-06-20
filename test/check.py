import torch
import vector
from time import time
import numpy as np

mW = 80.385 * 1000  # MeV : W Boson Mass
mN = 0  # GeV : Neutrino Mass


def MakeTensor(inpt, device="cpu"):
    return torch.tensor([inpt], device=device, dtype=torch.float64)


def MakeTensor_(inpt, indx):
    return torch.tensor(
        [
            [i[indx].px / 1000, i[indx].py / 1000, i[indx].pz / 1000, i[indx].e / 1000]
            for i in inpt
        ],
        dtype=torch.float64,
        device="cuda",
    )


def AssertEquivalence(truth, pred, threshold=0.0001):
    diff = abs(truth - pred)
    if truth == 0:
        truth += 1
    diff = abs((diff / truth)) * 100
    if diff < threshold:
        return True
    if truth < 1e-12 and pred < 1e-12:
        return True  # Getting to machine precision difference
    return False


def AssertEquivalenceList(truth, pred, threshold=0.0001):
    for i, j in zip(truth, pred):
        if AssertEquivalence(i, j, threshold):
            continue
        return False
    return True


def AssertEquivalenceRecursive(truth, pred, threshold=0.001):
    try:
        return AssertEquivalence(float(truth), float(pred), threshold)
    except:
        for i, j in zip(truth, pred):
            if AssertEquivalenceRecursive(i, j, threshold):
                continue
            return False
        return True


def AssertSimilarSets(pred1, pred2, threshold):
    if len(pred1) != len(pred2):
        return False
    p1, p2 = [], []
    for i, j in zip(pred1, pred2):
        if sum(i) != 0:
            p1.append(i)
        if sum(j) != 0:
            p2.append(j)
    for i in p1:
        diff1 = {}
        for k in p2:
            diff1[sum([abs((l1 - l2) / l1) * 100 for l1, l2 in zip(k, i)]) ** 0.5] = [
                k,
                i,
            ]
        l = list(diff1)
        l.sort()
        trig = False
        if l[0] > threshold:
            trig = True
        if trig:
            return False
    return True


def ParticleToTorch(part, device="cuda"):
    tx = torch.tensor([[part.px]], device=device, dtype=torch.float64)
    ty = torch.tensor([[part.py]], device=device, dtype=torch.float64)
    tz = torch.tensor([[part.pz]], device=device, dtype=torch.float64)
    te = torch.tensor([[part.e]], device=device, dtype=torch.float64)
    return tx, ty, tz, te


def ParticleToTensor(part, device="cuda"):
    return torch.tensor(
        [[part.px, part.py, part.pz, part.e]], device=device, dtype=torch.float64
    )


def ParticleToVector(part):
    return vector.obj(pt=part.pt, eta=part.eta, phi=part.phi, E=part.e)


def PerformanceInpt(varT, varC, v1=None, v2=None, v3=None, v4=None, v5=None, v6=None):
    if v5 != None and v6 != None:
        t1 = time()
        rest = varT(v1, v2, v3, v4, v5, v6)
        diff1 = time() - t1

        t1 = time()
        resc = varC(v1, v2, v3, v4, v5, v6)
        diff2 = time() - t1

    elif v3 != None and v4 != None:
        t1 = time()
        rest = varT(v1, v2, v3, v4)
        diff1 = time() - t1

        t1 = time()
        resc = varC(v1, v2, v3, v4)
        diff2 = time() - t1

    elif v3 != None and v4 is None:
        t1 = time()
        rest = varT(v1, v2, v3)
        diff1 = time() - t1

        t1 = time()
        resc = varC(v1, v2, v3)
        diff2 = time() - t1

    elif v3 is None and v4 is None:
        t1 = time()
        rest = varT(v1, v2)
        diff1 = time() - t1

        t1 = time()
        resc = varC(v1, v2)
        diff2 = time() - t1

    print("--- Testing Performance Between C++ and CUDA of " + varT.__name__ + " ---")
    print("Speed Factor (> 1 is better): ", diff1 / diff2)
    assert AssertEquivalenceRecursive(resc, rest)


def ParticleCollectors(ev):
    t1 = [t for t in ev.Tops if t.LeptonicDecay][0]
    t2 = [t for t in ev.Tops if t.LeptonicDecay][1]

    out = []
    prt = {abs(p.pdgid): p for p in t1.Children}
    b = prt[5]
    lep = [prt[i] for i in [11, 13, 15] if i in prt][0]
    nu = [prt[i] for i in [12, 14, 16] if i in prt][0]
    out.append([b, lep, nu, t1])

    prt = {abs(p.pdgid): p for p in t2.Children}
    b = prt[5]
    lep = [prt[i] for i in [11, 13, 15] if i in prt][0]
    nu = [prt[i] for i in [12, 14, 16] if i in prt][0]
    out.append([b, lep, nu, t2])
    return out


class SampleTensor:
    def __init__(self, b, mu, ev, top, device="cpu", S=[[100, 0], [0, 100]]):
        self.device = device
        self.n = len(b)

        self.Sxx = self.MakeTensor(S[0][0])
        self.Sxy = self.MakeTensor(S[0][1])
        self.Syx = self.MakeTensor(S[1][0])
        self.Syy = self.MakeTensor(S[1][1])

        self.b = self.MakeKinematics(0, b)
        self.mu = self.MakeKinematics(0, mu)

        self.b_ = self.MakeKinematics(1, b)
        self.mu_ = self.MakeKinematics(1, mu)

        self.mT = torch.tensor(
            [[top[i][0].Mass / 1000] for i in range(self.n)],
            device=self.device,
            dtype=torch.float64,
        )
        self.mW = self.MakeTensor(mW / 1000)
        self.mN = self.MakeTensor(mN / 1000)

        self.MakeEvent(ev)

    def MakeKinematics(self, idx, obj):
        return torch.tensor(
            [
                [i[idx].pt / 1000.0, i[idx].eta, i[idx].phi, i[idx].e / 1000.0]
                for i in obj
            ],
            device=self.device,
            dtype=torch.float64,
        )

    def MakeEvent(self, obj):
        self.met = torch.tensor(
            [[ev.met / 1000.0] for ev in obj], device=self.device, dtype=torch.float64
        )
        self.phi = torch.tensor(
            [[ev.met_phi] for ev in obj], device=self.device, dtype=torch.float64
        )

    def MakeTensor(self, val):
        return torch.tensor(
            [[val] for i in range(self.n)], device=self.device, dtype=torch.float64
        )

    def __iter__(self):
        self.it = -1
        return self

    def __next__(self):
        self.it += 1
        if self.it == self.n:
            raise StopIteration()

        return [
            self.b[self.it],
            self.mu[self.it],
            self.b_[self.it],
            self.mu_[self.it],
            self.met[self.it],
            self.phi[self.it],
            self.mT[self.it],
            self.mW[self.it],
            self.mN[self.it],
        ]


class SampleVector:
    def __init__(self, b, mu, ev, top):
        self.n = len(ev)
        self.b = [self.MakeKinematics(0, i) for i in b]
        self.b_ = [self.MakeKinematics(1, i) for i in b]

        self.mu = [self.MakeKinematics(0, i) for i in mu]
        self.mu_ = [self.MakeKinematics(1, i) for i in mu]

        self.met_x = []
        self.met_y = []

        for i in ev:
            x, y = self.MakeEvent(i)
            self.met_x.append(x)
            self.met_y.append(y)

        self.mT = [top[i][0].Mass / 1000 for i in range(self.n)]
        self.mW = [mW / 1000 for i in range(self.n)]
        self.mN = [mN / 1000 for i in range(self.n)]

    def MakeKinematics(self, idx, obj):
        r = vector.obj(
            pt=obj[idx].pt / 1000.0,
            eta=obj[idx].eta,
            phi=obj[idx].phi,
            E=obj[idx].e / 1000.0,
        )
        return r

    def MakeEvent(self, obj):
        x = (obj.met / 1000.0) * np.cos(obj.met_phi)
        y = (obj.met / 1000.0) * np.sin(obj.met_phi)
        return x, y

    def __iter__(self):
        self.it = -1
        return self

    def __next__(self):
        self.it += 1
        if self.it == self.n:
            raise StopIteration()

        return [
            self.b[self.it],
            self.mu[self.it],
            self.b_[self.it],
            self.mu_[self.it],
            self.met_x[self.it],
            self.met_y[self.it],
            self.mT[self.it],
            self.mW[self.it],
            self.mN[self.it],
        ]
