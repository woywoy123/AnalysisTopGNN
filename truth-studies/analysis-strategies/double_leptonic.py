from AnalysisG.Templates import SelectionTemplate

class DiLeptonic(SelectionTemplate):

    def __init__(self):
        SelectionTemplate.__init__(self)

        self.TopMasses = {
                "Lep-Had" : [],
                "Lep-Lep" : [],
                "Had-Had" : [],
                "All" : [],
        }
        self.ZPrime = {}
        self.PhaseSpaceZ = {}
        self.PhaseSpaceT = {}
        self.Kinematics = {}

        self.AllowFailure = False
        self.__params__ = {"btagger" : None, "truth" : None}

    def ParticleRouter(self, event):
        particles = []
        if self._truthmode == "children":
            particles += event.TopChildren

        elif self._truthmode == "jets+truthleptons":
            particles += event.Jets
            particles += [c for c in event.TopChildren if c.is_lep]

        elif self._truthmode == "detector":
            particles += event.DetectorObjects

        return particles

    def Selection(self, event):
        self._this_b = self.__params__["btagger"]
        self._truthmode = self.__params__["truth"]
        particles = self.ParticleRouter(event)
        leptons = []
        bquark = []
        for i in particles:
            if i.is_lep: leptons += [i]
            else: bquark += [i] if getattr(i, self._this_b) else []
        if len(leptons) != 2: return False
        if len(bquark) != 4: return False
        self.__bquarks = bquark
        self.__leptons = leptons
        return True

    def Highest_b(self):
        highb = { c.pt : c for c in self.__bquarks}
        highpt = sorted(highb, reverse = True)
        if len(highb) >= 2: highpt = highpt[:2]
        high_ptb = [highb[c] for c in highpt]
        return high_ptb

    def Strategy(self, event):
        part = self.ParticleRouter(event)

        # find the highest pT b-quarks or bjets
        highb = self.Highest_b()
        self.__bquarks = None
        self.__leptons = None

        # Remove these b's from the list particle candidates and other b quarks
        particles = []
        for i in part:
            if i in highb: continue
            elif i.is_lep: pass
            elif getattr(i, self._this_b): continue
            particles += [i]

        # Compute the DeltaR between b's
        delR_P = {p.DeltaR(c) : [p, c] for p in highb for c in particles}
        delR = sorted(delR_P)

        # Construct the seeds by selecting only the closest particle from the list 
        # and determining whether the closest was a lepton or quark
        candidates = {x : [x] for x in highb}
        for can in highb:
            it = iter(delR)
            this = None
            dR = None
            while True:
                try: dR = next(it)
                except StopIteration: break

                # check if the candidate is in the deltaR pairs
                if can not in delR_P[dR]: continue

                # Select this pair and make it public
                this = delR_P[dR]

                # Remove this pair from the dic
                delR_P = {r : delR_P[r] for r in delR_P if r != dR}
                delR   = [r for r in delR if r != dR]
                break

            if dR is None: break
            if this is None: continue
            candidates[can].append(this[-1])

        # Now check whether the closest particle is a lepton or quark type
        type_dic = {}
        for can in candidates:
            type_can = candidates[can][-1]
            if can is type_can: type_dic[can] = []
            if type_can.is_lep: type_dic[can] = [can, type_can]
            else:
                # find an additional quark or jet
                type_dic[can] = [can, type_can]
                for dr in delR_P:
                    this = delR_P[dr]
                    if can not in this: continue
                    if this[-1].is_lep: continue
                    type_dic[can].append(this[-1])
                    break
        # if the number of the number of b's is less than 2, reject the event
        if len(type_dic) < 2: return "NoPairs::Rejected"
        if sum([len(val) == 0 for can, val in type_dic.items()]) == 1: return "NoPairs::Rejected"

        # count the number of leptons in this candidate list
        n_lep = sum([sum([c.is_lep for c in type_dic[can]]) for can in type_dic])
        if n_lep == 0:
            t, t_ = list(type_dic.values())
            sel_type = "Had-Had"

        elif n_lep == 1:
            for can in type_dic:
                top_c = [c for c in type_dic[can]]
                if sum([c.is_lep for c in top_c]) == 0: continue
                lep = [c for c in top_c if c.is_lep][0]
                b = [c for c in top_c if not c.is_lep][0]

                nu = self.Nu(b, lep, event, gev = True)
                if len(nu) == 0: return "NoSingleNuSolution::Rejected"
                type_dic[can] += [nu[0]]
            t, t_ = list(type_dic.values())
            sel_type = "Lep-Had"

        elif n_lep == 2:
            dic = { "l" : [], "b" : []}
            for can in type_dic:
                lep = [c for c in type_dic[can] if c.is_lep][0]
                b = [c for c in type_dic[can] if not c.is_lep][0]
                dic["l"] += [lep]
                dic["b"] += [b]
            bs = dic["b"]
            ls = dic["l"]
            nus = self.NuNu(bs[0], bs[1], ls[0], ls[1], event, gev = True)
            if len(nus) == 0: return "NoDoubleNuSolution::Rejected"
            t, t_ = [[bs[i], ls[i], nus[0][i]] for i in range(2)]
            sel_type = "Lep-Lep"

        mode = []
        for can in type_dic:
            x = [int(c.charge) for c in type_dic[can] if int(c.charge)]
            if not len(x): continue
            if x[0] < 0: mode.append("-")
            else: mode.append("+")
        if not len(mode): mode = "NA"
        else: mode = "".join(mode)

        tops = [sum(t).Mass/1000, sum(t_).Mass/1000]
        self.TopMasses[sel_type] += tops
        self.TopMasses["All"] += tops

        njets = len(event.Jets)
        zp = sum(t+t_).Mass/1000
        short = event.meta.logicalDatasetName
        if "All" not in self.ZPrime: self.ZPrime["All"] = []
        if short not in self.ZPrime: self.ZPrime[short] = {}
        if sel_type not in self.ZPrime[short]: self.ZPrime[short][sel_type] = []

        if short not in self.PhaseSpaceZ:
            self.PhaseSpaceZ[short] = {}
            self.PhaseSpaceT[short] = {}
            self.Kinematics[short] = {}

        if njets not in self.PhaseSpaceZ:
            self.PhaseSpaceZ[short][njets] = {}
            self.PhaseSpaceT[short][njets] = {}
            self.Kinematics[short][njets] = {}

        if mode not in self.PhaseSpaceZ[short][njets]:
            self.PhaseSpaceZ[short][njets][mode] = []
            self.PhaseSpaceT[short][njets][mode] = []
            self.Kinematics[short][njets][mode] = {"pt" : [], "eta" : [], "phi": [], "e": []}

        self.PhaseSpaceT[short][njets][mode] += tops
        self.PhaseSpaceZ[short][njets][mode] += [zp]

        particles = sum([type_dic[k]for k in type_dic], [])
        self.Kinematics[short][njets][mode]["pt"]  += [i.pt for i in particles]
        self.Kinematics[short][njets][mode]["eta"] += [i.eta for i in particles]
        self.Kinematics[short][njets][mode]["phi"] += [i.phi for i in particles]
        self.Kinematics[short][njets][mode]["e"]   += [i.e for i in particles]


        self.ZPrime[short][sel_type] += [zp]
        self.ZPrime["All"] += [zp]
        return "FoundSolutions::Passed"

