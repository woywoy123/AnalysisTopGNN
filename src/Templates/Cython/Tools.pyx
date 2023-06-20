#distutils: language = c++
#cython: language_level=3

from libcpp.string cimport string

cdef extern from "../Headers/Tools.h" namespace "Tools":
    string Hashing(string inpt)

def Hash(str v) -> str:
    return Hashing(<string> v.encode("UTF-8")).decode("UTF-8")
