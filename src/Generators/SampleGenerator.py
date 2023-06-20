import random
import numpy as np
from sklearn.model_selection import ShuffleSplit, KFold
from torch.utils.data import SubsetRandomSampler
from AnalysisG.Notification import _RandomSamplers
from AnalysisG.Settings import Settings
from torch_geometric.loader import DataListLoader
from AnalysisG.Tracer import SampleTracer


class RandomSamplers(_RandomSamplers, Settings):
    def __init__(self):
        self.Caller = "RANDOMSAMPLER"
        Settings.__init__(self)

    def RandomizeEvents(self, Events, nEvents):
        if isinstance(Events, dict):
            Indx = list(Events.values())
        else:
            Indx = Events
        random.shuffle(Indx)
        if len(Events) >= nEvents:
            return Indx[0:nEvents]
        self.NotEnoughEvents(Events, nEvents)
        return {i.hash: i for i in Indx}

    def MakeTrainingSample(self, Sample, TrainingSize=50):
        if isinstance(Sample, dict) == False:
            return self.ExpectedDictionarySample(type(Sample))
        All = np.array(list(Sample))
        self.RandomizingSamples(len(All), TrainingSize)
        rs = ShuffleSplit(
            n_splits=1, test_size=float((100 - TrainingSize) / 100), random_state=42
        )
        for train_idx, test_idx in rs.split(All):
            pass
        for i in All[train_idx]:
            Sample[i].TrainMode = "train"
        for i in All[test_idx]:
            Sample[i].TrainMode = "test"

        self.RandomizingSize(len(train_idx), len(test_idx))

        return {
            "train_hashes": All[train_idx].tolist(),
            "test_hashes": All[test_idx].tolist(),
        }

    def MakekFolds(self, sample, folds, batch_size=1, shuffle=True, asHashes=False):
        if isinstance(sample, dict):
            try:
                smpl = [i.hash for i in list(sample.values()) if i.TrainMode != "test"]
            except AttributeError:
                return False
        elif isinstance(sample, list):
            return self.MakeFolds(
                {i.hash: i for i in sample}, folds, batch_size, shuffle
            )
        else:
            return False
        if len(sample) < folds:
            return False
        split = KFold(n_splits=folds, shuffle=shuffle)
        output = {
            "k-" + str(f + 1): {"train": None, "leave-out": None} for f in range(folds)
        }

        smpl = np.array(smpl)
        for f, (train_idx, test_idx) in enumerate(split.split(np.arange(len(smpl)))):
            train_idx, test_idx = smpl[train_idx].tolist(), smpl[test_idx].tolist()
            output["k-" + str(f + 1)]["train"] = (
                train_idx if asHashes else [sample[i] for i in train_idx]
            )
            output["k-" + str(f + 1)]["leave-out"] = (
                test_idx if asHashes else [sample[i] for i in test_idx]
            )
        return output

    def MakeDataLoader(self, sample, SortByNodes=False, batch_size=1):
        if isinstance(sample, dict):
            sample = list(sample.values())
        elif isinstance(sample, list):
            pass
        elif issubclass(type(sample), SampleTracer):
            pass
        else:
            return False

        output = {}
        for i in sample:
            key = "all" if not SortByNodes else i.num_nodes
            if key not in output:
                output[key] = []
            output[key] += [i.hash]
        return [
            j for i in output for j in DataListLoader(output[i], batch_size=batch_size)
        ]
