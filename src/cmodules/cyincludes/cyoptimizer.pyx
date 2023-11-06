# distutils: language = c++
# cython: language_level = 3

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.map cimport map, pair
from libcpp cimport tuple
from libcpp cimport bool

from cython.operator cimport dereference
from cython.parallel cimport prange

from cytools cimport env, enc, penc, pdec, map_to_dict, recast
from cytypes cimport folds_t, data_t, graph_t
from cyoptimizer cimport *
from cyepoch cimport *

from torchmetrics.classification import MulticlassROC, MulticlassAUROC
from AnalysisG.Plotting import TH1F, TLine
from torch_geometric.data import Batch
from tqdm import trange
import numpy as np
import pickle
import torch
import h5py



cdef _check_sub(f, str key):
    try: return f.create_group(key)
    except ValueError: return f[key]

cdef struct k_graphed:
    string pkl
    int node_size

cdef dict template_th1f(str path, str xtitle, str ytitle, str title, float xstep):
    cdef dict output = {}
    output["OutputDirectory"] = path
    output["Histograms"] = []
    output["Filename"] = ""
    output["xTitle"] = xtitle
    output["yTitle"] = ytitle
    output["xBins"] = 1500
    output["xMin"] = 0
    output["xMax"] = 1500
    output["Title"] = title
    output["xStep"] = xstep
    output["OverFlow"] = True
    output["OverlayHists"] = True
    return output

cdef dict template_tline(str path, str xtitle, str ytitle, str title):
    cdef dict output = {}
    output["OutputDirectory"] = path
    output["Filename"] = ""
    output["xTitle"] = xtitle
    output["yTitle"] = ytitle
    output["xMin"] = 0
    output["yMin"] = 0
    output["Title"] = title
    output["yDataUp"] = []
    output["yDataDown"] = []
    output["xData"] = []
    return output

cdef tuple collapse_masses(map[int, CyEpoch*] data, str mode, str path):
    cdef pair[int, CyEpoch*] its
    cdef string name

    cdef str pth, p_, filename
    cdef int cls, kf
    cdef dict m, con, mass

    cdef dict output = {}
    cdef dict truth = {}

    for its in data:
        pth = path + "/Epoch-" + str(its.first)
        for kf, con in dict(its.second.masses).items():
            for name, mass in con.items():
                for cls, m in mass.items():
                    p_ = pth + "/kfold-" + str(kf) + "/" + env(name)
                    filename = "classification-" + str(cls)
                    if p_ not in output:
                        output[p_] = {}
                        output[p_][filename] = {"Title" : mode, "xData" : []}

                        truth[p_] = {}
                        truth[p_][filename] = {"Title" : "Truth", "xData" : []}

                    output[p_][filename]["xData"] += m["mass_pred"]
                    truth[p_][filename]["xData"]  += m["mass_truth"]
                its.second.masses[kf][name].clear()
        its.second.masses.clear()
    return truth, output

cdef void make_mass_plots(map[int, CyEpoch*] train, map[int, CyEpoch*] valid, map[int, CyEpoch*] test, str path):
    cdef tuple tr = collapse_masses(train, "training", path)
    cdef tuple va = collapse_masses(valid, "validation", path)
    cdef tuple te = collapse_masses(test, "evaluation", path)

    tr_t, tr_p = tr
    va_t, va_p = va
    ev_t, ev_p = te
    cdef str mva, kf, x, file_n
    cdef dict tmpl
    cdef list files, xData

    for file_n in set(sum([list(tr_t), list(va_t), list(ev_t)], [])):
        mva = file_n.split("/")[-1]
        kf = file_n.split("/")[-2]
        mva = "Reconstructed Mass Using MVA: " + mva + " " + kf
        files = []
        if file_n in tr_t: files += list(tr_t[file_n])
        if file_n in va_t: files += list(va_t[file_n])
        if file_n in ev_t: files += list(ev_t[file_n])
        for x in set(files):
            xData = []
            tmpl = template_th1f(file_n, "Mass (GeV)", "Entries <unit>", mva, 100)
            tmpl["Filename"] = x
            try: tmpl["Histograms"] += [TH1F(**tr_p[file_n][x])]
            except KeyError: pass

            try: tmpl["Histograms"] += [TH1F(**va_p[file_n][x])]
            except KeyError: pass

            try: tmpl["Histograms"] += [TH1F(**ev_p[file_n][x])]
            except KeyError: pass

            try: xData += va_t[file_n][x]["xData"]
            except KeyError: pass
            try: xData += ev_t[file_n][x]["xData"]
            except KeyError: pass
            try: xData += tr_t[file_n][x]["xData"]
            except KeyError: pass
            tmpl["Histogram"] = TH1F(**{"Title" : "Truth", "xData" : xData, "Color": "b"})
            tmpl["yLogarithmic"] = True
            th = TH1F(**tmpl)
            th.SaveFigure()
            del th

