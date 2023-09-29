from neutrino_reconstruction.common import *
import torch
import pyc
device = "cuda" if torch.cuda.is_available() else "cpu"

def test_transform_px():
    d1 = create_tensor_cpu_1d()
    d1_cu = d1.to(device = device)
    p1 = create_vector_polar(1, 2, 3, 4)
    assert rounder(pyc.Transform.Px(d1[:, 0], d1[:, 2]), p1.px)
    assert rounder(pyc.Transform.Px(d1), p1.px)
    assert rounder(pyc.Transform.Px(d1_cu[:, 0], d1_cu[:, 2]), p1.px)
    assert rounder(pyc.Transform.Px(d1_cu), p1.px)
    assert rounder(pyc.Transform.Px(1, 3), p1.px)
    assert rounder(pyc.Transform.Px([[1, 2, 3, 4]]), p1.px)

def test_transform_py():
    d1 = create_tensor_cpu_1d()
    d1_cu = d1.to(device = device)
    p1 = create_vector_polar(1, 2, 3, 4)
    assert rounder(pyc.Transform.Py(d1[:, 0], d1[:, 2]), p1.py)
    assert rounder(pyc.Transform.Py(d1), p1.py)
    assert rounder(pyc.Transform.Py(d1_cu[:, 0], d1_cu[:, 2]), p1.py)
    assert rounder(pyc.Transform.Py(d1_cu), p1.py)
    assert rounder(pyc.Transform.Py(1, 3), p1.py)
    assert rounder(pyc.Transform.Py([[1, 2, 3, 4]]), p1.py)

def test_transform_pz():
    d1 = create_tensor_cpu_1d()
    d1_cu = d1.to(device = device)
    p1 = create_vector_polar(1, 2, 3, 4)
    assert rounder(pyc.Transform.Pz(d1[:, 0], d1[:, 1]), p1.pz)
    assert rounder(pyc.Transform.Pz(d1), p1.pz)
    assert rounder(pyc.Transform.Pz(d1_cu[:, 0], d1_cu[:, 1]), p1.pz)
    assert rounder(pyc.Transform.Pz(d1_cu), p1.pz)
    assert rounder(pyc.Transform.Pz(1, 2), p1.pz)
    assert rounder(pyc.Transform.Pz([[1, 2, 3, 4]]), p1.pz)

def test_transform_pxpypz():
    d1 = create_tensor_cpu_1d()
    d1_cu = d1.to(device = device)
    p1 = create_vector_polar(1, 2, 3, 4)
    p1 = [p1.px, p1.py, p1.pz]
    assert rounder_l(pyc.Transform.PxPyPz(d1[:, 0], d1[:, 1], d1[:, 2]), p1)
    assert rounder_l(pyc.Transform.PxPyPz(d1), p1)
    assert rounder_l(pyc.Transform.PxPyPz(d1_cu[:, 0], d1_cu[:, 1], d1_cu[:, 2]), p1)
    assert rounder_l(pyc.Transform.PxPyPz(d1_cu), p1)
    assert rounder_l(pyc.Transform.PxPyPz(1, 2, 3), p1)
    assert rounder_l(pyc.Transform.PxPyPz([[1, 2, 3, 4]]), p1)

def test_transform_pxpypze():
    d1 = create_tensor_cpu_1d()
    d1_cu = d1.to(device = device)
    p1 = create_vector_polar(1, 2, 3, 4)
    p1 = [p1.px, p1.py, p1.pz, p1.e]
    assert rounder_l(pyc.Transform.PxPyPzE(d1[:, 0], d1[:, 1], d1[:, 2], d1[:, 3]), p1)
    assert rounder_l(pyc.Transform.PxPyPzE(d1), p1)
    assert rounder_l(pyc.Transform.PxPyPzE(d1_cu[:, 0], d1_cu[:, 1], d1_cu[:, 2], d1_cu[:, 3]), p1)
    assert rounder_l(pyc.Transform.PxPyPzE(d1_cu), p1)
    assert rounder_l(pyc.Transform.PxPyPzE(1, 2, 3, 4), p1)
    assert rounder_l(pyc.Transform.PxPyPzE([[1, 2, 3, 4]]), p1)

