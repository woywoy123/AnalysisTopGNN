from AnalysisTopGNN import Analysis 
from AnalysisTopGNN.Events import Event 
from AnalysisTopGNN.Templates import Selection

class MakeTruth(Selection):

    def __init__(self):
        AnalysisTemplate.__init__(self)

        self.Truth = {
                       "Lep" : {"Top" : [], "Children" : []}, 
                       "Had" : {"Top" : [], "Children" : []}, 
                    "HadHad" : {"Top" : [], "Children" : []}, 
                    "LepLep" : {"Top" : [], "Children" : []}, 
                    "HadLep" : {"Top" : [], "Children" : []}, 
                    "LepHad" : {"Top" : [], "Children" : []}, 
        }

    def Selection(self, event):

        # Construct All the Truth
        # -> Tops 
        tops = [k for k in event.Tops if len(k.Children) > 0]
        l  = [t for t in tops if t.LeptonicDecay]
        l_ = [t for t in tops if t.LeptonicDecay and t.FromRes == 1]
        
        h  = [t for t in tops if not t.LeptonicDecay]
        h_ = [t for t in tops if not t.LeptonicDecay and t.FromRes == 1]

        if len(sum(h_ + l_).Children) == 0:
            return "Failed->NoResonanceChildren"
        
        self.Truth["Lep"]["Top"] += [x.Mass for x in l]
        self.Truth["Had"]["Top"] += [x.Mass for x in h]
        self.Truth["Had"*len(h_) + "Lep"*len(l_)]["Top"] += [sum(h_ + l_).Mass]
        
        # -> Children 
        self.Truth["Lep"]["Children"] += [ sum(x.Children).Mass for x in l ]
        self.Truth["Had"]["Children"] += [ sum(x.Children).Mass for x in h ]
        self.Truth["Had"*len(h_) + "Lep"*len(l_)]["Children"] += [sum([i for k in h_ + l_ for i in k.Children]).Mass]

class ChildrenSelection(Selection):

    def __init__(self):
        AnalysisTemplate.__init__(self)
        self.Reconstruction = {
               "Lep" : {"Children" : []}, 
               "Had" : {"Children" : []}, 
            "HadHad" : {"Children" : []}, 
            "LepLep" : {"Children" : []}, 
            "HadLep" : {"Children" : []}, 
            "LepHad" : {"Children" : []}, 
        }
        
        self.lepNum = [11, 13, 15]
        self.nuNumber = [12, 14, 16]
        self.Excl = self.lepNum + self.nuNumber

    def Selection(self, event):
        # Selection 1: on the Children: 
        # - Select the two most energetic children, provided they are quarks.
        # - Assign either leptons or other children to these two based on the lowest deltaR. 
        #   -> If quarks are lowest deltaR: Use two additional quark children 
        #   -> If lepton is matched: Use single/double neutrino reconstruction code.
        # - Derive the Top and the resonance mass
        children = event.TopChildren 
        
        # ---- Get two highest PT quark children ----- # 
        ch = self.Sort({ c.pt/1000 : c for c in children if abs(c.pdgid) not in self.Excl }, True)
        ch = list(ch.values())[:2]
        
        # ----- Remove the two selected children and neutrinos ----- #
        resid_c = [ c for c in children if c not in ch and abs(c.pdgid) not in self.nuNumber ]
        dr = self.Sort({ k.DeltaR(p) : [k, p] for k in resid_c for p in ch})
        
        tmp = []
        cp1, cp2 = [], []
        tl1, tl2 = False, False
        for c in dr:
            p = dr[c][0]
            p_ = dr[c][1]
            
            if p in tmp:
                continue 
            tmp.append(p)
            
            lp = abs(p.pdgid) in self.Excl
            if p_ == ch[0]:
                tl1 = True if lp and len(cp1) == 0 else tl1 
                cp1 += [p] if tl1 and len(cp1) == 0 else []
                cp1 += [p] if not tl1 and len(cp1) < 2 and not lp else []
            if p_ == ch[1]:
                tl2 = True if lp and len(cp2) == 0 else tl2 
                cp2 += [p] if tl2 and len(cp2) == 0 else []
                cp2 += [p] if not tl2 and len(cp2) < 2 and not lp else []
        
        cp1 += [ch[0]]
        cp2 += [ch[1]]
        
        # ------ double Neutrino ----- #
        tl1 = cp1[0].pdgid in self.lepNum
        tl2 = cp2[0].pdgid in self.lepNum
        if len(cp1) == 2 and len(cp2) == 2 and tl1 and tl2:
            o = self.NuNu(cp1[1], cp2[1], cp1[0], cp2[0], event)
            if len(o) == 0:
                return "Failed->NoNuNu"
            m1 = { sum(cp1 + [x[0]]).Mass : cp1 + [x[0]] for x in o }
            m2 = { sum(cp2 + [x[1]]).Mass : cp2 + [x[1]] for x in o }
            o = list(self.Sort({ abs(x1 - x2) : [m1[x1], m2[x2]] for x1, x2 in zip(m1, m2) }).values())[0]
            self.Reconstruction["Lep"]["Children"] += [sum(i).Mass for i in o]
            self.Reconstruction["LepLep"]["Children"] += [sum([i for t in o for i in t]).Mass]
            return "Success->NuNu"
            
        # ------ Single Neutrino ----- #
        if len(cp1) == 2 and tl1:
            o = self.Nu(cp1[1], cp1[0], event)
            if len(o) == 0:
                return "Failed->NoNu"
            t1 = sum(o + cp1)
            t2 = sum(cp2)
            self.Reconstruction["Lep"]["Children"] += [t1.Mass]
            self.Reconstruction["Had"]["Children"] += [t2.Mass]
            self.Reconstruction["LepHad"]["Children"] += [(t1+t2).Mass]
            return "Success->Nu"
            
        # ------ Single Neutrino ----- #
        if len(cp2) == 2 and tl2:
            o = self.Nu(cp2[1], cp2[0], event)
            if len(o) == 0:
                return "Failed->NoNu"
            t2 = sum(o + cp2)
            t1 = sum(cp1)
            self.Reconstruction["Lep"]["Children"] += [t2.Mass]
            self.Reconstruction["Had"]["Children"] += [t1.Mass]
            self.Reconstruction["HadLep"]["Children"] += [(t1+t2).Mass]
            return "Success->Nu"
                
        # ------ All Hadronic ----- #
        t1 = sum(cp1)
        t2 = sum(cp2)
        self.Reconstruction["Had"]["Children"] += [t2.Mass]
        self.Reconstruction["Had"]["Children"] += [t1.Mass]
        self.Reconstruction["HadHad"]["Children"] += [(t1+t2).Mass]
        return "Success->Hadron"
 

#Ana = Analysis()
#Ana.Event = Event
#Ana.EventCache = True 
#Ana.DumpPickle = True 
#Ana.InputSample("bsm-1000", "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root")
#Ana.chnk = 1000
#Ana.Launch()
#
#x = MakeTruth()
#x(Ana)
#
#y = ChildrenSelection()
#y(Ana)
#print(y._CutFlow)

