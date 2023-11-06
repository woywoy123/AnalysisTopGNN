# distuils: language = c++
# cython: language_level = 3

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map, pair
from cytools cimport env, enc

cdef extern from "../abstractions/abstractions.h" namespace "Tools":
    cdef vector[string] split(string, string) except +
    cdef string Hashing(string inpt) except +
    cdef vector[vector[string]] Quantize(vector[string]& v, int n) except +
    cdef map[string, int] CheckDifference(vector[string], vector[string], int i) except +


cpdef list csplit(str val, str delim):
    cdef string x
    return [env(x) for x in split(enc(val), enc(val))]

cpdef str chash(str inpt): return env(Hashing(enc(inpt)))

cpdef list cQuantize(list v, int batch):
    cdef str c
    return Quantize([enc(c) for c in v], batch)

cpdef list cCheckDifference(list inp1, list inp2, int thread):
    cdef str i
    cdef list output = []
    cdef pair[string, int] itr
    for itr in CheckDifference([enc(i) for i in inp1], [enc(i) for i in inp2], thread):
        output.append(env(itr.first))
    return output
