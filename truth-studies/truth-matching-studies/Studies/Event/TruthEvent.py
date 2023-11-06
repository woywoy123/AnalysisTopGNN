from AnalysisG.Templates import SelectionTemplate

class EventNTruthJetAndJets(SelectionTemplate):

        def __init__(self):
                SelectionTemplate.__init__(self)
                self.TruthJets = []
                self.Jets = []
                self.MET = []
                self.nLep = []

        def Strategy(self, event):
                self.TruthJets.append(len(event.TruthJets))
                self.Jets.append( len(event.Jets))
                self.MET.append(event.met/1000)
                self.nLep.append(len([ i for i in event.TopChildren if i.is_lep ]))


class EventMETImbalance(SelectionTemplate):

        def __init__(self):
                SelectionTemplate.__init__(self)
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
                mass = particle.Mass
                e = particle.e
                px_, py_, pz_ = particle.px, particle.py, particle.pz
                pz = pz_*math.cos(angle) + py_*math.sin(angle)
                py = -pz_*math.sin(angle) + py_*math.cos(angle)
                particle.py = py
                particle.pz = pz

        def Strategy(self, event):
                import math
                t4 = sum(event.Tops)
                imb_angle = math.atan2(t4.pt, t4.pz)
                self.PT_4Tops.append(t4.pt/1000)
                self.Pz_4Tops.append(t4.pz/1000)

                self.Top4_angle.append(imb_angle)
                self.Rotation(t4, -imb_angle)
                self.r_Top4_angle.append(math.atan2(t4.pt, t4.pz))

                c4 = sum(event.TopChildren)
                self.Children_angle.append(math.atan2(c4.pt, c4.pz))
                self.Rotation(c4, -imb_angle)
                self.r_Children_angle.append(math.atan2(c4.pt, c4.pz))

                # Missing MET 
                nuPT = sum([i for i in event.TopChildren if abs(i.pdgid) in [12, 14, 16]])
                self.NeutrinoET += [nuPT.pt/1000]
                self.MET += [event.met / 1000]
                self.METDelta += [nuPT.pt/1000 - event.met/1000]

                self.Rotation(nuPT, -imb_angle)
                self.r_NeutrinoET += [nuPT.pt/1000]
                self.r_METDelta += [nuPT.pt/1000 - event.met/1000]
