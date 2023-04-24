# cython: linetrace=True

from libc.math cimport sin, cos, sinh, atan2, asinh, pow

__all__ = ["Px", "Py", "Pz", "PT", "Phi", "Eta", "PxPyPzEMass", "deltaR", "energy", "IsIn"]

cpdef double Px(double pt, double phi):
    return pt*cos(phi)

cpdef double Py(double pt, double phi):
    return pt*sin(phi)

cpdef double Pz(double pt, double eta):
    return pt*sinh(eta)

cpdef double PT(double px, double py):
    return pow( pow(px, 2) + pow(py, 2), 0.5 )

cpdef double Phi(double px, double py):
    return atan2(py, px)

cpdef double Eta(double px, double py, double pz):
    cdef double pt = PT(px, py)
    return asinh(pz/pt)

cpdef double PxPyPzEMass(double px, double py, double pz, double e):
    cdef double s = pow(e, 2) - pow(px, 2) - pow(py, 2) - pow(pz, 2)
    if s < 0:
        return 0
    return pow(s, 0.5)/1000

cpdef double deltaR(double eta1, double eta2, double phi1, double phi2):
    return pow(pow(eta1 - eta2, 2) + pow(phi1 - phi2, 2), 0.5)

cpdef double energy(double m, double px, double py, double pz):
    cdef double p2 = pow(px, 2) + pow(py, 2) + pow(pz, 2)
    return pow( p2 + pow(m, 2), 0.5 )

cpdef IsIn(list srch, dict objdic):
    cdef str l
    cdef int cnt = 0
    for l in srch:
        if l in objdic: 
            cnt += 1
    if len(srch) == cnt:
        return True
    return False
