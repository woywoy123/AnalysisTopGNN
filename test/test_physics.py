from neutrino_reconstruction.common import *
import pyc.Physics as Physics
device = "cuda" if torch.cuda.is_available() else "cpu"

def test_polar_p2():
    assert_cuda_polar(Physics, "P2", [0, 1, 2], "p2")
    assert_tensor_polar(Physics, "P2", [0, 1, 2], "p2")

def test_polar_p():
    assert_cuda_polar(Physics, "P", [0, 1, 2], "p")
    assert_tensor_polar(Physics, "P2", [0, 1, 2], "p2")

def test_cartesian_p2():
    assert_cuda_cartesian(Physics, "P2", [0, 1, 2], "p2")
    assert_tensor_cartesian(Physics, "P2", [0, 1, 2], "p2")

def test_cartesian_p():
    assert_cuda_cartesian(Physics, "P", [0, 1, 2], "p")
    assert_tensor_cartesian(Physics, "P", [0, 1, 2], "p")

def test_polar_beta2():
    assert_cuda_polar(Physics, "Beta2", [0, 1, 2, 3], "beta", 2)
    assert_tensor_polar(Physics, "Beta2", [0, 1, 2, 3], "beta", 2)

def test_polar_beta():
    assert_cuda_polar(Physics, "Beta", [0, 1, 2, 3], "beta")
    assert_tensor_polar(Physics, "Beta", [0, 1, 2, 3], "beta")

def test_cartesian_beta2():
    assert_cuda_cartesian(Physics, "Beta2", [0, 1, 2, 3], "beta", 2)
    assert_tensor_cartesian(Physics, "Beta2", [0, 1, 2, 3], "beta", 2)

def test_cartesian_beta():
    assert_cuda_cartesian(Physics, "Beta", [0, 1, 2, 3], "beta")
    assert_tensor_cartesian(Physics, "Beta", [0, 1, 2, 3], "beta")

def test_polar_M2():
    assert_cuda_polar(Physics, "M2", [0, 1, 2, 3], "M2")
    assert_tensor_polar(Physics, "M2", [0, 1, 2, 3], "M2")

def test_polar_M():
    assert_cuda_polar(Physics, "M", [0, 1, 2, 3], "M")
    assert_tensor_polar(Physics, "M", [0, 1, 2, 3], "M")

def test_cartesian_M2():
    assert_cuda_cartesian(Physics, "M2", [0, 1, 2, 3], "M2")
    assert_tensor_cartesian(Physics, "M2", [0, 1, 2, 3], "M2")

def test_cartesian_M():
    assert_cuda_cartesian(Physics, "M", [0, 1, 2, 3], "M")
    assert_tensor_cartesian(Physics, "M", [0, 1, 2, 3], "M")

def test_polar_Mt2():
    assert_cuda_polar(Physics, "Mt2", [0, 1, 3], "Mt", 2)
    assert_tensor_polar(Physics, "Mt2", [0, 1, 3], "Mt", 2)

def test_polar_Mt():
    assert_cuda_polar(Physics, "Mt", [0, 1, 3], "Mt")
    assert_tensor_polar(Physics, "Mt", [0, 1, 3], "Mt")

def test_cartesian_Mt2():
    assert_cuda_cartesian(Physics, "Mt2", [2, 3], "Mt", 2)
    assert_tensor_cartesian(Physics, "Mt2", [2, 3], "Mt", 2)

def test_cartesian_Mt():
    assert_cuda_cartesian(Physics, "Mt", [2, 3], "Mt")
    assert_tensor_cartesian(Physics, "Mt", [2, 3], "Mt")

def test_polar_theta():
    assert_cuda_polar(Physics, "Theta", [0, 1, 2], "theta")
    assert_tensor_polar(Physics, "Theta", [0, 1, 2], "theta")

def test_cartesian_theta():
    assert_cuda_cartesian(Physics, "Theta", [0, 1, 2], "theta")
    assert_tensor_cartesian(Physics, "Theta", [0, 1, 2], "theta")

def test_polar_deltaR():
    d1 = create_tensor_cpu_1d().to(device = device)
    d2 = create_tensor_cpu_1d().to(device = device)*2
    p1 = create_vector_polar(1, 2, 3, 4)
    p2 = create_vector_polar(2, 4, 6, 8)
    dr = p1.deltaR(p2)
    mrg = torch.cat([d1, d2], -1)
    assert rounder(Physics.Polar.DeltaR(*[mrg[:, i] for i in [1, 5, 2, 6]]), dr)
    assert rounder(Physics.Polar.DeltaR(d1, d2), dr)

    mrg = mrg.to(device = "cpu")
    d1, d2 = d1.to(device = "cpu"), d2.to(device = "cpu")
    assert rounder(Physics.Polar.DeltaR(*[mrg[:, i] for i in [1, 5, 2, 6]]), dr)
    assert rounder(Physics.Polar.DeltaR(d1, d2), dr)

def test_cartesian_deltaR():
    d1 = create_tensor_cpu_1d().to(device = device)
    d2 = create_tensor_cpu_1d().to(device = device)*2
    p1 = create_vector_cartesian(1, 2, 3, 4)
    p2 = create_vector_cartesian(2, 4, 6, 8)
    mrg = torch.cat([d1, d2], -1)
    dr = p1.deltaR(p2)
    assert rounder(Physics.Cartesian.DeltaR(*[mrg[:, i] for i in [0, 4, 1, 5, 2, 6]]), dr)
    assert rounder(Physics.Cartesian.DeltaR(d1, d2), dr)

    mrg = mrg.to(device = "cpu")
    d1, d2 = d1.to(device = "cpu"), d2.to(device = "cpu")
    assert rounder(Physics.Cartesian.DeltaR(*[mrg[:, i] for i in [0, 4, 1, 5, 2, 6]]), dr)
    assert rounder(Physics.Cartesian.DeltaR(d1, d2), dr)

if __name__ == "__main__":
    pass
    test_polar_p2()
    test_polar_p()
    test_cartesian_p2()
    test_cartesian_p()

    test_polar_beta2()
    test_polar_beta()
    test_cartesian_beta2()
    test_cartesian_beta()

    test_polar_M2()
    test_polar_M()
    test_cartesian_M2()
    test_cartesian_M()

    test_polar_Mt2()
    test_polar_Mt()
    test_cartesian_Mt2()
    test_cartesian_Mt()
    test_cartesian_theta()
    test_polar_theta()

    test_polar_deltaR()
    test_cartesian_deltaR()

