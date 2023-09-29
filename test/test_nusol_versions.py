from neutrino_reconstruction.common import *
import torch
import pyc

precision = 10e-10
tolerance = 1e-1
mW = 80.385 * 1000
mT = 172.0 * 1000
mN = 0

def Attestation(truth, pred):
    v = abs(truth - pred) > tolerance
    for i, j, s in zip(truth, pred, v):
        if s.sum(-1).sum(-1) == 0: continue
        for r in i:
            if r.sum(-1).sum(-1) == 0: continue
            check = False
            for k in j:
                b = abs(r - k)/abs(r)
                if k.sum(-1).sum(-1) == 0: continue
                if (b > tolerance).sum(-1).sum(-1) != 0: continue
                check = True
                break
            assert check

def tensor_nu(coord, device = "cpu"):
    x = loadSingle()
    device = device if torch.cuda.is_available() else "cpu"
    masses = torch.tensor([[mW, mT, mN]], dtype = torch.float64, device = device)
    S2 = torch.tensor([[100, 9], [50, 100]], dtype = torch.float64, device = device)
    inpt = {"bq" : [], "lep" : [], "ev" : [], "mass" : [], "s2" : []}
    cu = True if device == "cuda" else False
    ita = iter(x)
    for i in range(len(x)):
        x_ = next(ita)
        ev, lep, bquark = x_[0], x_[1], x_[2]
        ev.cuda = cu
        lep.cuda = cu
        bquark.cuda = cu

        inpt["bq"].append(bquark.ten_polar if coord == "polar" else bquark.ten_cart)
        inpt["lep"].append(lep.ten_polar if coord == "polar" else lep.ten_cart)
        inpt["ev"].append(ev.ten_polar if coord == "polar" else ev.ten_cart)

    bq = torch.cat(inpt["bq"], dim = 0)
    lep = torch.cat(inpt["lep"], dim = 0)
    ev = torch.cat(inpt["ev"], dim = 0)
    return {"bq" : bq, "lep" : lep, "ev" : ev, "mass" : masses, "S2" : S2}

def reference_nu(device = "cpu"):
    device = device if torch.cuda.is_available() else "cpu"
    inpt = tensor_nu("cart", device)
    cu = pyc.NuSol.Nu(
            inpt["bq"], inpt["lep"], inpt["ev"],
            inpt["mass"], inpt["S2"], precision)
    return cu

def test_nu_cuda_polar_combined():
    truth = reference_nu("cuda")
    x = tensor_nu("polar", "cuda")
    pred = pyc.NuSol.Polar.Nu(x["bq"], x["lep"], x["ev"], x["mass"], x["S2"], precision)
    Attestation(truth[0], pred[0])

def test_nu_cuda_polar_separate():
    truth = reference_nu("cuda")
    x = tensor_nu("polar", "cuda")
    pt_b, eta_b, phi_b, e_b = [x["bq"][:, i] for i in range(4)]
    pt_mu, eta_mu, phi_mu, e_mu = [x["lep"][:, i] for i in range(4)]
    met, phi = [x["ev"][:, i] for i in range(2)]

    pred = pyc.NuSol.Polar.Nu(
            pt_b, eta_b, phi_b, e_b, pt_mu, 
            eta_mu, phi_mu, e_mu, met, phi, x["mass"], x["S2"], precision)
    Attestation(truth[0], pred[0])


def test_nu_cuda_cartesian_combined():
    truth = reference_nu("cuda")
    x = tensor_nu("cart", "cuda")
    pred = pyc.NuSol.Cartesian.Nu(
            x["bq"], x["lep"], x["ev"], x["mass"], x["S2"], precision)
    Attestation(truth[0], pred[0])

def test_nu_cuda_cartesian_separate():
    truth = reference_nu("cuda")
    x = tensor_nu("cart", "cuda")
    pt_b, eta_b, phi_b, e_b = [x["bq"][:, i] for i in range(4)]
    pt_mu, eta_mu, phi_mu, e_mu = [x["lep"][:, i] for i in range(4)]
    met, phi = [x["ev"][:, i] for i in range(2)]

    pred = pyc.NuSol.Cartesian.Nu(
            pt_b , eta_b , phi_b , e_b ,
            pt_mu, eta_mu, phi_mu, e_mu,
            met, phi, x["mass"], x["S2"], precision)
    Attestation(truth[0], pred[0])