cdef dict collapse_points(map[string, vector[point_t]]* tmp, int epoch, dict lines, str mode, report_t* state, str metric):
    cdef pair[string, vector[point_t]]itv
    cdef point_t pnt
    cdef str var_name

    for itv in dereference(tmp):
        pnt = point_t()
        stats(itv.second, &pnt)
        var_name = env(itv.first)
        if var_name not in lines: lines[var_name] = {}
        if mode not in lines[var_name]:
            lines[var_name][mode] = {"yDataDown" : [], "yDataUp" : [], "xData" : [], "yData" : [], "Title" : mode}
        lines[var_name][mode]["yDataDown"].append(pnt.stdev)
        lines[var_name][mode]["yDataUp"].append(pnt.stdev)
        lines[var_name][mode]["yData"].append(pnt.average)
        lines[var_name][mode]["xData"].append(epoch)
        if   metric == "auc" and mode == "training"  : state.auc_train[itv.first] = pnt.average
        elif metric == "auc" and mode == "validation": state.auc_valid[itv.first] = pnt.average
        elif metric == "auc" and mode == "evaluation": state.auc_eval[itv.first] = pnt.average

        elif metric == "acc" and mode == "training"  :
            state.acc_train[itv.first]      = pnt.average
            state.acc_train_up[itv.first]   = pnt.maximum
            state.acc_train_down[itv.first] = pnt.minimum

        elif metric == "acc" and mode == "validation":
            state.acc_valid[itv.first]      = pnt.average
            state.acc_valid_up[itv.first]   = pnt.maximum
            state.acc_valid_down[itv.first] = pnt.minimum

        elif metric == "acc" and mode == "evaluation":
            state.acc_eval[itv.first]      = pnt.average
            state.acc_eval_up[itv.first]   = pnt.maximum
            state.acc_eval_down[itv.first] = pnt.minimum

        elif metric == "lss" and mode == "training"  :
            state.loss_train[itv.first]      = pnt.average
            state.loss_train_up[itv.first]   = pnt.maximum
            state.loss_train_down[itv.first] = pnt.minimum

        elif metric == "lss" and mode == "validation":
            state.loss_valid[itv.first]      = pnt.average
            state.loss_valid_up[itv.first]   = pnt.maximum
            state.loss_valid_down[itv.first] = pnt.minimum

        elif metric == "lss" and mode == "evaluation":
            state.loss_eval[itv.first]      = pnt.average
            state.loss_eval_up[itv.first]   = pnt.maximum
            state.loss_eval_down[itv.first] = pnt.minimum
    return lines

cdef void make_accuracy_plots(map[int, CyEpoch*] train, map[int, CyEpoch*] valid, map[int, CyEpoch*] test, str path, report_t* state):
    cdef pair[int, CyEpoch*] itr
    cdef pair[string, point_t] its
    cdef pair[string, vector[point_t]] itv

    cdef map[string, vector[point_t]] tmp_tr
    cdef map[string, vector[point_t]] tmp_va
    cdef map[string, vector[point_t]] tmp_te

    cdef list folds = []
    cdef list epochs = []
    cdef int epoch, kf

    for itr in train:
        folds += list(train[itr.first].accuracy)
        epochs += [itr.first]

    for itr in valid:
        folds += list(valid[itr.first].accuracy)
        epochs += [itr.first]

    for itr in test:
        folds += list(test[itr.first].accuracy)
        epochs += [itr.first]

    cdef point_t pnt
    cdef dict lines = {}
    for epoch in sorted(set(epochs)):
        for kf in sorted(set(folds)):
            if train.count(epoch) and train[epoch].accuracy.count(kf):
                for its in train[epoch].accuracy[kf]: tmp_tr[its.first].push_back(its.second)
            if valid.count(epoch) and valid[epoch].accuracy.count(kf):
                for its in valid[epoch].accuracy[kf]: tmp_va[its.first].push_back(its.second)
            if test.count(epoch) and test[epoch].accuracy.count(kf):
                for its in test[epoch].accuracy[kf]: tmp_te[its.first].push_back(its.second)

        lines = collapse_points(&tmp_tr, epoch, lines, "training", state, "acc")
        lines = collapse_points(&tmp_va, epoch, lines, "validation", state, "acc")
        lines = collapse_points(&tmp_te, epoch, lines, "evaluation", state, "acc")

    for var_name in lines:
        for mode in lines[var_name]: lines[var_name][mode] = TLine(**lines[var_name][mode])
        tmpl = template_tline(path, "Epoch", "Accuracy", "Achieved Accuracy of " + var_name)
        tmpl["Filename"] = var_name + "_accuracy"
        tmpl["Lines"] = list(lines[var_name].values())
        tl = TLine(**tmpl)
        tl.SaveFigure()
        del tl

