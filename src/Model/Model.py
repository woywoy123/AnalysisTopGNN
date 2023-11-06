from AnalysisG._cmodules.cWrapping import ModelWrapper
from AnalysisG.Notification import _ModelWrapper
from torch_geometric.data import Data
import torch

class Model(_ModelWrapper, ModelWrapper):
    def __init__(self, inpt = None):
        ModelWrapper.__init__(self, inpt)
        self.Caller = "MODEL"
        self.Verbose = 3

    def SampleCompatibility(self, smpl):
        if self._check_broken_model(): return False
        self.match_data_model_vars(smpl)
        if not self._iscompatible(smpl): return False
        return True
