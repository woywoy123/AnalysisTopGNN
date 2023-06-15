from AnalysisG.Templates import SelectionTemplate
from mtt_reconstruction import MttReconstructor
from Efficiency import Efficiency_weighted1,Efficiency_weighted2
from statistics import mean

class Common(SelectionTemplate):

    def __init__(self):
        SelectionTemplate.__init__(self)
        self.object_types = ['Children', 'TruthJet', 'Jet']
        self.cases = [i for i in range(10)]
        self.masses = {object_type : {case_num : [] for case_num in self.cases} for object_type in self.object_types}
        self.efficiencies = {object_type : {case_num : {method: [] for method in range(2)} for case_num in self.cases} for object_type in self.object_types}
        self.efficiency_avg = {object_type : {case_num : {method: [] for method in range(2)} for case_num in self.cases} for object_type in self.object_types}

    def Selection(self, event):
        #< here we define what events are allowed to pass >
        # Basic selection, should be true anyway
        num_lep = len([1 for child in event.TopChildren if child.is_lep])
        num_lep_res = len([1 for child in event.TopChildren if child.is_lep and child.Parent[0].FromRes])
        num_tops = len(event.Tops)
        num_tau = len([1 for child in event.TopChildren if abs(child.pdgid) == 15])
        num_gluon = len([1 for child in event.TopChildren if abs(child.pdgid) == 21])
        num_gamma = len([1 for child in event.TopChildren if abs(child.pdgid) == 22])
        return num_tops == 4 and num_lep == 2 and num_lep_res == 1# and num_tau == 0 and num_gluon == 0 and num_gamma == 0


    def Strategy(self, event):
        #< here we can write out 'grouping' routine. >
        #< To Collect statistics on events, just return a string containing '->' >
        for object_type in self.object_types:
            for case_num in self.cases:
                mtt_reconstructor = MttReconstructor(event, case_num, object_type)
                self.masses[object_type][case_num].append(mtt_reconstructor.mtt)
                # here is how you get the grouping:
                # grouping = mtt_reconstructor.grouping
                # it will return a list of lists
                # grouping[0] is a list of objects, matched to top #0
                grouping = mtt_reconstructor.grouping
                if not grouping: grouping = []
                for method in range(2):
                    self.efficiencies[object_type][case_num][method].append([Efficiency_weighted1(grouping[i], i, event) for i in range(len(grouping))] if method == 0 else [Efficiency_weighted2(grouping[i], i, event) for i in range(len(grouping))])
                    self.efficiency_avg[object_type][case_num][method].append(mean(self.efficiencies[object_type][case_num][method][-1]) if self.efficiencies[object_type][case_num][method][-1] else 0)

        return "Success->SomeString"