cdef void make_loss_plots(map[int, CyEpoch*] train, map[int, CyEpoch*] valid, map[int, CyEpoch*] test, str path, report_t* state):
    cdef pair[int, CyEpoch*] itr
    cdef pair[string, point_t] its
    cdef pair[string, vector[point_t]] itv

    cdef map[string, vector[point_t]] tmp_tr
    cdef map[string, vector[point_t]] tmp_va
    cdef map[string, vector[point_t]] tmp_te

    cdef list folds = []
    cdef list epochs = []
    cdef int epoch, kf

    for itr in train:
        folds += list(train[itr.first].loss)
        epochs += [itr.first]

    for itr in valid:
        folds += list(valid[itr.first].loss)
        epochs += [itr.first]

    for itr in test:
        folds += list(test[itr.first].loss)
        epochs += [itr.first]

    cdef point_t pnt
    cdef dict lines = {}
    for epoch in sorted(set(epochs)):
        for kf in sorted(set(folds)):
            if train.count(epoch) and train[epoch].loss.count(kf):
                for its in train[epoch].loss[kf]: tmp_tr[its.first].push_back(its.second)
            if valid.count(epoch) and valid[epoch].loss.count(kf):
                for its in valid[epoch].loss[kf]: tmp_va[its.first].push_back(its.second)
            if test.count(epoch) and test[epoch].loss.count(kf):
                for its in test[epoch].loss[kf]: tmp_te[its.first].push_back(its.second)

        lines = collapse_points(&tmp_tr, epoch, lines, "training", state, "lss")
        lines = collapse_points(&tmp_va, epoch, lines, "validation", state, "lss")
        lines = collapse_points(&tmp_te, epoch, lines, "evaluation", state, "lss")

    for var_name in lines:
        for mode in lines[var_name]:
            lines[var_name][mode] = TLine(**lines[var_name][mode])
        tmpl = template_tline(path, "Epoch", "Loss (arb.)", "Loss Curve for " + var_name)
        tmpl["Filename"] = var_name + "_loss"
        tmpl["Lines"] = list(lines[var_name].values())
        tl = TLine(**tmpl)
        tl.SaveFigure()
        del tl

cdef dict make_roc_curve(map[string, roc_t]* roc_, dict lines, str mode):
    cdef pair[string, roc_t] its

    for its in dereference(roc_):
        if not its.second.pred.size(): continue
        pred = torch.tensor(its.second.pred)
        dereference(roc_)[its.first].pred.clear()

        tru = torch.tensor(its.second.truth, dtype = torch.long).view(-1)
        dereference(roc_)[its.first].truth.clear()
        roc = MulticlassROC(**{"num_classes": pred.size()[1]})
        auc = MulticlassAUROC(**{"num_classes": pred.size()[1]})
        fpr, tpr, thres = roc(pred, tru)
        auc_ = auc(pred, tru).view(-1)
        del tru
        del pred
        for cls in range(len(fpr)):
            its.second.fpr[cls] = fpr[cls].tolist()
            its.second.tpr[cls] = tpr[cls].tolist()
            its.second.thre[cls] = thres[cls].tolist()
            try: dereference(roc_)[its.first].auc[cls+1] = auc_[cls].item()
            except IndexError: pass
            name = "ROC Curve: "+ env(its.first) + " classification - " + str(cls)
            if name not in lines: lines[name] = []
            lines[name] += [TLine(**{"xData" : its.second.fpr[cls], "yData" : its.second.tpr[cls], "Title" : mode})]
        its.second.fpr.clear()
        its.second.tpr.clear()
        its.second.thre.clear()
    return lines

