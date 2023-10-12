import itertools
import sys
# sys.path.append('/nfs/dust/atlas/user/sitnikov/AnalysisTopGNN/models/NeutrinoReconstructionOriginal/')
# from neutrino_momentum_reconstruction import doubleNeutrinoSolutions
import vector as v
from AnalysisG.Particles.Particles import Top, Children, TruthJet, Jet, Neutrino
import numpy as np
import torch
from nu_reco import getNeutrinoSolutions

t_mass = 172.76
w_mass = 80.379

class EventChecker:
    def __init__(self, event, obj_type='Children', sample_type='BSM'):
        self.obj_type = obj_type
        self.event = event
        objs = event.TopChildren if obj_type == 'Children' else event.TruthJets if obj_type == 'TruthJets' else event.Jets
        self.num_b = len([1 for obj in objs if obj.is_b])
        self.num_lep = len([1 for child in event.TopChildren if child.is_lep])
        self.num_lep_res = len([1 for child in event.TopChildren if child.is_lep and child.Parent[0].FromRes])
        self.num_tops = len(event.Tops)
        self.num_merged_jets = 0 if obj_type == 'Children' else len([1 for obj in objs if len(obj.Tops) > 1])
        self.num_tau = len([1 for child in event.TopChildren if abs(child.pdgid) == 15])
        self.num_gluon = len([1 for child in event.TopChildren if abs(child.pdgid) == 21])
        self.num_gamma = len([1 for child in event.TopChildren if abs(child.pdgid) == 22])
        if sample_type == 'BSM':
            self.is_ok = self.num_tops == 4 and self.num_lep == 2 and self.num_lep_res == 1 and self.num_merged_jets == 0 and self.num_tau == 0 and self.num_gamma == 0 and self.num_gluon == 0
        else:
            self.is_ok = self.num_tops == 4 and self.num_lep == 2 and self.num_merged_jets == 0 and self.num_tau == 0 and self.num_gamma == 0 and self.num_gluon == 0

def Combinatorial(n, k, msk, t = None, v = None, num = 0):
    if t == None:
        t = []
    if v == None:
        v = []
    if n == 0:
        t += [torch.tensor(num).unsqueeze(-1).bitwise_and(msk).ne(0).to(dtype = int).tolist()]
        v += [num]
        return t, v

    if n-1 >= k:
        t, v = Combinatorial(n-1, k, msk, t, v, num)
    if k > 0:
        t, v = Combinatorial(n-1, k -1, msk, t, v, num | ( 1 << (n-1)))

    return t, v

class MatchingBase:
    def __init__(self, lst=None, tops=None, allow_assignment_to_one_top=True, override_tops=None):
        self.tops = tops if tops is not None else [i for i in range(len(lst))] if lst is not None else [i for i in range(4)]
        self.allow_assignment_to_one_top = allow_assignment_to_one_top
        self.override_tops = override_tops if override_tops is not None else {itop : itop for itop in range(-1, 5)}
        self.is_jet = False

    def __getitem__(self, key):
        return {self.override_tops[itop] : [self.lst[i] for i, j in enumerate(self.assignments[key]) if j == itop] for itop in set(self.assignments[key])}

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        if len(self.assignments) <= self.idx:
            raise StopIteration
        self.idx += 1
        return self[self.idx - 1]

    def _get_truth_assignment(self):
        self.assignments = [[obj.TopIndex[0] if self.is_jet else obj.TopIndex for obj in self.lst]]
        self.tops = list(set(self.assignments[0]))

    def __len__(self):
        return len(self.assignments)

class BMatching(MatchingBase):
    is_jet = True 
    def __init__(self, lst):
        super().__init__(lst=lst, tops=[i for i in range(len(lst))], allow_assignment_to_one_top=False)
        self.lst = lst
        self.assignments = [[i for i in range(len(lst))]]


