from AnalysisG.Templates import SelectionTemplate
from mtt_reconstruction import MttReconstructor
from Efficiency import Efficiency_weighted1,Efficiency_weighted2
from statistics import mean
import copy

class Common(SelectionTemplate):

    def __init__(self):
        SelectionTemplate.__init__(self)
        self.masses = {}
        self.eventNumbers = {}
        self.runNumbers = {}
        self.mcChannelNumbers = {}
        self.BDTs = {}
        

    def Selection(self, event):
        #< here we define what events are allowed to pass >
        # Basic selection, should be true anyway
        n_bjet = len([jet for jet in event.Jets if jet.is_b])
        n_lep = len(event.Electrons) + len(event.Muons)
        return n_lep == 2 and n_bjet == 4

    def Strategy(self, event):
        #< here we can write out 'grouping' routine. >
        #< To Collect statistics on events, just return a string containing '->' >
        mtt_reconstructor = MttReconstructor(event, 9, 'Jet')
        if not mtt_reconstructor.mtt:
            return "Failure->Mass not reconstructed"
        if event.ROOTName not in self.masses:
            self.masses[event.ROOTName] = []
            self.eventNumbers[event.ROOTName] = []
            self.runNumbers[event.ROOTName] = []
            self.mcChannelNumbers[event.ROOTName] = []
            self.BDTs[event.ROOTName] = []
        self.masses[event.ROOTName].append(mtt_reconstructor.mtt)
        self.eventNumbers[event.ROOTName].append(event.eventNumber)
        self.runNumbers[event.ROOTName].append(event.runNumber)
        self.mcChannelNumbers[event.ROOTName].append(event.mcChannelNumber)
        self.BDTs[event.ROOTName].append(event.BSMBDT_1000)
        return "Success->SomeString"