cdef void make_auc_curve(map[string, roc_t]* roc_, map[string, vector[point_t]]* auc_):
    cdef pair[string, roc_t] its
    cdef pair[int, float] iti
    cdef point_t data
    for its in dereference(roc_):
        for iti in its.second.auc:
            data = point_t()
            data.average = iti.second
            dereference(auc_)[enc(env(its.first) + " classification - " + str(iti.first))].push_back(data)


cdef void make_roc_plots(map[int, CyEpoch*] train, map[int, CyEpoch*] valid, map[int, CyEpoch*] test, str path, report_t* state):
    cdef pair[int, CyEpoch*] itr

    cdef dict tmp_tr = {}
    cdef dict tmp_va = {}
    cdef dict tmp_te = {}

    cdef list folds = []
    cdef list epochs = []
    cdef int epoch, kf
    cdef pair[int, map[string, roc_t]] itx

    for itr in train:
        folds += [itx.first for itx in train[itr.first].auc]
        epochs += [itr.first]

    for itr in valid:
        folds += [itx.first for itx in valid[itr.first].auc]
        epochs += [itr.first]

    for itr in test:
        folds += [itx.first for itx in test[itr.first].auc]
        epochs += [itr.first]

    cdef dict lines
    cdef dict line_auc = {}
    cdef map[string, vector[point_t]] auc_tr
    cdef map[string, vector[point_t]] auc_va
    cdef map[string, vector[point_t]] auc_ev

    for epoch in sorted(set(epochs)):
        for kf in sorted(set(folds)):
            lines = {}
            if train.count(epoch) and train[epoch].auc.count(kf):
                lines = make_roc_curve(&train[epoch].auc[kf], lines, "training")
                make_auc_curve(&train[epoch].auc[kf], &auc_tr)

            if valid.count(epoch) and valid[epoch].auc.count(kf):
                lines = make_roc_curve(&valid[epoch].auc[kf], lines, "validation")
                make_auc_curve(&valid[epoch].auc[kf], &auc_va)

            if test.count(epoch) and test[epoch].auc.count(kf):
                lines = make_roc_curve(&test[epoch].auc[kf], lines, "evaluation")
                make_auc_curve(&test[epoch].auc[kf], &auc_ev)

            for name in lines:
                fname = name.split(" ")[2].replace(" ", "")
                cls = name.split("-")[1].replace(" ", "")

                pth = path + "/ROC/Epoch-" + str(epoch) + "/classification-" + cls + "/kfold-" + str(kf)
                tmpl = template_tline(pth, "False Positive Rate", "True Positive Rate", name + " @ Epoch: " + str(epoch))
                tmpl["Filename"] = fname + "_epoch_" + str(epoch)
                tmpl["Lines"] = lines[name]
                tl = TLine(**tmpl)
                tl.SaveFigure()
                del tl

        line_auc = collapse_points(&auc_tr, epoch, line_auc, "training", state, "auc")
        line_auc = collapse_points(&auc_va, epoch, line_auc, "validation", state, "auc")
        line_auc = collapse_points(&auc_ev, epoch, line_auc, "evaluation", state, "auc")

    for var_name in line_auc:
        for mode in line_auc[var_name]: line_auc[var_name][mode] = TLine(**line_auc[var_name][mode])
        pth = path + "/AUC/classification-" + var_name.split("-")[-1].replace(" ", "")
        tmpl = template_tline(pth, "Epoch", "Area Under Curve", "Area Under Curve of MVA: " + var_name)
        tmpl["Filename"] = var_name.split(" ")[0]
        tmpl["Lines"] = list(line_auc[var_name].values())

        tl = TLine(**tmpl)
        tl.SaveFigure()
        del tl