class Matching(MatchingBase):
    is_jet = False
    def __init__(self, lst, is_truth=True, tops=[i for i in range(4)], allow_assignment_to_one_top=True, override_tops=None, compare_to_w=False):
        super().__init__(lst=lst, tops=tops, allow_assignment_to_one_top=allow_assignment_to_one_top, override_tops=override_tops)
        self.lst = lst
        self.compare_to_w = compare_to_w
        if len(self.lst) != 0 and (type(self.lst[0]) == type(TruthJet()) or type(self.lst[0]) == type(Jet())):
            self.is_jet = True
        self.is_truth = is_truth
        if self.is_truth:
            self._get_truth_assignment()
        elif len(self.tops) > 2 and not self.allow_assignment_to_one_top:
            self._get_comb_assignment_template_manytops()
        else:
            if len(self.tops) > 2 and self.allow_assignment_to_one_top:
                print('Warning, assigning objects to more than 2 tops, when assignment of several objects to one top is allowed, is not implemented')
            self._get_comb_assignment_template()
            self.update_tops(self.tops)

    def _get_comb_assignment_template_manytops(self):
        import itertools 
        self.assignments = [list(perm) for perm in itertools.permutations(self.tops, len(self.lst))]

    def _get_comb_assignment_template(self):
        n = len(self.lst)
        msk = torch.pow(2, torch.arange(n))
        self.assignments_template = []
        for i in range(n + 1):
            self.assignments_template += Combinatorial(n, i, msk)[0]
        assert 2**n == len(self.assignments_template)
        if self.compare_to_w:
            at_new = {}
            for template in self.assignments_template:
                tops = [[self.lst[i] for i, j in enumerate(template) if j == itop] for itop in [0, 1]]
                mean_diff = np.mean([abs((sum(top).Mass if len(top) != 0 else 0) - w_mass) for top in tops])
                if mean_diff not in at_new:
                    at_new[mean_diff] = []
                at_new[mean_diff].append(template)
            small_keys = sorted(list(at_new.keys()))
            self.assignments_template = []
            for key in small_keys:
                self.assignments_template += at_new[key]
                if len(self.assignments_template) > 5:
                    break

    def update_tops(self, new_tops):
        if self.is_truth:
            return
        # print('tops before changing', self.tops)
        self.tops = new_tops
        # print('tops after changing', self.tops)
        self.assignments = []
        for i in self.tops:
            for j in self.tops:
                if i == j:
                    continue
                tops = [i, j]
                self.assignments += [[tops[k] for k in template] for template in self.assignments_template if self.allow_assignment_to_one_top or len(set(template)) == 2]

class NuMatching(MatchingBase):
    def __init__(self, bs=None, leps=None, nus=None, matching_type='truth', tops=None, event=None, allow_assignment_to_one_top=True, override_tops=None):
        super().__init__(tops=tops, allow_assignment_to_one_top=allow_assignment_to_one_top, override_tops=override_tops)
        self.matching_type = matching_type
        sorted_tops = sorted(list(leps.keys()), key=lambda x: leps.get(x)[0].pt, reverse=True)
        self.tops = [i for i in sorted_tops if i in leps and i in bs][:2]

        self.bs = sum([bs[i] for i in bs if i in self.tops], start=[])
        self.leps = sum([leps[i] for i in leps if i in self.tops], start=[])
        self.nus = sum(nus, start=[]) if nus else None
        if matching_type == 'truth':
            self.lst = self.nus
            self._get_truth_assignment()
        else:
            if None in self.bs or None in self.leps or len(self.bs) != 2 or len(self.leps) != 2:
                self.assignments = []
            else:
                met = sum(self.nus).pt
                met_phi = sum(self.nus).phi
                print(met, event.met, met_phi, event.met_phi)
                nus_result = None
                nus_result = getNeutrinoSolutions(self.bs[0], self.bs[1], self.leps[0], self.leps[1], met, met_phi)
                print(nus_result)
                # for nu1, nu2 in nus_result:
                    # print('\n', nu1.px, nu1.py, nu1.pz, nu1.e)
                    # print(nu2.px, nu2.py, nu2.pz, nu2.e)
                if nus_result is None or len(nus_result) == 0:
                    self.assignments = []
                else:
                    self.lst = self._match(nus_result)
                    if self.lst is None:
                        self.assignments = []
                    else:
                        self.assignments = [self.tops]

    # @staticmethod
    # def _convert_to_particles(nu_sol):
    #     def _convert_to_particle(threevec):
    #         vec = v.obj(x=threevec[0], y=threevec[1], z=threevec[2], m=0)
    #         result = Children()
    #         result.pt = vec.rho*1000
    #         result.eta = vec.eta
    #         result.phi = vec.phi
    #         result.e = vec.t*1000
    #         result.pdgid = 12
    #         return result
    #     result = []
    #     for sol_pair in nu_sol:
    #         result.append([_convert_to_particle(sol_pair[i]) for i in range(2)])
    #     return result

    # @staticmethod
    # def _convert_to_vector(particle):
    #     return v.obj(pt=particle.pt/1000, eta=particle.eta, phi=particle.phi, e=particle.e/1000)

    def _match(self, nus_result):
        key = None
        result = None
        loss_calc = LossCalculator()
        for res in nus_result:
            if self.matching_type == 'reco_truth':
                if len(self.nus) < 2:
                    return None
                new_key = sum([loss_calc.get_dR(res[i], self.nus[i]) for i in range(2)])
            else:
                new_key = sum([loss_calc.get_loss(b=self.bs[i], w=[self.leps[i], res[i]]) for i in range(2)])
            if key == None or new_key < key:
                key = new_key
                result = res
        return result

