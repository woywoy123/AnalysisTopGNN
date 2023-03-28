from AnalysisTopGNN.Templates import Selection

class EventNTruthJetAndJets(Selection):

        def __init__(self):
                Selection.__init__(self)
                self.TruthJets = []
                self.Jets = []
                self.MET = []
                self.nLep = []
                
        def Strategy(self, event):
                lep = [11, 13, 15]
                self.TruthJets.append(len(event.TruthJets))
                self.Jets.append( len(event.Jets))
                self.MET.append(event.met/1000)
                self.nLep.append(len([ i for i in event.TopChildren if abs(i.pdgid) in lep ]))


class EventMETImbalance(Selection):

        def __init__(self):
                Selection.__init__(self)
                self.PT_4Tops = []
                self.Pz_4Tops = []
                self.Top4_angle = []

                self.Children_angle = []

                self.r_Top4_angle = []
                self.r_Children_angle = []

                self.NeutrinoET = []
                self.MET = []
                self.METDelta = []

                self.r_NeutrinoET = []
                self.r_METDelta = []
 
        def Selection(self, event):
                return len(event.Tops) == 4

        def Rotation(self, particle, angle):
                import math
                pt_, pz_ = particle.pt, particle.pz
                pt = pt_*math.cos(-angle) + pz_*math.sin(-angle)
                pz = pz_*math.cos(-angle) - pt_*math.sin(-angle)
                particle.pt, particle.pz = pt, pz

        def RotationP(self, particle, angle):
                import math
                pt_, pz_ = particle.pt, particle.pz
                pt = pt_*math.cos(angle) + pz_*math.sin(angle)
                pz = pz_*math.cos(angle) - pt_*math.sin(angle)
                particle.pt, particle.pz = pt, pz

        def Strategy(self, event):
                import math
                t4 = sum(event.Tops)

                imb_angle = math.atan(t4.pt/t4.pz)

                self.PT_4Tops.append(t4.pt/1000)
                self.Pz_4Tops.append(t4.pz/1000)
                self.Top4_angle.append(imb_angle)

                c4 = sum(event.TopChildren)
                self.Children_angle.append(math.atan(c4.pt/c4.pz))
                
                self.Rotation(t4, imb_angle)
                self.r_Top4_angle.append(math.atan(t4.pt/t4.pz))
                
                self.Rotation(c4, imb_angle)
                self.r_Children_angle.append(math.atan(c4.pt/c4.pz))
                
                # Missing MET 
                nuPT = sum([i for i in event.TopChildren if abs(i.pdgid) in [12, 14, 16]])
                self.NeutrinoET += [nuPT.pt/1000] 
                self.MET += [event.met / 1000]
                self.METDelta += [nuPT.pt/1000 - event.met/1000]

                self.RotationP(nuPT, imb_angle)
                self.r_NeutrinoET += [nuPT.pt/1000] 
                self.r_METDelta += [nuPT.pt/1000 - event.met/1000]