cdef void make_nodes(map[int, CyEpoch*] train, map[int, CyEpoch*] valid, map[int, CyEpoch*] test, str path):
    cdef pair[int, CyEpoch*] its
    cdef pair[int, node_t] nd
    cdef dict hist = {
            "training"  : {"xData" : [], "Title" : "training"},
            "validation": {"xData" : [], "Title" : "validation"},
            "evaluation": {"xData" : [], "Title" : "evaluation"}
    }

    cdef int mx_ = 0
    for its in train:
        for nd in its.second.nodes:
            hist["training"]["xData"] += sum([[i]*j for i, j in dict(nd.second.num_nodes).items()], [])
            m = max(hist["training"]["xData"])
            if m > mx_: mx_ = m
        break

    for its in valid:
        for nd in its.second.nodes:
            hist["validation"]["xData"] += sum([[i]*j for i, j in dict(nd.second.num_nodes).items()], [])
            m = max(hist["validation"]["xData"])
            if m > mx_: mx_ = m
        break

    for its in test:
        for nd in its.second.nodes:
            hist["evaluation"]["xData"] += sum([[i]*j for i, j in dict(nd.second.num_nodes).items()], [])
            m = max(hist["evaluation"]["xData"])
            if m > mx_: mx_ = m
        break

    tmpl = template_th1f(path, "Number of Nodes", "Entries (arb.)", "Node Distribution for Sample Type", 1)
    tmpl["Filename"] = "NodeStatistics"
    tmpl["xBins"] = mx_ + 1
    tmpl["xMax"] = mx_ + 1
    tmpl["Stack"] = True
    tmpl["OverlayHists"] = False
    tmpl["xBinCentering"] = True
    for node in hist: tmpl["Histograms"] += [TH1F(**hist[node])]
    th = TH1F(**tmpl)
    th.SaveFigure()



cdef class DataLoader:

    cdef CyOptimizer* ptr
    cdef map[string, k_graphed] data
    cdef map[string, k_graphed*] this_batch
    cdef map[int, vector[string]] batch_hash

    cdef int indx_s
    cdef int indx_e
    cdef int kfold
    cdef string mode

    cdef str device
    cdef dict online
    cdef public bool purge
    cdef public sampletracer

    def __cinit__(self):
        self.sampletracer = None
        self.purge = False
        self.online = {}

    def __init__(self): pass
    def __dealloc__(self): pass
    def __len__(self): return self.batch_hash.size()

    cdef DataLoader set_batch(self, int kfold, int batch_size, string mode):
        cdef vector[vector[string]] batches
        if   mode == b"train": batches = self.ptr.fetch_train(kfold, batch_size)
        elif mode == b"valid": batches = self.ptr.fetch_validation(kfold, batch_size)
        elif mode == b"eval":  batches = self.ptr.fetch_evaluation(batch_size)
        else: return self

        self.device = self.sampletracer.Device
        self.this_batch.clear()
        self.batch_hash.clear()
        self.kfold = kfold
        self.mode = mode

        cdef int idx
        cdef string hash_
        cdef int size = batches.size()
        cdef map[string, k_graphed*] to_fetch
        for idx in prange(size, nogil = True, num_threads = size):
            if   mode == b"train": self.batch_hash[idx] = self.ptr.check_train(&batches[idx], kfold)
            elif mode == b"valid": self.batch_hash[idx] = self.ptr.check_validation(&batches[idx], kfold)
            elif mode == b"eval":  self.batch_hash[idx] = self.ptr.check_evaluation(&batches[idx])
            for hash_ in batches[idx]: self.this_batch[hash_] = &self.data[hash_]
            for hash_ in self.batch_hash[idx]: to_fetch[hash_] = &self.data[hash_]
            if self.batch_hash[idx].size(): pass
            else: self.batch_hash[idx] = batches[idx]
        self.indx_e = size

        if not to_fetch.size(): return self
        cdef pair[string, k_graphed*] itr
        cdef vector[string] cfetch = [itr.first for itr in to_fetch]
        cdef list fetch = pdec(&cfetch)
        self.sampletracer.RestoreGraphs(fetch)

        cdef map[string, graph_t] graphs = self.sampletracer.makelist(fetch, True)[1]
        if not graphs.size(): self.ptr.flush_train(&cfetch, self.kfold)
        else: self.sampletracer.FlushGraphs(fetch)

        cdef graph_t* gr
        for idx in prange(graphs.size(), nogil = True, num_threads = graphs.size()):
            gr = &graphs[cfetch[idx]]
            to_fetch[gr.event_hash].pkl = gr.pickled_data
            to_fetch[gr.event_hash].node_size = gr.hash_particle.size()
        graphs.clear()
        return self

    def __iter__(self):
        self.indx_s = 0
        return self

    def __next__(self):
        if self.indx_s == self.indx_e: raise StopIteration
        cdef vector[string]* hash_ = &self.batch_hash[self.indx_s]
        if not len(self.sampletracer.MonitorMemory("Graph")): pass
        elif self.mode.compare(b"train"): self.ptr.flush_train(hash_, self.kfold)
        elif self.mode.compare(b"valid"): self.ptr.flush_validation(hash_, self.kfold)
        elif self.mode.compare(b"eval"):  self.ptr.flush_evaluation(hash_)
        self.indx_s += 1

        cdef list out = []
        cdef string t_hash
        cdef k_graphed* gr
        for t_hash in dereference(hash_):
            try: data = self.online[env(t_hash)]
            except KeyError:
                gr = self.this_batch[t_hash]
                if gr.pkl.size(): pass
                else: return None
                data = pickle.loads(gr.pkl).to(device = self.device)
                self.online[env(t_hash)] = data
            out.append(data)

        cdef int idx = self.sampletracer.MaxGPU
        cdef tuple cuda = (None, None)
        if idx != -1:
            try: cuda = torch.cuda.mem_get_info()
            except RuntimeError: pass

        if cuda[0] is not None and (cuda[1] - cuda[0])/(1024**3) > idx:
            self.purge = True
            data = Batch().from_data_list(out)
            for k in self.online.values(): del k
            torch.cuda.empty_cache()
            return data
        self.purge = False
        return Batch().from_data_list(out)