class Filter:
    def __init__(self, lst, pt_cut=None, eta_cut=None):
        self.lst = lst
        self.pt_cut = pt_cut
        self.eta_cut = eta_cut
        self.data_type = 'Unknown'
        if len(self.lst) != 0:
            if isinstance(self.lst[0], Children):
                self.data_type = 'Children'
            elif isinstance(self.lst[0], TruthJet):
                self.data_type = 'TruthJet'
            elif isinstance(self.lst[0], Jet):
                self.data_type = 'Jet'

        self.obj = {'b' : None,
                    'add' : None,
                    'lep' : None,
                    'nu' : None}

    def is_type(self, obj, type):
        if type == 'b':
            return obj.is_b
        elif type == 'add':
            return obj.is_add
        elif type == 'lep':
            return obj.is_lep
        elif type == 'nu':
            return obj.is_nu
        return False

    def get_obj(self, obj_type, pt_cut=None, eta_cut=None):
        if pt_cut is None:
            pt_cut = self.pt_cut
        if eta_cut is None:
            eta_cut = self.eta_cut
        if self.obj[obj_type] is None or (pt_cut is not None and pt_cut != self.pt_cut) or (eta_cut is not None and eta_cut != self.eta_cut):
            self.pt_cut = pt_cut
            self.eta_cut = eta_cut
            self.obj[obj_type] = [obj for obj in self.lst if self.is_type(obj, obj_type) and (obj.pt > self.pt_cut if self.pt_cut != None else True) and (abs(obj.eta) <= self.eta_cut if self.eta_cut != None else True)]
        return self.obj[obj_type]


    def get_b(self, pt_cut=None, limit_b_number=None):
        result = self.get_obj('b', pt_cut)
        result = sorted(result, key=lambda x: x.pt, reverse=True)[:limit_b_number]
        return result

    def get_add(self, pt_cut=None, limit_b_number=None):
        bs = self.get_obj('b', pt_cut)
        bs = sorted(bs, key=lambda x: x.pt, reverse=True)[limit_b_number:]
        result = self.get_obj('add', pt_cut) + bs
        return sorted(result, reverse=True, key=lambda elem: elem.pt)[:11]

    def get_lep(self, pt_cut=None):
        return self.get_obj('lep', pt_cut)

    def get_nu(self, pt_cut=None):
        return self.get_obj('nu', pt_cut)

