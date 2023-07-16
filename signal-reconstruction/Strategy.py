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
        self.BSMBDTs = {}
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
        mtt_reconstructor = MttReconstructor(event, 9, 'Jet')
        mass = mtt_reconstructor.mtt
        if event.ROOTName not in self.masses:
            self.masses[event.ROOTName] = []
            self.eventNumbers[event.ROOTName] = []
            self.runNumbers[event.ROOTName] = []
            self.mcChannelNumbers[event.ROOTName] = []
            self.BSMBDTs[event.ROOTName] = []
            # self.SMBDTs[event.ROOTName] = []
        self.masses[event.ROOTName].append(mass if mass >= 0 else 0)
        # self.masses[event.ROOTName].append(event.resonance_mass)
        self.eventNumbers[event.ROOTName].append(event.eventNumber)
        self.runNumbers[event.ROOTName].append(event.runNumber)
        self.mcChannelNumbers[event.ROOTName].append(event.mcChannelNumber)
        self.BSMBDTs[event.ROOTName].append(event.BSMBDT_1000)
        # self.SMBDTs[event.ROOTName].append(event.SMBDT)
        if mass <= 0:
            return "Failure->Mass not reconstructed"
        return "Success->SomeString"
