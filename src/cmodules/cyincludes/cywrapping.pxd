from libcpp cimport bool
from cytypes cimport code_t

cdef class OptimizerWrapper:
    cdef _optim
    cdef _sched
    cdef _model

    cdef str _path
    cdef str _outdir
    cdef str _run_name
    cdef str _optimizer_name
    cdef str _scheduler_name

    cdef int _epoch
    cdef bool _train
    cdef dict _state
    cdef dict _optim_params
    cdef dict _sched_params

cdef class ModelWrapper:
    cdef str  _run_name
    cdef str  _path

    cdef dict _params
    cdef dict _in_map
    cdef dict _out_map
    cdef dict _loss_map
    cdef dict _class_map
    cdef int  _epoch
    cdef bool _train

    cdef code_t _code
    cdef _model
    cdef _loss_sum