class TruthJetMatcher:
    def __init__(self, truthjets, jets):
        self.truthjets = truthjets
        matches = set()
        for jet in jets:
            d = {j : jet.DeltaR(truthjets[j]) for j in range(len(truthjets))}
            matches.add(sorted(d, key=d.get)[0])
        # print(matches, len(truthjets), len(jets), len(matches))
        self.truthjets = [truthjets[i] for i in matches]
        # print('selected', self.truthjets, 'truthjets')

class LossCalculator:
    def __init__(self, alpha=1, beta=1, gamma=1):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    @staticmethod
    def get_diff(v1, v2):
        return ((v1.x - v2.x)**2 + (v1.y - v2.y)**2 + (v1.z - v2.z)**2)**0.5

    @staticmethod
    def get_dR(v1, v2):
        return((v1.eta - v2.eta)**2 + (v1.phi - v2.phi)**2)**0.5

    def get_loss(self, b, w):
        dR_ww = []
        dR_wb = []
        for i in range(len(w)):
            if b:
                dR_wb.append(self.get_dR(b, w[i]))
            for j in range(len(w)):
                if i == j:
                    continue
                dR_ww.append(self.get_dR(w[i], w[j]))
        w_mass_reco = sum(w).Mass if len(w) != 0 else 0
        if b == None:
            if len(w) == 0:
                t_mass_reco = 0
            else:
                t_mass_reco = w_mass_reco
        else:
            t_mass_reco = sum(w + [b]).Mass
        dR = dR_ww + dR_wb
        mean_dR = np.mean(dR) if len(dR) != 0 else 0
        return  self.alpha*mean_dR + \
        self.beta*1e-2*abs(w_mass_reco - w_mass) + \
        self.gamma*1e-2*abs(t_mass_reco - t_mass)