def test_transform_pt():
    d1 = create_tensor_cpu_1d()
    d1_cu = d1.to(device = device)
    p1 = create_vector_cartesian(1, 2, 3, 4).pt
    assert rounder(pyc.Transform.Pt(d1[:, 0], d1[:, 1]), p1)
    assert rounder(pyc.Transform.Pt(d1), p1)
    assert rounder(pyc.Transform.Pt(d1_cu[:, 0], d1_cu[:, 1]), p1)
    assert rounder(pyc.Transform.Pt(d1_cu), p1)
    assert rounder(pyc.Transform.Pt(1, 2), p1)
    assert rounder(pyc.Transform.Pt([[1, 2, 3, 4]]), p1)

def test_transform_eta():
    d1 = create_tensor_cpu_1d()
    d1_cu = d1.to(device = device)
    p1 = create_vector_cartesian(1, 2, 3, 4).eta
    assert rounder(pyc.Transform.Eta(d1[:, 0], d1[:, 1], d1[:, 2]), p1)
    assert rounder(pyc.Transform.Eta(d1), p1)
    assert rounder(pyc.Transform.Eta(d1_cu[:, 0], d1_cu[:, 1], d1_cu[:, 2]), p1)
    assert rounder(pyc.Transform.Eta(d1_cu), p1)
    assert rounder(pyc.Transform.Eta(1, 2, 3), p1)
    assert rounder(pyc.Transform.Eta([[1, 2, 3, 4]]), p1)

def test_transform_phi():
    d1 = create_tensor_cpu_1d()
    d1_cu = d1.to(device = device)
    p1 = create_vector_cartesian(1, 2, 3, 4).phi
    assert rounder(pyc.Transform.Phi(d1[:, 0], d1[:, 1]), p1)
    assert rounder(pyc.Transform.Phi(d1), p1)
    assert rounder(pyc.Transform.Phi(d1_cu[:, 0], d1_cu[:, 1]), p1)
    assert rounder(pyc.Transform.Phi(d1_cu), p1)
    assert rounder(pyc.Transform.Phi(1, 2), p1)
    assert rounder(pyc.Transform.Phi([[1, 2, 3, 4]]), p1)

def test_transform_ptetaphi():
    d1 = create_tensor_cpu_1d()
    d1_cu = d1.to(device = device)
    p1 = create_vector_cartesian(1, 2, 3, 4)
    p1 = [p1.pt, p1.eta, p1.phi]
    assert rounder_l(pyc.Transform.PtEtaPhi(d1[:, 0], d1[:, 1], d1[:, 2]), p1)
    assert rounder_l(pyc.Transform.PtEtaPhi(d1), p1)
    assert rounder_l(pyc.Transform.PtEtaPhi(d1_cu[:, 0], d1_cu[:, 1], d1_cu[:, 2]), p1)
    assert rounder_l(pyc.Transform.PtEtaPhi(d1_cu), p1)
    assert rounder_l(pyc.Transform.PtEtaPhi(1, 2, 3), p1)
    assert rounder_l(pyc.Transform.PtEtaPhi([[1, 2, 3, 4]]), p1)

def test_transform_ptetaphie():
    d1 = create_tensor_cpu_1d()
    d1_cu = d1.to(device = device)
    p1 = create_vector_cartesian(1, 2, 3, 4)
    p1 = [p1.pt, p1.eta, p1.phi, p1.e]
    assert rounder_l(pyc.Transform.PtEtaPhiE(d1[:, 0], d1[:, 1], d1[:, 2], d1[:, 3]), p1)
    assert rounder_l(pyc.Transform.PtEtaPhiE(d1), p1)
    assert rounder_l(pyc.Transform.PtEtaPhiE(d1_cu[:, 0], d1_cu[:, 1], d1_cu[:, 2], d1_cu[:, 3]), p1)
    assert rounder_l(pyc.Transform.PtEtaPhiE(d1_cu), p1)
    assert rounder_l(pyc.Transform.PtEtaPhiE(1, 2, 3, 4), p1)
    assert rounder_l(pyc.Transform.PtEtaPhiE([[1, 2, 3, 4]]), p1)

if __name__ == "__main__":
    test_transform_px()
    test_transform_py()
    test_transform_pz()
    test_transform_pxpypz()
    test_transform_pxpypze()

    test_transform_pt()
    test_transform_eta()
    test_transform_phi()
    test_transform_ptetaphi()
    test_transform_ptetaphie()