def tensor_nunu(coord, device = "cpu"):
    x = loadDouble()
    device = device if torch.cuda.is_available() else "cpu"
    masses = torch.tensor([[mW, mT, mN]], dtype = torch.float64, device = device)
    inpt = {"bq1" : [], "bq2" : [], "lep1" : [], "lep2" : [], "ev" : []}
    cu = True if device == "cuda" else False
    ita = iter(x)
    for i in range(len(x)):
        x_ = next(ita)
        ev, lep1, lep2, bq1, bq2 = x_
        ev.cuda = cu
        lep1.cuda = cu
        lep2.cuda = cu
        bq1.cuda = cu
        bq2.cuda = cu

        inpt["bq1"].append(bq1.ten_polar if coord == "polar" else bq1.ten_cart)
        inpt["bq2"].append(bq2.ten_polar if coord == "polar" else bq2.ten_cart)
        inpt["lep1"].append(lep1.ten_polar if coord == "polar" else lep1.ten_cart)
        inpt["lep2"].append(lep2.ten_polar if coord == "polar" else lep2.ten_cart)
        inpt["ev"].append(ev.ten_polar if coord == "polar" else ev.ten_cart)

    bq1 = torch.cat(inpt["bq1"], dim = 0)
    bq2 = torch.cat(inpt["bq2"], dim = 0)
    lep1 = torch.cat(inpt["lep1"], dim = 0)
    lep2 = torch.cat(inpt["lep2"], dim = 0)
    ev = torch.cat(inpt["ev"], dim = 0)
    return {"bq1" : bq1, "bq2" : bq2, "lep1" : lep1, "lep2" : lep2, "ev" : ev, "mass" : masses}

def reference_nunu(device = "cpu"):
    device = device if torch.cuda.is_available() else "cpu"
    inpt = tensor_nunu("cart", device)
    inpt = [i for i in inpt.values()] + [precision]
    cu = pyc.NuSol.NuNu(*inpt)
    return cu

def test_nunu_cuda_polar_combined():
    truth = reference_nunu("cuda")
    inpt = tensor_nunu("polar", "cuda")
    inpt = [i for i in inpt.values()] + [precision]
    pred = pyc.NuSol.Polar.NuNu(*inpt)
    Attestation(truth[0], pred[0])
    Attestation(truth[1], pred[1])

def test_nunu_cuda_polar_separate():
    truth = reference_nunu("cuda")
    x = tensor_nunu("polar", "cuda")
    inpt =  [x["bq1"][:, i] for i in range(4)]
    inpt += [x["bq2"][:, i] for i in range(4)]
    inpt += [x["lep1"][:, i] for i in range(4)]
    inpt += [x["lep2"][:, i] for i in range(4)]
    inpt += [x["ev"][:, i] for i in range(2)]
    inpt += [x["mass"], precision]
    pred = pyc.NuSol.Polar.NuNu(*inpt)
    Attestation(truth[0], pred[0])
    Attestation(truth[1], pred[1])

def test_nunu_cuda_cartesian_combined():
    truth = reference_nunu("cuda")
    inpt = tensor_nunu("cart", "cuda")
    inpt = [i for i in inpt.values()] + [precision]
    pred = pyc.NuSol.Cartesian.NuNu(*inpt)
    Attestation(truth[0], pred[0])
    Attestation(truth[1], pred[1])

def test_nunu_cuda_cartesian_separate():
    truth = reference_nunu("cuda")
    x = tensor_nunu("cart", "cuda")
    inpt =  [x["bq1"][:, i] for i in range(4)]
    inpt += [x["bq2"][:, i] for i in range(4)]
    inpt += [x["lep1"][:, i] for i in range(4)]
    inpt += [x["lep2"][:, i] for i in range(4)]
    inpt += [x["ev"][:, i] for i in range(2)]
    inpt += [x["mass"], precision]
    pred = pyc.NuSol.Cartesian.NuNu(*inpt)
    Attestation(truth[0], pred[0])
    Attestation(truth[1], pred[1])


def test_nu_cpu_polar_combined():
    truth = reference_nu("cpu")
    x = tensor_nu("polar", "cpu")
    pred = pyc.NuSol.Polar.Nu(x["bq"], x["lep"], x["ev"], x["mass"], x["S2"], precision)
    Attestation(truth[0], pred[0])

def test_nu_cpu_polar_separate():
    truth = reference_nu("cpu")
    x = tensor_nu("polar", "cpu")
    pt_b, eta_b, phi_b, e_b = [x["bq"][:, i] for i in range(4)]
    pt_mu, eta_mu, phi_mu, e_mu = [x["lep"][:, i] for i in range(4)]
    met, phi = [x["ev"][:, i] for i in range(2)]

    pred = pyc.NuSol.Polar.Nu(
            pt_b, eta_b, phi_b, e_b, pt_mu, 
            eta_mu, phi_mu, e_mu, met, phi, x["mass"], x["S2"], precision)
    Attestation(truth[0], pred[0])


def test_nu_cpu_cartesian_combined():
    truth = reference_nu("cpu")
    x = tensor_nu("cart", "cpu")
    pred = pyc.NuSol.Cartesian.Nu(x["bq"], x["lep"], x["ev"], x["mass"], x["S2"], precision)
    Attestation(truth[0], pred[0])