class MttReconstructor:
    def __init__(self, event, case_num, data_type, jet_pt_cut=None, jet_eta_cut=None):
        self.case_num = case_num
        self.event = event
        self.data_type = data_type
        children = Filter(event.Electrons + event.Muons) if data_type == 'Jet' else Filter(event.TopChildren) 
        self.nu = children.get_nu()
        self.lep = children.get_lep()
        tj = TruthJetMatcher(event.TruthJets, event.Jets).truthjets if data_type == 'TruthJet' else []
        jets = Filter(event.TopChildren if data_type == 'Children' else tj if data_type == 'TruthJet' else event.Jets, pt_cut=jet_pt_cut, eta_cut=jet_eta_cut)
        self.b = jets.get_b(limit_b_number=4)
        self.add = jets.get_add(limit_b_number=4)
        self.loss_calc = LossCalculator()
        self.compare_add_to_w = False if self.data_type =='Children' else True
        self._mtt = -1
        self._grouping = -1
        self.event_type = f'{len(self.lep)}lep{len(self.nu)}nu{len(self.b)}b{len(self.add)}add'

    def _select_resonance_truth(self):
        result = []
        for itop, top in enumerate(self.tops):
            if len(top) != 0 and top[0].FromRes:
                result += top
        return result

    def _select_resonance_pt(self):
        pts_lep = {i : sum(top).pt if i in self.lep_for_nu_reco and len(top) != 0 else 0 for i, top in enumerate(self.tops)}
        pts_had = {i : sum(top).pt if i not in self.lep_for_nu_reco and len(top) != 0 else 0 for i, top in enumerate(self.tops)}
        return self.tops[max(pts_lep, key=pts_lep.get)] + self.tops[max(pts_had, key=pts_had.get)]

    def select_resonance(self):
        if self.case_num == 0:
            self.res_products = self._select_resonance_truth()
        else:
            self.res_products = self._select_resonance_pt()

    def combine_tops(self):
        self.tops = [[] for i in range(4)]
        for objs in [self.bs, self.leps, self.nus, self.adds]:
            for i in objs:
                if i != -1:
                    self.tops[i] += objs[i]

    def calculate_loss(self):
        loss = 0
        for i in range(4):
            if i in self.bs:
                b = self.bs[i][0]
            else:
                b = None
            w = []
            if i in self.leps:
                w += self.leps[i]
            if i in self.nus:
                w += self.nus[i]
            if i in self.adds:
                w += self.adds[i]
            loss += self.loss_calc.get_loss(b=b, w=w)
        return loss

    @property
    def mtt(self):
        if self._mtt == -1:
            self.calculate_mtt()
        return self._mtt

    @property
    def grouping(self):
        if self._grouping == -1:
            self.calculate_mtt()
        return self._grouping

    def calculate_mtt(self):
        self._mtt = None
        self._grouping = None
        key = None
        # self._mtt = 'no nus'

        b_matching = BMatching(self.b)        

        add_matching = Matching(self.add, is_truth=True if self.case_num in [0, 1, 2, 3, 4, 5, 6] else False, compare_to_w=self.compare_add_to_w, tops=[0, 1])
        for self.bs in b_matching:
            lep_matching = Matching(self.lep, is_truth=True) if self.case_num in [0, 1, 2, 3] else \
            Matching(self.lep,
                     is_truth=False,
                     tops=b_matching.tops,
                     allow_assignment_to_one_top=False)

            for self.leps in lep_matching:
                if len(self.leps) < 2 or len([i for i in self.bs if i in self.leps]) < 2:
                    continue
                lep_in_b_tops = [i for i in self.leps if i in self.bs]
                # print('\n\nbs:', self.bs.keys())
                # print('leps', self.leps.keys())
                # print('potential leptons for nu matching', lep_in_b_tops)
                for self.lep_for_nu_reco in itertools.combinations(lep_in_b_tops, 2):
                    # print('actual leptons for nu matching', lep_for_nu_reco)
                    # lep_leftovers = [i for i in self.leps if i not in lep_for_nu_reco]
                    # print('lepton leftovers', lep_leftovers)
                    override_tops = {
                        nu.TopIndex : [key for key in self.leps if self.leps[key][0].TopIndex == nu.TopIndex][0] if (len([key for key in self.leps if self.leps[key][0].TopIndex == nu.TopIndex]) != 0) else nu.TopIndex for nu in self.nu } if self.case_num in [4, 7] else None

                    nu_matching = \
                        NuMatching(bs={i : self.bs[i] for i in self.lep_for_nu_reco if i in self.bs},
                                leps={i :self.leps[i] for i in self.lep_for_nu_reco},
                                nus=[[nu for nu in self.nu if nu.TopIndex in self.lep_for_nu_reco]] if self.data_type != 'Jet' else [None],
                                matching_type='truth' if self.case_num in [0, 1, 4, 7] else 'reco_truth' if self.case_num in [2, 5, 8] else 'reco_loss',
                                tops=self.lep_for_nu_reco,
                                event=self.event,
                                allow_assignment_to_one_top=False,
                                override_tops=override_tops)
                    
                    for self.nus in nu_matching:
                        # for i in self.nus:
                        #     print('\n', self.nus[i][0].px, self.nus[i][0].py, self.nus[i][0].pz, self.nus[i][0].e)
                        tops = [i for i in range(4) if i not in self.nus]
                        add_matching.update_tops(tops)
                        import numpy as np
                        for self.adds in add_matching:
                            # print('adds')
                            self.combine_tops()
                            self.select_resonance()
                            new_key = 1 if self.case_num in [0, 1, 2, 3] else self.calculate_loss()
                            if key is None or new_key < key or (new_key > key and self._mtt == -1):
                                # print('here')
                                # e = 0
                                # p = 0
                                # for i in self.res_products:
                                #     # print(i.pdgid, i.Mass)
                                #     # print(i.pdgid, i.px, i.py, i.pz, i.e)
                                #     e += i.e
                                #     p += i.pt*np.cosh(i.eta)
                                # print('the actual nus')
                                # for nu in self.nu:
                                #     print(nu.px, nu.py, nu.pz, nu.e)
                                self._mtt = sum(self.res_products).Mass # 
                                key = new_key
                                # print('Sum', (e**2 - p**2)**0.5, sum(self.res_products).Mass)
                                # print(e, p, sum(self.res_products).e, sum(self.res_products).pt*np.cosh(sum(self.res_products).eta))
                                self._grouping = self.tops.copy()
