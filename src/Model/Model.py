from AnalysisG.Notification import _ModelWrapper
from .LossFunctions import LossFunctions
from torch_geometric.data import Data
import torch

try:
    import PyC.Transform.Tensors as PT
    import PyC.Physics.Tensors.Cartesian as CT
except:
    pass


class ModelWrapper(_ModelWrapper):
    def __init__(self, model=None):
        self.Caller = "MODEL"
        self.Verbose = 3
        self.OutputDirectory = None
        self.RunName = None
        self.Epoch = None

        # Mass reconstruction part
        self.TruthMode = True if model is None else False
        self.Keys = {"pt": "N_pT", "eta": "N_eta", "phi": "N_phi", "e": "N_energy"}

        self._Model = model
        self._inputs = {}
        self._outputs = {}

        # Mappings
        self.o_mapping = {}
        self.i_mapping = {}

        self._truth = True
        self._train = True

        self._GetModelInputs
        self._build

    def __call__(self, data):
        self._Model(**{k: getattr(data, k) for k in self.i_mapping})

        dc = self._Model.__dict__
        pred = {"batch": data.batch, "edge_index": data.edge_index}
        if self._truth:
            pred.update({self.o_mapping[k]: dc[k] for k in self.o_mapping})
        else:
            pred.update({k: dc[k] for k in self._outputs})
        if not self._truth:
            return Data().from_dict(pred), None

        loss = {
            o[2:]: self._loss[o[2:]](pred[t], getattr(data, t))
            for o, t in zip(self.o_mapping, self.o_mapping.values())
        }
        self._l = loss
        self.Data = data
        self.Pred = Data().from_dict(pred)
        return self.Pred, loss

    def _scan(self, inpt, key):
        return {k: inpt[k] for k in inpt if k.startswith(key)}

    def _mapping(self, inpt, key):
        return {
            "O" + k[3:]: k
            for k in inpt
            if k.startswith(key) and "O" + k[3:] in self._outputs
        }

    @property
    def _inject_tools(self):
        self._Model.MassEdgeFeature = self.MassEdgeFeature
        self._Model.MassNodeFeature = self.MassNodeFeature

    @property
    def _GetModelInputs(self):
        if self.TruthMode:
            return
        code = self._Model.forward.__code__
        self._inputs = {
            key: None for key in code.co_varnames[: code.co_argcount] if key != "self"
        }
        return self._inputs

    @property
    def _build(self):
        if self.TruthMode:
            return
        self._outputs = self._scan(self._Model.__dict__, "O_")
        mod = self._Model.__dict__["_modules"]
        mod = {i: mod[i] for i in mod}
        mod.update(self._Model.__dict__)
        c = self._scan(self._Model.__dict__, "C_")
        loss = self._scan(mod, "L_")
        self._loss = {
            l[2:]: LossFunctions(
                loss[l], c["C_" + l[2:]] if "C_" + l[2:] in c else False
            )
            for l in loss
        }

    def SampleCompatibility(self, smpl):
        self._pth = self.OutputDirectory + "/" + self.RunName
        smpl = list(smpl.to_dict())
        self.i_mapping = {k: smpl[smpl.index(k)] for k in self._inputs if k in smpl}

        self.o_mapping = self._mapping(smpl, "E_T_")
        self.o_mapping.update(self._mapping(smpl, "N_T_"))
        self.o_mapping.update(self._mapping(smpl, "G_T_"))

        try:
            self._inject_tools
        except:
            pass

        if not self._iscompatible:
            return False
        return True

    @property
    def train(self):
        return self._train

    @train.setter
    def train(self, val):
        self._train = val
        if self._train:
            self._Model.train()
        else:
            self._Model.eval()

    @property
    def dump(self):
        out = {"epoch": self.Epoch, "model": self._Model.state_dict()}
        torch.save(out, self._pth + "/" + str(self.Epoch) + "/TorchSave.pth")

    @property
    def load(self):
        lib = torch.load(self._pth + "/" + str(self.Epoch) + "/TorchSave.pth")
        self._Model.load_state_dict(lib["model"])
        self._Model.eval()
        return self._pth + " @ " + str(self.Epoch)

    @property
    def backward(self):
        loss = sum([self._l[x]["loss"] for x in self._l])
        if self._train:
            loss.backward()
        return loss

    @property
    def device(self):
        return self._Model.device

    @device.setter
    def device(self, val):
        self._Model = self._Model.to(val)

    def _switch(self, sample, pred):
        shape = pred.size()
        if shape[1] > 1:
            pred = pred.max(1)[1]
        pred = pred.view(-1)
        if shape[0] == sample.edge_index.size()[1]:
            return self.MassEdgeFeature(sample, pred).tolist()
        elif shape[0] == sample.num_nodes:
            return self.MassNodeFeature(sample, pred).tolist()
        else:
            return []

    def _debatch(self, inpt, sample):
        btch = inpt.batch.unique()
        smples = [sample.subgraph(sample.batch == b) for b in btch]
        inpt = [inpt.subgraph(inpt.batch == b) for b in btch]
        return smples, inpt

    @property
    def mass(self):
        data = self.Data if self.TruthMode else self.Pred
        sample, pred = self._debatch(data, self.Data)
        return [
            {o[2:]: self._switch(j, i[self.o_mapping[o]]) for o in self.o_mapping}
            for i, j in zip(pred, sample)
        ]

    @property
    def __SummingNodes(self):
        try:
            Pmu = {i: self._data[self.Keys[i]] for i in self.Keys}
        except TypeError:
            Pmu = {i: getattr(self._data, self.Keys[i]) for i in self.Keys}
        Pmu = torch.cat(
            [PT.PxPyPz(Pmu["pt"], Pmu["eta"], Pmu["phi"]), Pmu["e"]], dim=-1
        )

        # Get the prediction of the sample and extract from the topology the number of unique classes
        edge_index = self._data.edge_index
        edge_index_r = edge_index[0][self._mask == True]
        edge_index_s = edge_index[1][self._mask == True]

        # Weird floating point inaccuracy. When using Unique, the values seem to change slightly
        Pmu = Pmu.to(dtype=torch.long)
        Pmu_n = torch.zeros(Pmu.shape, device=Pmu.device, dtype=torch.long)
        Pmu_n.index_add_(0, edge_index_r, Pmu[edge_index_s])

        # Make sure to find self loops - Avoid double counting
        excluded_self = edge_index[1] == edge_index[0]
        excluded_self[excluded_self] = False
        excluded_self[self._mask == True] = False
        Pmu_n[edge_index[0][excluded_self]] += Pmu[edge_index[1][excluded_self]]

        Pmu_n = (Pmu_n / 1000).to(dtype=torch.long)
        Pmu_n = torch.unique(Pmu_n, dim=0)

        Pmu_n = CT.Mass(Pmu_n).view(-1)
        return Pmu_n[Pmu_n > 0]

    def MassNodeFeature(self, Sample, pred, excl_zero=True):
        self._data = Sample
        if excl_zero:
            self._mask = (
                pred[self._data.edge_index[0]] * pred[self._data.edge_index[1]] > 0
            )
        else:
            self._mask = (
                pred[self._data.edge_index[0]] == pred[self._data.edge_index[1]]
            )
        return self.__SummingNodes

    def MassEdgeFeature(self, Sample, pred):
        self._data = Sample
        self._mask = pred == 1
        return self.__SummingNodes

    def ClosestParticle(self, tru, pred):
        res = []
        if len(tru) == 0:
            return res
        if len(pred) == 0:
            return pred
        p = pred.pop(0)
        max_tru, min_tru = max(tru), min(tru)
        col = True if p <= max_tru and p >= min_tru else False

        if col == False:
            if len(pred) == 0:
                return res
            return self.ClosestParticle(tru, pred)

        diff = [abs(p - t) for t in tru]
        tru.pop(diff.index(min(diff)))
        res += self.ClosestParticle(tru, pred)
        res.append(p)
        return res

    @property
    def ParticleEfficiency(self):
        tmp = self.TruthMode
        self.TruthMode = True
        t = self.mass

        self.TruthMode = False
        p = self.mass
        output = []
        for b in range(len(t)):
            out = {}
            for f in t[b]:
                pred, truth = p[b][f], t[b][f]
                pred = self.ClosestParticle(truth, pred)
                p_l, t_l = len(pred), len(truth)
                out[f] = {
                    "%": float(p_l / (t_l if t_l != 0 else 1)) * 100,
                    "nrec": p_l,
                    "ntru": t_l,
                }
            output.append(out)
        self.TruthMode = tmp
        return output
