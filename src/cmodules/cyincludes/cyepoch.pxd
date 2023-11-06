from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map, pair
from cytools cimport env
from libcpp cimport tuple
from cytypes cimport data_t
from cython.operator cimport dereference


cdef extern from "../epoch/epoch.h":

    cdef struct point_t:
        float minimum
        float maximum
        float average
        float stdev
        vector[float] tmp

    cdef struct roc_t:
        vector[vector[float]] truth
        vector[vector[float]] pred

        map[int, float] auc
        map[int, vector[float]] fpr
        map[int, vector[float]] tpr
        map[int, vector[float]] thre

    cdef struct node_t:
        int max_nodes
        map[int, int] num_nodes

    cdef struct mass_t:
        map[float, int] mass_truth
        map[float, int] mass_pred

    cdef cppclass CyEpoch nogil:
        CyEpoch() except +
        void process_data() except +
        void add_kfold(int, map[string, data_t]*) except +

        map[int, map[string, map[int, mass_t]]] masses
        map[int, map[string, data_t]] container
        map[int, map[string, point_t]] accuracy
        map[int, map[string, point_t]] loss
        map[int, map[string, roc_t]] auc
        map[int, node_t] nodes

        int epoch

cdef inline stats(vector[point_t] inp, point_t* ptr):
    cdef float s = inp.size()

    cdef point_t i
    cdef float av = 0
    cdef float stdev = 0
    for i in inp: av += i.average/s
    for i in inp: stdev += ((av - i.average)**2)/s
    stdev = stdev**0.5
    ptr.average = av
    ptr.stdev = stdev
    ptr.minimum = av - stdev
    ptr.maximum = av + stdev
