import random
import pyc
import torch
torch.set_printoptions(4, profile="full", linewidth=100000)
device = "cuda" if torch.cuda.is_available() else "cpu"

def _makeMatrix(l, m, n, tmp):
    x = torch.tensor(
            [[[random.random() for i in range(tmp)] for k in range(n)] for t in range(l)],
            device = device, dtype = torch.float64)

    y = torch.tensor(
            [[[random.random() for i in range(m)] for k in range(tmp)] for t in range(l)],
            device = device, dtype = torch.float64)
    return x, y

def _AttestEqual(truth, custom):
    x = (truth - custom).sum(-1).sum(-1).sum(-1)
    x_t = truth.sum(-1).sum(-1).sum(-1)
    x[x_t != 0] /= x_t[ x_t != 0]
    assert x < 10e-8

def _compareMulti(l, m, n, tmp):
    x, y = _makeMatrix(l, m, n, tmp)
    x_ = x.matmul(y)
    x_cu = pyc.Operators.Mul(x, y)
    _AttestEqual(x_, x_cu)

def test_matrix_multi():
    # Equally sized 
    _compareMulti(10, 10, 10, 10)

    # M > N
    _compareMulti(10, 17, 10, 10)

    # M < N
    _compareMulti(10, 10, 17, 10)

    # intermediate n, M < N
    _compareMulti(10, 15, 18, 5)

    # intermediate n, M > N
    _compareMulti(10, 18, 15, 5)

    # intermediate n, M = N
    _compareMulti(10, 15, 15, 5)

def test_costheta():
    x = torch.tensor([[random.random()*100 for i in range(10)] for _ in range(100)], device = device, dtype = torch.float64)
    y = torch.tensor([[random.random()*100 for i in range(10)] for _ in range(100)], device = device, dtype = torch.float64)

    cu = pyc.Operators.CosTheta(x, y)
    xy = (x*y).sum(-1, keepdim = True)
    x2 = (x*x).sum(-1, keepdim = True)
    y2 = (y*y).sum(-1, keepdim = True)
    t = xy/(torch.sqrt(x2*y2))
    _AttestEqual(t, cu)


def test_sintheta():
    x = torch.tensor([[random.random() for i in range(1000)] for _ in range(100)], device = device, dtype = torch.float64)
    y = torch.tensor([[random.random() for i in range(1000)] for _ in range(100)], device = device, dtype = torch.float64)

    cu = pyc.Operators.SinTheta(x, y)

    xy2 = torch.pow((x*y).sum(-1, keepdim = True), 2)
    x2 = (x*x).sum(-1, keepdim = True)
    y2 = (y*y).sum(-1, keepdim = True)
    x2y2 = x2*y2

    t = torch.sqrt(1 - xy2/x2y2)
    _AttestEqual(t, cu)

def test_rx():
    x = torch.tensor([[random.random()] for i in range(10)], device = device, dtype = torch.float64)
    x_ = pyc.Operators.Rx(x)

    z = torch.zeros_like(x)
    o = torch.ones_like(x)
    c = torch.cos(x)
    s = torch.sin(x)
    tru = torch.cat([o, z, z, z, c, -s, z, s, c], dim = -1).view(-1, 3, 3)
    _AttestEqual(tru, x_)

def test_ry():
    x = torch.tensor([[random.random()] for i in range(10)], device = device, dtype = torch.float64)
    x_ = pyc.Operators.Ry(x)

    z = torch.zeros_like(x)
    o = torch.ones_like(x)
    c = torch.cos(x)
    s = torch.sin(x)
    tru = torch.cat([c, z, s, z, o, z, -s, z, c], dim = -1).view(-1, 3, 3)

    _AttestEqual(tru, x_)

def test_rz():
    x = torch.tensor([[random.random()] for i in range(10)], device = device, dtype = torch.float64)
    x_ = pyc.Operators.Rz(x)

    z = torch.zeros_like(x)
    o = torch.ones_like(x)
    c = torch.cos(x)
    s = torch.sin(x)
    tru = torch.cat([c, -s, z, s, c, z, z, z, o], dim = -1).view(-1, 3, 3)
    _AttestEqual(tru, x_)

def test_cofactor():
    x = torch.tensor([[[(i+1) + (k+1) for i in range(3)] for k in range(3)] for i in range(2)], device = device, dtype = torch.float64)
    x_ = pyc.Operators.CoFactors(x)
    x = torch.tensor([[-1, 2, -1, 2, -4, 2, -1, 2, -1] for i in range(2)], device = device, dtype = torch.float64).view(-1, 3, 3)
    _AttestEqual(x, x_)

def test_det():
    x = torch.tensor([[[random.random()*10 for i in range(3)] for k in range(3)] for i in range(100)], device = device, dtype = torch.float64)
    x_t = torch.det(x)
    x_ = pyc.Operators.Determinant(x)
    _AttestEqual(x_t.view(-1, 1), x_)

def test_inverse():
    x = torch.tensor([[[random.random()*10 for i in range(3)] for k in range(3)] for i in range(10000)], device = device, dtype = torch.float64)
    det = pyc.Operators.Determinant(x).view(-1)

    x_ = pyc.Operators.Inverse(x)
    x_t = torch.inverse(x)
    _AttestEqual(x_t[det != 0], x_[det != 0])

def test_cross():
    if device != "cuda": return 
    def rdm(): return [random.random()*100, random.random()*100, random.random()*100]

    x = torch.tensor([ [rdm() for _ in range(3)] for _ in range(1000) ], device = device, dtype = torch.float64)
    y = torch.tensor([ [rdm() for _ in range(3)] for _ in range(1000) ], device = device, dtype = torch.float64)

    x_t = torch.linalg.cross(y, x)
    x_cu = pyc.Operators.Cross(y, x)

    _AttestEqual(x_t, x_cu)

if __name__ == "__main__":
    test_matrix_multi()
    test_costheta()
    test_sintheta()
    test_rx()
    test_ry()
    test_rz()
    test_cofactor()
    test_det()
    test_inverse()
    test_cross()
