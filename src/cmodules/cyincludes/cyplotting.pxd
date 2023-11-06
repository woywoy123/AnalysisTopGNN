from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp cimport bool

from cyplotstruct cimport *

cdef extern from "../plotting/plotting.h":
    cdef cppclass CyPlotting nogil:
        CyPlotting() except +
        paint_t  painter_params
        io_t     file_params
        figure_t figure_params

