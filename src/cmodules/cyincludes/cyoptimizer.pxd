from cytypes cimport folds_t, data_t
from libcpp.vector cimport vector
from libcpp.string cimport string, stoi
from libcpp.map cimport map, pair
from libcpp cimport bool

from cyepoch cimport CyEpoch
from cytools cimport env, enc
from cython.operator cimport dereference

from tqdm import trange
import numpy as np

cdef extern from "../optimizer/optimizer.h" namespace "Optimizer":
    cdef cppclass CyOptimizer nogil:
        CyOptimizer() except +

        void register_fold(const folds_t* inpt) except +
        void train_epoch_kfold(int epoch, int kfold, map[string, data_t]* data) except +
        void validation_epoch_kfold(int epoch, int kfold, map[string, data_t]* data) except +
        void evaluation_epoch_kfold(int epoch, int kfold, map[string, data_t]* data) except +

        void flush_train(vector[string]*, int) except +
        void flush_validation(vector[string]*, int) except +
        void flush_evaluation(vector[string]*) except +

        vector[vector[string]] fetch_train(int kfold, int batch) except +
        vector[vector[string]] fetch_validation(int kfold, int batch) except +
        vector[vector[string]] fetch_evaluation(int batch) except +

        vector[string] check_train(vector[string]*, int) except +
        vector[string] check_validation(vector[string]*, int) except +
        vector[string] check_evaluation(vector[string]*) except +

        map[string, int] fold_map() except +

        vector[int] use_folds
        map[int, CyEpoch*] epoch_train
        map[int, CyEpoch*] epoch_valid
        map[int, CyEpoch*] epoch_test

cdef inline vector[folds_t] kfold_build(string* hash_, vector[tuple[string, bool]]* kf) noexcept nogil:
    cdef vector[folds_t] folds
    cdef folds_t fold = folds_t()
    fold.event_hash = dereference(hash_)
    fold.train = False
    fold.test = False
    fold.evaluation = False

    cdef tuple[string, bool] i
    for i in dereference(kf):
        if not i[0].rfind(b"k-", 0): folds.push_back(fold)
        elif not i[0].rfind(b"train", 0): fold.train = True
        elif not i[0].rfind(b"test", 0):  fold.test = True

    if not fold.train:
        folds.push_back(fold)
        return folds

    cdef int idx = 0
    cdef string mode
    for i in dereference(kf):
        mode = i[0]
        if mode.rfind(b"k-", 0): continue
        folds[idx].kfold = stoi(mode.substr(2, mode.size()))
        if i[1]: folds[idx].train = True
        else: folds[idx].evaluation = True
        idx += 1
    return folds

cdef inline void _check_h5(f, str key, data_t* inpt):
    f.create_dataset(key + "-truth"       , data = np.array(inpt.truth),     chunks = True)
    f.create_dataset(key + "-pred"        , data = np.array(inpt.pred) ,     chunks = True)
    f.create_dataset(key + "-index"       , data = np.array(inpt.index),     chunks = True)
    f.create_dataset(key + "-nodes"       , data = np.array(inpt.nodes),     chunks = True)
    f.create_dataset(key + "-loss"        , data = np.array(inpt.loss) ,     chunks = True)
    f.create_dataset(key + "-accuracy"    , data = np.array(inpt.accuracy),  chunks = True)

    cdef pair[int, vector[vector[float]]] itr
    if len(inpt.mass_pred): pass
    else: return
    for itr in inpt.mass_pred: f.create_dataset(key + "-masses-pred ->" + str(itr.first), data = np.array(itr.second),  chunks = True)
    for itr in inpt.mass_truth: f.create_dataset(key + "-masses-truth ->" + str(itr.first), data = np.array(itr.second),  chunks = True)

cdef inline void _rebuild_h5(f, list var, CyOptimizer* ptr, string mode, int epoch, int kfold):
    cdef map[string, data_t] mp_data
    cdef data_t* data

    try: file = f[env(mode)]
    except KeyError: return

    cdef str i, key
    cdef int idx = 0
    cdef int idy = 0
    cdef int chnks = 1000000
    cdef int end = file[var[0] + "-truth"].shape[0]
    for _ in trange(0, int(end/chnks)+1):
        idy = (end - idy)%chnks + idy
        for key in var:
            mp_data[enc(key)] = data_t()
            data = &mp_data[enc(key)]
            data.truth = <vector[vector[float]]>file[key + "-truth"][idx : idy].tolist()
            data.pred = <vector[vector[float]]>file[key + "-pred"][idx : idy].tolist()
            data.index = <vector[vector[float]]>file[key + "-index"][idx : idy].tolist()
            data.nodes = <vector[vector[float]]>file[key + "-nodes"][idx : idy].tolist()
            data.loss = <vector[vector[float]]>file[key + "-loss"][idx : idy].tolist()
            data.accuracy = <vector[vector[float]]>file[key + "-accuracy"][idx : idy].tolist()
            for i in file:
                if not "masses" in i or key not in i: continue
                if "pred"  in i: data.mass_pred[int(i.split("->")[1])]  = <vector[vector[float]]>file[i][idx : idy].tolist()
                if "truth" in i: data.mass_truth[int(i.split("->")[1])] = <vector[vector[float]]>file[i][idx : idy].tolist()
        if   mode == b"training": ptr.train_epoch_kfold(epoch, kfold, &mp_data)
        elif mode == b"validation": ptr.validation_epoch_kfold(epoch, kfold, &mp_data)
        elif mode == b"evaluation": ptr.evaluation_epoch_kfold(epoch, kfold, &mp_data)
        mp_data.clear()
        idx = idy
        idy = idy + chnks
    if   mode == b"training"   and ptr.epoch_train.count(epoch): ptr.epoch_train[epoch].process_data()
    elif mode == b"validation" and ptr.epoch_valid.count(epoch): ptr.epoch_valid[epoch].process_data()
    elif mode == b"evaluation" and ptr.epoch_test.count(epoch):  ptr.epoch_test[epoch].process_data()


cdef struct report_t:
    int current_epoch
    map[string, float] auc_train
    map[string, float] auc_valid
    map[string, float] auc_eval

    map[string, float] loss_train
    map[string, float] loss_valid
    map[string, float] loss_eval

    map[string, float] loss_train_up
    map[string, float] loss_valid_up
    map[string, float] loss_eval_up

    map[string, float] loss_train_down
    map[string, float] loss_valid_down
    map[string, float] loss_eval_down


    map[string, float] acc_train
    map[string, float] acc_valid
    map[string, float] acc_eval

    map[string, float] acc_train_up
    map[string, float] acc_valid_up
    map[string, float] acc_eval_up

    map[string, float] acc_train_down
    map[string, float] acc_valid_down
    map[string, float] acc_eval_down