cdef class cOptimizer:
    cdef CyOptimizer* ptr
    cdef DataLoader data

    cdef dict online_
    cdef map[string, k_graphed] graphs_
    cdef vector[string] cached_

    cdef bool _train
    cdef bool _test
    cdef bool _val

    cdef report_t state
    cdef public bool metric_plots
    cdef public sampletracer

    def __cinit__(self):
        self.ptr = new CyOptimizer()
        self.data = DataLoader()
        self.data.ptr = self.ptr
        self.sampletracer = None
        self._train = False
        self._test = False
        self._val = False
        self.state = report_t()

    def __init__(self):
        pass

    def __dealloc__(self):
        del self.ptr

    def length(self):
        return map_to_dict(<map[string, int]>self.ptr.fold_map())

    @property
    def kFolds(self): return self.ptr.use_folds

    cpdef report_t reportable(self): return self.state

    cpdef bool GetHDF5Hashes(self, str path):
        if path.endswith(".hdf5"): pass
        else: path += ".hdf5"

        try: f = h5py.File(path, "r")
        except FileNotFoundError: return False

        cdef bool k
        cdef str h_, h__
        cdef map[string, vector[tuple[string, bool]]] res
        for h_ in f: res[enc(h_)] = [(enc(h__), k) for h__, k in f[h_].attrs.items()]
        cdef vector[string] idx = <vector[string]>(list(res))

        cdef int i, j
        cdef map[string, vector[folds_t]] output
        for i in prange(idx.size(), nogil = True, num_threads = idx.size()):
            output[idx[i]] = kfold_build(&idx[i], &res[idx[i]])
            for j in range(output[idx[i]].size()): self.ptr.register_fold(&output[idx[i]][j])
        output.clear()
        return True

    cpdef UseAllHashes(self, list inpt):
        cdef int idx
        cdef folds_t fold_hash
        cdef vector[string] data = penc(inpt)
        for idx in prange(data.size(), nogil = True, num_threads = 12):
            fold_hash = folds_t()
            fold_hash.kfold = 1
            fold_hash.train = True
            fold_hash.event_hash = data[idx]
            self.ptr.register_fold(&fold_hash)
        data.clear()

    def FetchTraining(self, int kfold, int batch_size):
        if self.data.sampletracer is not None: pass
        else: self.data.sampletracer = self.sampletracer
        self._train = True
        self._val = False
        self._test = False
        return self.data.set_batch(kfold, batch_size, b"train")

    def FetchValidation(self, int kfold, int batch_size):
        if self.data.sampletracer is not None: pass
        else: self.data.sampletracer = self.sampletracer
        self._train = False
        self._val = True
        self._test = False
        return self.data.set_batch(kfold, batch_size, b"valid")

    def FetchEvaluation(self, int batch_size):
        if self.data.sampletracer is not None: pass
        else: self.data.sampletracer = self.sampletracer
        self._train = False
        self._val = False
        self._test = True
        return self.data.set_batch(-1, batch_size, b"eval")

    def UseTheseFolds(self, list inpt): self.ptr.use_folds = <vector[int]>inpt

    cpdef AddkFold(self, int epoch, int kfold, dict inpt, dict out_map):
        cdef map[string, data_t] map_data = recast(inpt, out_map)
        if  self._train: self.ptr.train_epoch_kfold(epoch, kfold, &map_data)
        elif  self._val: self.ptr.validation_epoch_kfold(epoch, kfold, &map_data)
        elif self._test: self.ptr.evaluation_epoch_kfold(epoch, kfold, &map_data)
        map_data.clear()

    cpdef FastGraphRecast(self, int epoch, int kfold, list inpt, dict out_map):
        cdef str key
        cdef int i, l
        cdef list graphs
        cdef map[string, data_t] map_data
        for i in trange(len(inpt)):
            graphs = inpt[i].pop("graphs")
            graphs = [Batch().from_data_list(graphs)]
            graphs = [{k : j.numpy(force = True) for k, j in k.to_dict().items()} for k in graphs[0].to_data_list()]
            for k in inpt[i]:
                if not isinstance(inpt[i][k], dict): inpt[i][k] = inpt[i][k].numpy(force = True)
                else: inpt[i][k] = {l : inpt[i][k][l].numpy(force = True) for l in inpt[i][k]}
            inpt[i]["graphs"] = graphs
            map_data = recast(inpt[i], out_map)
            if  self._train: self.ptr.train_epoch_kfold(epoch, kfold, &map_data)
            elif  self._val: self.ptr.validation_epoch_kfold(epoch, kfold, &map_data)
            elif self._test: self.ptr.evaluation_epoch_kfold(epoch, kfold, &map_data)
            map_data.clear()

    cpdef DumpEpochHDF5(self, int epoch, str path, int kfold):

        cdef CyEpoch* ep
        cdef pair[string, data_t] dt
        f = h5py.File(path + str(kfold) + "/epoch_data.hdf5", "w")
        if self.ptr.epoch_train.count(epoch):
            grp = _check_sub(f, "training")
            ep = self.ptr.epoch_train[epoch]
            for dt in ep.container[kfold]: _check_h5(grp, env(dt.first), &dt.second)
            ep.process_data()
        if self.ptr.epoch_valid.count(epoch):
            grp = _check_sub(f, "validation")
            ep = self.ptr.epoch_valid[epoch]
            for dt in ep.container[kfold]: _check_h5(grp, env(dt.first), &dt.second)
            ep.process_data()

        if self.ptr.epoch_test.count(epoch):
            grp = _check_sub(f, "evaluation")
            ep = self.ptr.epoch_test[epoch]
            for dt in ep.container[kfold]: _check_h5(grp, env(dt.first), &dt.second)
            ep.process_data()
        f.close()


    cpdef RebuildEpochHDF5(self, int epoch, str path, int kfold):
        f = h5py.File(path + str(kfold) + "/epoch_data.hdf5", "r")

        cdef str key
        cdef dict unique = {}
        for key in f["training"].keys():
            key = key.split("-")[0]
            if key in unique: pass
            else: unique[key] = None
        _rebuild_h5(f, list(unique), self.ptr, b"training"  , epoch, kfold)
        _rebuild_h5(f, list(unique), self.ptr, b"validation", epoch, kfold)
        _rebuild_h5(f, list(unique), self.ptr, b"evaluation", epoch, kfold)
        f.close()


    cpdef BuildPlots(self, int epoch, str path):
        make_mass_plots(self.ptr.epoch_train, self.ptr.epoch_valid, self.ptr.epoch_test, path)
        make_accuracy_plots(self.ptr.epoch_train, self.ptr.epoch_valid, self.ptr.epoch_test, path, &self.state)
        make_loss_plots(self.ptr.epoch_train, self.ptr.epoch_valid, self.ptr.epoch_test, path, &self.state)
        make_roc_plots(self.ptr.epoch_train, self.ptr.epoch_valid, self.ptr.epoch_test, path, &self.state)
        make_nodes(self.ptr.epoch_train, self.ptr.epoch_valid, self.ptr.epoch_test, path)



