from AnalysisTopGNN.Templates import Selection
from mtt_reconstruction import MttReconstructor

class Common(Selection):

    def __init__(self):
        Selection.__init__(self)
        self.object_types = ['Children', 'TruthJet', 'Jet']
        self.cases = [i for i in range(10)]
        self.masses = {object_type : {case_num : [] for case_num in self.cases} for object_type in self.object_types}

    def Selection(self, event):
        #< here we define what events are allowed to pass >
        # Basic selection, should be true anyway
        num_lep = len([1 for child in event.TopChildren if child.is_lep])
        num_lep_res = len([1 for child in event.TopChildren if child.is_lep and child.Parent[0].FromRes])
        num_tops = len(event.Tops)
        num_tau = len([1 for child in event.TopChildren if abs(child.pdgid) == 15])
        num_gluon = len([1 for child in event.TopChildren if abs(child.pdgid) == 21])
        num_gamma = len([1 for child in event.TopChildren if abs(child.pdgid) == 22])
        return num_tops == 4 and num_lep == 2 and num_lep_res == 1 and num_tau == 0 and num_gluon == 0 and num_gamma == 0


    def Strategy(self, event):
        #< here we can write out 'grouping' routine. >
        #< To Collect statistics on events, just return a string containing '->' >
        for object_type in self.object_types:
            for case_num in self.cases:
                mass = MttReconstructor(event, case_num, object_type).mtt
                self.masses[object_type][case_num].append(mass)
        return "Success->SomeString"