def test_nu_cpu_cartesian_separate():
    truth = reference_nu("cpu")
    x = tensor_nu("cart", "cpu")
    pt_b, eta_b, phi_b, e_b = [x["bq"][:, i] for i in range(4)]
    pt_mu, eta_mu, phi_mu, e_mu = [x["lep"][:, i] for i in range(4)]
    met, phi = [x["ev"][:, i] for i in range(2)]

    pred = pyc.NuSol.Cartesian.Nu(
            pt_b , eta_b , phi_b , e_b ,
            pt_mu, eta_mu, phi_mu, e_mu,
            met, phi, x["mass"], x["S2"], precision)
    Attestation(truth[0], pred[0])

def test_nunu_cpu_polar_combined():
    truth = reference_nunu("cpu")
    inpt = tensor_nunu("polar", "cpu")
    inpt = [i for i in inpt.values()] + [precision]
    pred = pyc.NuSol.Polar.NuNu(*inpt)
    Attestation(truth[0], pred[0])
    Attestation(truth[1], pred[1])

def test_nunu_cpu_polar_separate():
    truth = reference_nunu("cpu")
    x = tensor_nunu("polar", "cpu")
    inpt =  [x["bq1"][:, i] for i in range(4)]
    inpt += [x["bq2"][:, i] for i in range(4)]
    inpt += [x["lep1"][:, i] for i in range(4)]
    inpt += [x["lep2"][:, i] for i in range(4)]
    inpt += [x["ev"][:, i] for i in range(2)]
    inpt += [x["mass"], precision]
    pred = pyc.NuSol.Polar.NuNu(*inpt)
    Attestation(truth[0], pred[0])
    Attestation(truth[1], pred[1])

def test_nunu_cpu_cartesian_combined():
    truth = reference_nunu("cpu")
    inpt = tensor_nunu("cart", "cpu")
    inpt = [i for i in inpt.values()] + [precision]
    pred = pyc.NuSol.Cartesian.NuNu(*inpt)
    Attestation(truth[0], pred[0])
    Attestation(truth[1], pred[1])

def test_nunu_cpu_cartesian_separate():
    truth = reference_nunu("cpu")
    x = tensor_nunu("cart", "cpu")
    inpt =  [x["bq1"][:, i] for i in range(4)]
    inpt += [x["bq2"][:, i] for i in range(4)]
    inpt += [x["lep1"][:, i] for i in range(4)]
    inpt += [x["lep2"][:, i] for i in range(4)]
    inpt += [x["ev"][:, i] for i in range(2)]
    inpt += [x["mass"], precision]
    pred = pyc.NuSol.Cartesian.NuNu(*inpt)
    Attestation(truth[0], pred[0])
    Attestation(truth[1], pred[1])

def test_nu_floats_polar_combined():
    truth = reference_nu("cpu")
    inpt = tensor_nu("polar", "cpu")
    inpt = [i.tolist() for i in inpt.values()] + [precision]
    pred = pyc.NuSol.Polar.Nu(*inpt)
    Attestation(truth[0], pred[0])
    Attestation(truth[1], pred[1])

def test_nu_floats_cartesian_combined():
    truth = reference_nu("cpu")
    inpt = tensor_nu("cart", "cpu")
    inpt = [i.tolist() for i in inpt.values()] + [precision]
    pred = pyc.NuSol.Cartesian.Nu(*inpt)
    Attestation(truth[0], pred[0])
    Attestation(truth[1], pred[1])

def test_nunu_floats_polar_combined():
    truth = reference_nunu("cpu")
    inpt = tensor_nunu("polar", "cpu")
    inpt = [i.tolist() for i in inpt.values()] + [precision]
    pred = pyc.NuSol.Polar.NuNu(*inpt)
    Attestation(truth[0], pred[0])
    Attestation(truth[1], pred[1])

def test_nunu_floats_cartesian_combined():
    truth = reference_nunu("cpu")
    inpt = tensor_nunu("cart", "cpu")
    inpt = [i.tolist() for i in inpt.values()] + [precision]
    pred = pyc.NuSol.Cartesian.NuNu(*inpt)
    Attestation(truth[0], pred[0])
    Attestation(truth[1], pred[1])

if __name__ == "__main__":
    test_nu_cuda_polar_combined()
    test_nu_cuda_polar_separate()
    test_nu_cuda_cartesian_combined()
    test_nu_cuda_cartesian_separate()

    test_nunu_cuda_polar_combined()
    test_nunu_cuda_polar_separate()
    test_nunu_cuda_cartesian_combined()
    test_nunu_cuda_cartesian_separate()

    test_nu_cpu_polar_combined()
    test_nu_cpu_polar_separate()
    test_nu_cpu_cartesian_combined()
    test_nu_cpu_cartesian_separate()

    test_nunu_cpu_polar_combined()
    test_nunu_cpu_polar_separate()
    test_nunu_cpu_cartesian_combined()
    test_nunu_cpu_cartesian_separate()

    test_nu_floats_polar_combined()
    test_nu_floats_cartesian_combined()

    test_nunu_floats_polar_combined()
    test_nunu_floats_cartesian_combined()


