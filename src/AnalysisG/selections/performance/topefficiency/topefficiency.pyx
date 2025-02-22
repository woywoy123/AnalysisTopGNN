# distutils: language=c++
# cython: language_level=3

from AnalysisG.selections.performance.topefficiency.topefficiency cimport *
from AnalysisG.core.selection_template cimport *
from AnalysisG.core.tools cimport *

cdef class TopEfficiency(SelectionTemplate):
    def __cinit__(self):
        self.ptr = new topefficiency()
        self.tt = <topefficiency*>self.ptr

    def __dealloc__(self): del self.tt

    cdef void transform_dict_keys(self):

        self.p_topmass   = as_dict_dict(&self.tt.p_topmass)
        self.t_topmass   = as_dict_dict(&self.tt.t_topmass)

        self.p_zmass     = as_dict_dict(&self.tt.p_zmass)
        self.t_zmass     = as_dict_dict(&self.tt.t_zmass)

        self.prob_tops   = as_dict_dict(&self.tt.prob_tops)
        self.prob_zprime = as_dict_dict(&self.tt.prob_zprime)

        self.t_decay_region = as_dict_dict(&self.tt.t_decay_region)
        self.p_decay_region = as_dict_dict(&self.tt.p_decay_region)

        self.n_tru_tops      = as_basic_dict(&self.tt.n_tru_tops)
        self.n_pred_tops     = as_basic_dict_dict_f(&self.tt.n_pred_tops)
        self.n_perfect_tops  = as_basic_dict_dict_f(&self.tt.n_perfect_tops)

        self.t_nodes  = as_basic_dict_dict_f(&self.tt.t_nodes)
        self.p_nodes  = as_basic_dict_dict_f(&self.tt.p_nodes)

        self.truth_res_edge   = self.tt.truth_res_edge
        self.truth_top_edge   = self.tt.truth_top_edge

        self.truth_ntops      = self.tt.truth_ntops
        self.truth_signal     = self.tt.truth_signal

        self.pred_res_edge_score = self.tt.pred_res_edge_score
        self.pred_top_edge_score = self.tt.pred_top_edge_score

        self.pred_ntops_score    = self.tt.pred_ntops_score
        self.pred_signal_score   = self.tt.pred_signal_score

