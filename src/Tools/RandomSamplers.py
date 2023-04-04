import random
import numpy as np
from sklearn.model_selection import ShuffleSplit, KFold
from torch.utils.data import SubsetRandomSampler
from AnalysisTopGNN.Notification import RandomSamplers_

try:
    from torch_geometric.loader import DataLoader
except:
    from torch_geometric.data import DataLoader

class RandomSamplers(RandomSamplers_):

    def __init__(self):
        pass
    
    def RandomEvents(self, Events, nEvents):
        Indx = []
        if isinstance(Events, dict):
            Indx += list(Events.values())
        else:
            Indx += Events
        
        random.shuffle(Indx)
        if len(Events) < nEvents:
            self.NotEnoughEvents(Events, nEvents)
            return Indx    
        return Indx[0:nEvents]

    def MakeTrainingSample(self, Sample, TrainingSize = 50):
        if isinstance(Sample, dict) == False:
            self.ExpectedDictionarySample(type(Sample))
            return 
        
        All = np.array(list(Sample))
        self.RandomizingSamples(len(All), TrainingSize)
        
        rs = ShuffleSplit(n_splits = 1, test_size = float((100 - TrainingSize)/100), random_state = 42)
        for train_idx, test_idx in rs.split(All):
            pass 
        return {"train_hashes" : All[train_idx], "test_hashes" : All[test_idx]}

    def MakekFolds(self, sample, folds, batch_size = 1, shuffle = True):
        smpl = len(sample)
        if len(sample) < folds:
            return 

        split = KFold(n_splits = folds, shuffle=shuffle)
        output = {}
        for fold, (train_idx, test_idx) in enumerate(split.split(np.arange(len(sample)))):
            output[fold] = []
            output[fold] += [DataLoader(sample, batch_size=batch_size, sampler = SubsetRandomSampler(train_idx))]
            output[fold] += [DataLoader(sample, batch_size=batch_size, sampler = SubsetRandomSampler(test_idx))]
        return output

    def MakeSample(self, sample, SortByNodes = False, batch_size = 1):
        out = {}
        prcout = {}
        if SortByNodes:
            for hash_ in sample:
                i = sample[hash_]
                num_nodes = i.num_nodes.item()
                if num_nodes not in out:
                    out[num_nodes] = []
                    prcout[num_nodes] = []
                prcout[num_nodes].append(hash_)
                out[num_nodes].append(i)
        else:
            out["All"] = list(sample.values())
            prcout["All"] = list(sample)
        
        output = []
        output_prc = []
        for i in out:
            output += [d for d in DataLoader(out[i], batch_size=batch_size)]
            output_prc += [d for d in DataLoader(prcout[i], batch_size=batch_size)]
        return output, output_prc
