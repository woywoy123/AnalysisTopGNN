from AnalysisTopGNN.Templates import Selection 

class Common(Selection):

    def __init__(self):
        Selection.__init__(self)

    def Selection(self, event):
        #< here we define what events are allowed to pass >
        #< Need to return True if the event passes our selection >
        # e.g. 
        lep = [ 11, 13, 15 ] # < Electrons, Muons, Taus (we can remove taus)
        return len([c for c in event.TopChildren if abs(c.pdgid) in lep ]) == 2

    def Strategy(self, event):
        #< here we can write out 'grouping' routine. >
        #< To Collect statistics on events, just return a string containing '->' >

        return "Success->SomeString"
