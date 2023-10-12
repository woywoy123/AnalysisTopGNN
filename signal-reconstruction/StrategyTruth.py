from AnalysisG.Templates import SelectionTemplate
from mtt_reconstruction import MttReconstructor
from Efficiency import Efficiency_weighted1,Efficiency_weighted2
from statistics import mean
import copy

class Common(SelectionTemplate):

    def __init__(self):
        SelectionTemplate.__init__(self)
        self.masses = {}
        self.event_types = {}
        # self.eventNumbers = {}
        # self.runNumbers = {}
        # self.mcChannelNumbers = {}
        # self.BSMBDTs = {}
        # self.SMBDTs = {}
        

    def Selection(self, event):
        return True
        #< here we define what events are allowed to pass >
        # Basic selection, should be true anyway
        n_bjet = len([jet for jet in event.Jets if jet.is_b])
        n_lep = len(event.Electrons) + len(event.Muons)
        return True

    def Strategy(self, event):
        #< here we can write out 'grouping' routine. >
        #< To Collect statistics on events, just return a string containing '->' >
        for object_type in ['Children', 'TruthJet', 'Jet']:
            if object_type not in self.masses:
                self.masses[object_type] = {}
                self.event_types[object_type] = {}
            # cases = [7, 8, 9] if object_type == 'Jet' else range(10)
            cases = [9]
            for case_num in cases:
                if case_num not in self.masses[object_type]:
                    self.masses[object_type][case_num] = []
                    self.event_types[object_type][case_num] = []
                mtt_reconstructor = MttReconstructor(event, case_num, object_type)
                mass = mtt_reconstructor.mtt
                self.masses[object_type][case_num].append(mass)
                self.event_types[object_type][case_num].append(mtt_reconstructor.event_type)
        return "Success->SomeString"
