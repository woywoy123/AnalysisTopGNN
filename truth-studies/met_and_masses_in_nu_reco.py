from AnalysisG.Templates import SelectionTemplate
import pyc
from AnalysisG.Events.Events.Event import Event 


class Selection(SelectionTemplate):
    def __init__(self):
        SelectionTemplate.__init__(self)
        self.nsolutions = {'met_nu+mass_obj' : {i : 0 for i in range(5)},
                           'met_nu+mass_real' : {i : 0 for i in range(5)},
                           'met_reco+mass_obj' : {i : 0 for i in range(5)},
                           'met_reco+mass_real': {i : 0 for i in range(5)}}

    def Selection(self, event):
        leptons = [child for child in event.TopChildren if child.is_lep]
        if len(leptons) != 2:
            return False
        return True
    
    def Strategy(self, event):
        leptons = [child for child in event.TopChildren if child.is_lep]
        l1, l2 = leptons 
        t1 = l1.Parent[0]
        t2 = l2.Parent[0]
        b1 = [child for child in t1.Children if child.is_b][0]
        b2 = [child for child in t2.Children if child.is_b][0]
        nu1 = [child for child in t1.Children if child.is_nu][0]
        nu2 = [child for child in t2.Children if child.is_nu][0]

        mT = 172.5 #GeV
        mW = 80.379 #GeV
        mT1 = (b1 + l1 + nu1).Mass
        mT2 = (b2 + l2 + nu2).Mass
        mW1 = (l1 + nu1).Mass
        mW2 = (l2 + nu2).Mass
        fake_event = Event()
        fake_event.met = (nu1 + nu2).pt
        fake_event.met_phi = (nu1 + nu2).phi
        result = self.NuNu(b1, b2, l1, l2, fake_event, mT=(mT1 + mT2)/2, mW=(mW1 + mW2)/2)
        self.nsolutions['met_nu+mass_obj'][len(result)] += 1
        result = self.NuNu(b1, b2, l1, l2, event, mT=(mT1 + mT2)/2, mW=(mW1 + mW2)/2)
        self.nsolutions['met_reco+mass_obj'][len(result)] += 1
        result = self.NuNu(b1, b2, l1, l2, event, mT=mT*1000, mW=mW*1000)
        self.nsolutions['met_reco+mass_real'][len(result)] += 1
        result = self.NuNu(b1, b2, l1, l2, fake_event, mT=mT*1000, mW=mW*1000)
        self.nsolutions['met_nu+mass_real'][len(result)] += 1