import torch
import vector
import inspect
import json
import pyc
device = "cuda" if torch.cuda.is_available() else "cpu"

def create_vector_cartesian(px, py, pz, e):
    return vector.obj(px = px, py = py, pz = pz, E = e)

def create_vector_polar(pt, eta, phi, e):
    return vector.obj(pt = pt, eta = eta, phi = phi, E = e)

def create_tensor_cpu_1d(inpt = [1., 2., 3., 4.]):
    return torch.tensor(inpt).view(1, -1).to(dtype = torch.float64)

def create_tensor_cpu_nd(dim):
    return torch.cat([create_tensor_cpu_1d*(i+1) for i in range(dim)], 0)

def rounder(inpt1, inpt2, d = 5):
    try: i1 = round(inpt1.view(-1)[0].item(), d)
    except:
        try: i1 = round(inpt1[0], d)
        except: i1 = round(inpt1, d)
    i2 = round(inpt2, d)
    res = i1 == i2
    if not res: print(i1, i2)
    return res

def rounder_l(inpt1, inpt2, d = 5):
    try: inpt1 = inpt1.view(-1).tolist()
    except:
        if isinstance(inpt1[0], list): inpt1 = inpt1[0]
        else: pass
    dif = sum([abs(round(i - j, d))/j for i, j in zip(inpt1, inpt2)])
    return dif*100 < 1

def assert_cuda_cartesian(base, func, pos, func2, pw = 1):
    print("->", inspect.stack()[1][3])
    f = getattr(getattr(base, "Cartesian"), func)
    p1 = getattr(create_vector_cartesian(1, 2, 3, 4), func2)**pw
    d1 = create_tensor_cpu_1d().to(device = device)
    assert rounder(f(*[d1[:, i] for i in pos]), p1)
    assert rounder(f(d1), p1)

def assert_cuda_polar(base, func, pos, func2, pw = 1):
    print("->", inspect.stack()[1][3])
    f = getattr(getattr(base, "Polar"), func)
    p1 = getattr(create_vector_polar(1, 2, 3, 4), func2)**pw
    d1 = create_tensor_cpu_1d().to(device = device)
    assert rounder(f(*[d1[:, i] for i in pos]), p1)
    assert rounder(f(d1), p1)

def assert_tensor_cartesian(base, func, pos, func2, pw = 1):
    print("->", inspect.stack()[1][3])
    f = getattr(getattr(base, "Cartesian"), func)
    p1 = getattr(create_vector_cartesian(1, 2, 3, 4), func2)**pw
    d1 = create_tensor_cpu_1d()
    assert rounder(f(*[d1[:, i] for i in pos]), p1)
    assert rounder(f(d1), p1)

def assert_tensor_polar(base, func, pos, func2, pw = 1):
    print("->", inspect.stack()[1][3])
    f = getattr(getattr(base, "Polar"), func)
    p1 = getattr(create_vector_polar(1, 2, 3, 4), func2)**pw
    d1 = create_tensor_cpu_1d()
    assert rounder(f(*[d1[:, i] for i in pos]), p1)
    assert rounder(f(d1), p1)

class Particle:
    def __init__(self, pt, eta, phi, e):
        self.pt = pt
        self.eta = eta
        self.phi = phi
        self.e = e
        self._cuda = torch.cuda.is_available()

    @property
    def vec(self):
        dct = {
                "pt" : self.pt,
                "eta" : self.eta,
                "phi" : self.phi,
                "energy" : self.e
        }
        return vector.obj(**dct)

    @property
    def ten(self):
        vec = [self.pt, self.eta, self.phi, self.e]
        vec = torch.tensor([vec], dtype = torch.float64)
        vec = vec.to(device = self.cuda)
        return vec

    @property
    def ten_polar(self):
        return self.ten

    @property
    def ten_cart(self):
        return pyc.Transform.PxPyPzE(self.ten)

    @property
    def cuda(self):
        try:
            return "cuda" if self._cuda else "cpu"
        except:
            self._cuda = torch.cuda.is_available()
        return "cuda" if self._cuda else "cpu"

    @cuda.setter
    def cuda(self, v):
        self._cuda = v

class event:
    def __init__(self, met, phi):
        self.met = met
        self.phi = phi
        self._cuda = torch.cuda.is_available()

    @property
    def vec(self):
        return vector.obj(pt = self.met, phi = self.phi)

    @property
    def ten(self):
        vec = torch.tensor([self.vec.px, self.vec.py], dtype = torch.float64).view(-1, 2)
        vec = vec.to(device = self.cuda)
        return vec

    @property
    def ten_cart(self):
        return self.ten

    @property
    def ten_polar(self):
        vec = torch.tensor([self.met, self.phi], dtype = torch.float64).view(-1, 2)
        vec = vec.to(device = self.cuda)
        return vec

    @property
    def cuda(self):
        try:
            return "cuda" if self._cuda else "cpu"
        except:
            self._cuda = torch.cuda.is_available()
        return "cuda" if self._cuda else "cpu"

    @cuda.setter
    def cuda(self, v):
        self._cuda = v

def loads( n ):
    f = open("neutrino_reconstruction/" + n + "NeutrinoEvents.json", "r")
    x = json.load(f)
    f.close()
    out = []
    for i in x:
        eve = event(**i[0])
        parti = [Particle(**k) for k in i[1:]]
        out.append([eve]+parti)
    return out

def loadDouble(): return loads("Double")
def loadSingle(): return loads("Single")

