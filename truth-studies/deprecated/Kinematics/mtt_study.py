import itertools
import sys
sys.path.append('/nfs/dust/atlas/user/sitnikov/AnalysisTopGNN/models/NeutrinoReconstructionOriginal/')
from neutrino_momentum_reconstruction import doubleNeutrinoSolutions
import vector as v
from AnalysisTopGNN.Particles.Particles import Top, Children, TruthJet, Jet
import numpy as np
import torch

t_mass = 172.76
w_mass = 80.379

def get_b_truthjet_idx(event, pt_cut=15000):
    result = [i for i, truthjet in enumerate(event.TruthJets) if truthjet.is_b and len(truthjet.Tops) != 0 and is_good_truthjet(truthjet, pt_cut)]
    return result

def is_one_b_per_top(event, pt_cut=15000):
    for top in event.Tops:
        if sum([1 for truthjet in top.TruthJets if truthjet.is_b and is_good_truthjet(truthjet, pt_cut)]) != 1:
            return False
    return True

def is_lep(child):
    return abs(child.pdgid) == 11 or abs(child.pdgid) == 13

def get_lep_child_idx(event):
    result = [i for i, child in enumerate(event.TopChildren) if is_lep(child)]
    return result

def is_nu(child):
    return abs(child.pdgid) == 12 or abs(child.pdgid) == 14

def get_nu_child_idx(event):
    result = [i for i, child in enumerate(event.TopChildren) if is_nu(child)]
    return result

def is_one_top_for_truthjet(event):
    if sum([1 for truthjet in event.TruthJets if len(truthjet.Tops) > 1]) != 0:
        return False
    return True

def is_event_ok_truthjet(event):
    issues = []
    pt_cut = get_pt_cut_truthjet(event)
    b_idx = get_b_truthjet_idx(event, pt_cut)
    count_lep_res = 0
    for top in event.Tops:
        if top.FromRes and sum([1 for child in top.Children if abs(child.pdgid) in [11, 13]]) != 0:
            count_lep_res += 1
    if count_lep_res != 1:
        issues.append(f'{count_lep_res}lepfromres')
    if len(event.Tops) != 4:
        issues.append('manytops')
    # if len(b_idx) < 4:
    #     issues.append('not4b_partons_' + str(len(b_idx)))
    # if not is_one_b_per_top(event, pt_cut):
    #     issues.append('not1b1t')
    if not is_one_top_for_truthjet(event):
        issues.append('mergedjets')
    if len(get_lep_child_idx(event)) != 2:
        issues.append('not2lep')
    if sum([1 for child in event.TopChildren if abs(child.pdgid) == 15]) != 0:
        issues.append('tau')
    if len(issues) == 0:
        issues.append('ok')
    if len(issues) == 1 and 'partons' in issues[0]:
        issues.append('ok_variable')
    if len(issues) == 1 and 'variable' in issues[0]:
        issues.append('ok_partons')
    return issues

# class Filter:
#
#     def __init__(self):
#         self.Rej = False
#         self.Obj = []
#         self.truthjet = False
#
#     def AssignTruth(self, lst):
#         return [ self.Obj[i].TopIndex[0] if self.truthjet else self.Obj[i].TopIndex for i in lst]
#
#     def TruthJet(lst):
#         self.truthjet = True
#         return self.AssignTruth(lst)
#
#     def NotTruthJet(lst):
#         return self.AssignTruth(lst)
#
#     def Highest
#
# F = Filter()
# F.Obj += event.TruthJets
# F.AssignTruth(jet_idx)




def get_truthjet_assignment_truth(event, jet_idx):
    result = []
    for idx in jet_idx:
        result.append(event.TruthJets[idx].TopIndex[0])
    return result

def get_lep_assignment_truth(event, lep_idx):
    result = []
    for idx in lep_idx:
        result.append(event.TopChildren[idx].TopIndex)
    return result

def get_nu_assignment_truth(event, nu_idx):
    result = []
    for idx in nu_idx:
        result.append(event.TopChildren[idx].TopIndex)
    return result






def make_4vector(particle):
    # print(particle.e, particle.pt, particle.eta, particle.phi)
    result = v.obj(e=particle.e/1000, pt=particle.pt/1000, eta=particle.eta, phi=particle.phi)
    # print(result.e, result.pt, result.eta, result.phi)
    return result

def select_resonance_pt(tops, lep_tops):
    res_indices = []
    sum_tops = {itop : 0 for itop in tops}
    for i in tops:
        if len(tops[i]) == 0:
            sum_tops[i] = Top()
            sum_tops[i].pt = 0
        else:
            sum_tops[i] = sum(tops[i])
    if sum_tops[lep_tops[0]].pt > sum_tops[lep_tops[1]].pt:
        res_indices.append(lep_tops[0])
    else:
        res_indices.append(lep_tops[1])
    had_tops = [itop for itop in sum_tops if itop not in lep_tops]
    if sum_tops[had_tops[0]].pt > sum_tops[had_tops[1]].pt:
        res_indices.append(had_tops[0])
    else:
        res_indices.append(had_tops[1])
    return res_indices

def select_resonance_truth(tops, event):
    res_indices = []
    for itop in tops:
        # if event.Tops[itop].FromRes:
        #     res_indices.append(itop)
        if len(tops[itop]) != 0 and ((type(tops[itop][0]) == type(Children()) and event.Tops[itop].FromRes) or (type(tops[itop][0]) != type(Children()) and tops[itop][0].Tops[0].FromRes)):
            res_indices.append(itop)
    return res_indices

def find_diff(v1, v2):
    return ((v1.x - v2.x)**2 + (v1.y - v2.y)**2 + (v1.z - v2.z)**2)**0.5

def make_particle(v):
    result = Children()
    result.pt = (v.x**2 + v.y**2)**0.5*1000
    result.e = v.t*1000
    result.eta = v.eta
    result.phi = v.phi
    result.pdgid = 12
    return result

def make_vector(obj):
    return v.obj(x=obj[0], y=obj[1], z=obj[2], m=0)

def select_result_using_nu_truth(nu_truth, result):
    tv1 = nu_truth[0]
    tv2 = nu_truth[1]
    answer = {}
    for j in range(len(result)):
        rv1 = make_vector(result[j][0])
        rv2 = make_vector(result[j][1])
        c11 = find_diff(tv1, rv1)
        c22 = find_diff(tv2, rv2)
        c21 = find_diff(tv2, rv1)
        c12 = find_diff(tv1, rv2)
        answer[f'{j} same'] = c11 + c22
        # print(c11 + c22)
    choice = min(answer, key=answer.get)
    number_reco = int(choice.split(' ')[0])
    nu1 = make_vector(result[number_reco][0])
    nu2 = make_vector(result[number_reco][1])
    # if 'opposite' in choice:
    #     nu1, nu2 = nu2, nu1
    # print('selected')
    # print(nu1)
    # print(nu2)
    # print(nu_truth[0].x, nu_truth[0].y, nu_truth[0].z, nu_truth[0].m)
    # print(nu_truth[1].x, nu_truth[1].y, nu_truth[1].z, nu_truth[1].m)
    return make_particle(nu1), make_particle(nu2)

def get_dR(v1, v2):
    return((v1.eta - v2.eta)**2 + (v1.phi - v2.phi)**2)**0.5

def get_loss(b, w, alpha=1, beta=1, gamma=1):
    dR_ww = []
    dR_wb = []
    for i in range(len(w)):
        if b:
            dR_wb.append(get_dR(b, w[i]))
        for j in range(len(w)):
            if i == j:
                continue
            dR_ww.append(get_dR(w[i], w[j]))
    w_mass_reco = sum(w).CalculateMass() if len(w) != 0 else 0
    if b == None:
        if len(w) == 0:
            t_mass_reco = 0
        else:
            t_mass_reco = w_mass_reco
    else:
        t_mass_reco = sum(w + [b]).CalculateMass()
    dR = dR_ww + dR_wb
    mean_dR = np.mean(dR) if len(dR) != 0 else 0
    return  alpha*mean_dR + \
    beta*1e-2*abs(w_mass_reco - w_mass) + \
    gamma*1e-2*abs(t_mass_reco - t_mass)

def select_result_using_loss(bs, leps, result, alpha=1, beta=1, gamma=1):
    losses = {}
    for nus_np in result:
        nus = [make_particle(make_vector(nu)) for nu in nus_np]
        for assignment in [(0, 1), (1, 0)]:
            loss = get_loss(b=bs[0], w=[leps[0], nus[assignment[0]]], alpha=alpha, beta=beta, gamma=gamma) + get_loss(b=bs[1], w=[leps[1], nus[assignment[1]]], alpha=alpha, beta=beta, gamma=gamma)
            losses[loss] = (assignment, nus)
    min_loss = min(losses.keys())
    assignment, nus = losses[min_loss]
    # vec = make_4vector(nus[assignment[0]])
    # print(vec.x, vec.y, vec.z, vec.m)
    # vec = make_4vector(nus[assignment[1]])
    # print(vec.x, vec.y, vec.z, vec.m)
    return nus[assignment[0]], nus[assignment[1]]

def get_lep_assignments(b_idx):
    result = []
    for i in b_idx:
        for j in b_idx:
            if i != j:
                result.append((i, j))
    return result

def is_good_truthjet(truthjet, pt_cut=15000):
    # return len(truthjet.Tops) != 0
    return truthjet.pt >= pt_cut

def get_pt_cut_truthjet(event, max_njets=11):
    if len(event.TruthJets) <= max_njets:
        return 15000
    pts = [truthjet.pt for truthjet in event.TruthJets]
    pts = sorted(pts, reverse=True)
    # print(pts)
    # print((pts[9] + pts[10])*0.5)
    return max(15000, (pts[max_njets - 1] + pts[max_njets])*0.5)


def get_truthjet_assignments(event, had_tops):
    result = []
    checked_perms = set()
    # notbjets = [idx for idx, truthjet in enumerate(event.TruthJets) if not truthjet.is_b and is_good_truthjet(truthjet)]
    good_jets = [ijet for ijet, truthjet in enumerate(event.TruthJets) if not truthjet.is_b and is_good_truthjet(truthjet)]
    count_not_ok = 0
    mass_to_perm = {}
    for i in had_tops:
        for j in had_tops:
            if i != j:
                for combination in itertools.combinations_with_replacement([i, j], len(good_jets)):
                    for perm in itertools.permutations(combination):
                        if perm in checked_perms:
                            continue
                        checked_perms.add(perm)
                        is_ok = True
                        masses_w = []
                        masses_t = []
                        for k in [i, j]:
                            tj = [event.TruthJets[good_jets[idx]] for idx in range(len(good_jets)) if perm[idx] == k]
                            if len(tj) == 0:
                                masses_w.append(0)
                            else:
                                tjmass = sum(tj).CalculateMass()
                                masses_w.append(tjmass)
                        avgmass_w = np.mean(masses_w) if len(masses_w) != 0 else 0
                        if abs(avgmass_w - w_mass) > 20:
                            is_ok = False
                        if is_ok:
                            final_perm = []
                            for idx in range(len(good_jets)):
                                final_perm.append(perm[idx])

                            if avgmass_w not in mass_to_perm:
                                mass_to_perm[avgmass_w] = []
                            mass_to_perm[avgmass_w].append(final_perm)
                        else:
                            count_not_ok += 1
    masses = sorted(list(mass_to_perm.keys()))
    for mass in masses:
        result += mass_to_perm[mass]
        if len(result) > 3:
            break
    # print(len(result))
    return result

def Combinatorial(n, k, msk, t = [], v = [], num = 0):

    if n == 0:
        t += [torch.tensor(num).unsqueeze(-1).bitwise_and(msk).ne(0).to(dtype = int).tolist()]
        v += [num]
        return t, v

    if n-1 >= k:
        t, v = Combinatorial(n-1, k, msk, t, v, num)
    if k > 0:
        t, v = Combinatorial(n-1, k -1, msk, t, v, num | ( 1 << (n-1)))

    return t, v

def get_truthjet_assignments_smart(event, good_jets):
    result = []
    checked_perms = set()
    # notbjets = [idx for idx, truthjet in enumerate(event.TruthJets) if not truthjet.is_b and is_good_truthjet(truthjet)]
    # good_jets = [ijet for ijet, truthjet in enumerate(event.TruthJets) if not truthjet.is_b and is_good_truthjet(truthjet)]
    mass_too_high = []
    mass_too_low = []
    count_not_ok = 0
    mass_to_perm = {}
    num = len(good_jets)
    perms_to_check = []
    # msk = torch.pow(2, torch.arange(num))
    # for i in range(num + 1):
    #     print(i, num)
    #     out, _ = Combinatorial(num, i, msk)
    #     perms_to_check += out
    # print([len(perm) for perm in perms_to_check])
    # for idx in good_jets:
    #     print(event.TruthJets[idx].pt/1000)

    for combination in itertools.combinations_with_replacement([0, 1], len(good_jets)):
        for perm in itertools.permutations(combination):
            if perm in checked_perms:
                continue
            if (1 - i for i in perm) in checked_perms:
                continue
            checked_perms.add(perm)
            perms_to_check.append(perm)
    import random
    random.shuffle(perms_to_check)
    # print(len(perms_to_check), 'perms in total')
    for perm in perms_to_check:
        # print(perm)
        is_perm_ok = True
        for p in mass_too_high:
            assignment = {k : [idx for idx in p if perm[idx] == k] for k in [0, 1]}
            if len(assignment[0]) == 0 or len(assignment[1])  == 0:
                is_perm_ok = False
                # print('skipping', perm)
                break
        if not is_perm_ok:
            continue
        is_ok = True
        masses_w = []
        for k in [0, 1]:
            # print(len(good_jets), len(perm))
            tj = [event.TruthJets[good_jets[idx]] for idx in range(len(good_jets)) if perm[idx] == k]
            if len(tj) == 0:
                masses_w.append(0)
            else:
                tjmass = sum(tj).CalculateMass()
                masses_w.append(tjmass)
                # if tjmass - w_mass > 60:
                #     mass_too_high.append([idx for idx in range(len(good_jets)) if perm[idx] == k])
                #     # print('appended to mass_too_high', mass_too_high[-1])
                #     is_ok = False
                #     break
        avgmass_w = np.mean(masses_w) if len(masses_w) != 0 else 0
        # if avgmass_w - w_mass > 20:
        #     is_ok = False
        if is_ok:
            final_perm = []
            for idx in range(len(good_jets)):
                final_perm.append(perm[idx])

            if avgmass_w not in mass_to_perm:
                mass_to_perm[avgmass_w] = []
            mass_to_perm[avgmass_w].append(final_perm)
        else:
            count_not_ok += 1
    masses = sorted(list(mass_to_perm.keys()))
    for mass in masses:
        result += mass_to_perm[mass]
        if len(result) > 5:
            break
    # print(len(result))
    return result

def reconstruct_mtt_truthjets(event, case=0, alpha=1, beta=1, gamma=1):
    pt_cut = get_pt_cut_truthjet(event)
    # print(pt_cut)
    b_idx = get_b_truthjet_idx(event, pt_cut)
    jet_idx = [idx for idx in range(len(event.TruthJets)) if idx not in b_idx and is_good_truthjet(event.TruthJets[idx], pt_cut)]
    # print('b jets')
    # for idx in b_idx:
    #     print(event.TruthJets[idx])
    # print('add jets')
    # for idx in jet_idx:
    #     print(event.TruthJets[idx])
    lep_idx = get_lep_child_idx(event)
    lep_tops = [event.TopChildren[idx].TopIndex for idx in lep_idx]

    if case in [0, 1, 2, 3]:
        lep_assignments = [get_lep_assignment_truth(event, lep_idx)]
    else:
        tops_with_b = [event.TruthJets[idx].TopIndex[0] for idx in b_idx]
        lep_assignments = get_lep_assignments(tops_with_b)

    if case in [0, 1, 2, 3, 4, 5, 6]:
        jet_assignments = [get_truthjet_assignment_truth(event, jet_idx)]
    else:
        # print(len(jet_idx))
        # print([truthjet.TopIndex for truthjet in event.TruthJets])
        jet_assignments_template = get_truthjet_assignments_smart(event, jet_idx)
        if len(jet_assignments_template) == 0:
            # print('no jet assignment')
            return None
        # print('done')
    losses = {}

    # print(len(lep_assignments))
    for lep_assignment in lep_assignments:
        if case in [4, 5, 6]:
            if sum([1 for idx in lep_assignment if idx not in lep_tops]) != 0:
                # print('lep wrong')
                continue
        blep_idx = [idx for idx in b_idx if event.TruthJets[idx].TopIndex[0] in lep_assignment]
        if case not in [0, 1, 4, 7] and len(blep_idx) < 2:
            # print('not 2 blep')
            continue

        if case in [2, 3, 5, 6, 8, 9]:
            try:
                # print('HEE')
                bs = [make_4vector(event.TruthJets[idx]) for idx in blep_idx]
                leps = [make_4vector(event.TopChildren[idx]) for idx in lep_idx]
                nu_idx = get_nu_child_idx(event)
                nus = [make_4vector(event.TopChildren[idx]) for idx in nu_idx]
                nu_solutions = doubleNeutrinoSolutions((bs[0], bs[1]), (leps[0], leps[1]), (event.met/1000*np.cos(event.met_phi), event.met/1000*np.sin(event.met_phi)))
                print((nu_solutions.nunu_s))
                if case in [2, 5, 8]:
                    nu_res = select_result_using_nu_truth(nus, nu_solutions.nunu_s)
                else:
                    bs = [event.TruthJets[idx] for idx in blep_idx]
                    leps = [event.TopChildren[idx] for idx in lep_idx]
                    nu_res = select_result_using_loss(bs, leps, nu_solutions.nunu_s, alpha=alpha, beta=beta, gamma=gamma)
            except np.linalg.LinAlgError:
                continue
        else:
            nu_idx = get_nu_child_idx(event)
            nu_res = [event.TopChildren[idx] for idx in nu_idx]
        import time
        start = time.time()
        if case not in [0, 1, 2, 3, 4, 5, 6]:
            had_tops = [itop for itop in range(len(event.Tops)) if itop not in lep_assignment]
            # print(had_tops)
            jet_assignments = []
            for jet_assignment in jet_assignments_template:
                # print(jet_assignment)
                jet_assignments.append([had_tops[i] if i != -1 else -1 for i in jet_assignment])
                jet_assignments.append([had_tops[1 - i] if i != -1 else -1 for i in jet_assignment])
                # print(jet_assignments[-1])
                # print(jet_assignments[-2])
        end = time.time()
        # print(case)
        # print(len(jet_assignments), len(jet_idx), end-start)
        for jet_assignment in jet_assignments:
            tops = {i : [] for i in range(len(event.Tops))}
            for idx in b_idx:
                tops[event.TruthJets[idx].TopIndex[0]].append(event.TruthJets[idx])
            for itop, ilep in zip(lep_assignment, lep_idx):
                tops[itop].append(event.TopChildren[ilep])
            for itop, nu in zip(lep_assignment, nu_res):
                tops[itop].append(nu)
            for itop, ijet in zip(jet_assignment, jet_idx):
                if itop != -1:
                    tops[itop].append(event.TruthJets[ijet])
            # for itop in tops:
            #     print([obj.TopIndex for obj in tops[itop]])
            if case == 0:
                res_indices = select_resonance_truth(tops, event)
            else:
                res_indices = select_resonance_pt(tops, lep_assignment)
            # for itop in res_indices:
            #     print(itop)
            #     for item in tops[itop]:
            #         print(item.pt)
            # print(res_indices)
            res_products = []
            for itop in res_indices:
                for item in tops[itop]:
                    res_products.append(item)
                    # print(item)
            # print(res_products)
            # res_products = [item for item in tops[itop] for itop in res_indices]
            lep_ok = 1
            had_ok = 1
            for itop in res_indices:
                if itop in lep_assignment:
                    for obj in tops[itop]:
                        if type(obj) == type(Children()):
                            if obj.pdgid == 'children_pdgid':
                                continue
                            if obj.TopIndex != itop:
                                lep_ok -= 1
                                break
                        else:
                            if obj.TopIndex[0] != -1 and obj.TopIndex[0] != itop:
                                lep_ok -= 1
                                break
                else:
                    for obj in tops[itop]:
                        if type(obj) == type(Children()):
                            if obj.TopIndex != itop:
                                had_ok -= 1
                                break
                        else:
                            if obj.TopIndex[0] != -1 and obj.TopIndex[0] != itop:
                                had_ok -= 1
                                break

            if case in [0, 1, 2, 3]:
                if len(res_products) == 0:
                    # print('no res products')
                    return None
                return sum(res_products).CalculateMass(), f'{lep_ok}lep{had_ok}had_right'
            else:
                if len(res_products) == 0:
                    # print('no res products')
                    continue
                loss = 0
                for itop in tops:
                    if len(tops[itop]) == 0:
                        b = None
                        w = []
                    elif type(tops[itop][0]) == type(TruthJet()) and tops[itop][0].is_b:
                        b = tops[itop][0]
                        w = tops[itop][1:]
                    else:
                        b = None
                        w = tops[itop]
                    loss += get_loss(b=b, w=w, alpha=alpha, beta=beta, gamma=gamma)


                losses[loss] = {'m' : sum(res_products).CalculateMass(), 'label' : f'{lep_ok}lep{had_ok}had_right'}
                # print('loss', loss, lep_assignment, {itop : [obj.TopIndex for obj in tops[itop]] for itop in tops})
    if len(losses) == 0:
        # print('no lossess')
        return None
    min_loss = min(losses.keys())
    # print('choosing loss', min_loss)
    return losses[min_loss]['m'], losses[min_loss]['label']

def get_b_child_idx(event):
    result = [i for i, child in enumerate(event.TopChildren) if abs(child.pdgid) == 5]
    return result

def get_jet_child_assignment_truth(event, jet_idx):
    result = []
    for idx in jet_idx:
        result.append(event.TopChildren[idx].TopIndex)
    return result

def select_resonance_truth_children(tops, event):
    res_indices = []
    for itop in tops:
        if not event.Tops[itop].FromRes:
            res_indices.append(itop)
    return res_indices

def get_jet_child_assignments(event, had_tops):
    result = []
    checked_perms = set()
    notbjets = [idx for idx, child in enumerate(event.TopChildren) if abs(child.pdgid) in [1, 2, 3, 4]]
    good_jets = notbjets
    count_not_ok = 0
    mass_to_perm = {}
    for i in had_tops:
        for j in had_tops:
            if i != j:
                for combination in itertools.combinations_with_replacement([i, j], len(good_jets)):
                    for perm in itertools.permutations(combination):
                        if perm in checked_perms:
                            continue
                        checked_perms.add(perm)
                        is_ok = True
                        masses_w = []
                        masses_t = []
                        for k in [i, j]:
                            tj = [event.TopChildren[good_jets[idx]] for idx in range(len(good_jets)) if perm[idx] == k]
                            if len(tj) == 0:
                                # is_ok = False
                                masses_w.append(0)
                                # if len(tops[k]) == 0:
                                #     masses_t.append(0)
                                # else:
                                #     masses_t.append(sum(tops[k]).CalculateMass())
                            else:
                                tjmass = sum(tj).CalculateMass()
                                # if abs(tjmass - w_mass) > 40:
                                #     is_ok = False
                                masses_w.append(tjmass)
                                # masses_t.append(sum(tj + tops[k]).CalculateMass())
                        avgmass_w = np.mean(masses_w) if len(masses_w) != 0 else 0
                        # avgmass_t = np.mean(masses_t)
                        if abs(avgmass_w - w_mass) > 40:
                            is_ok = False
                        if is_ok:
                            igood_jet = 0
                            final_perm = []
                            for idx in notbjets:
                                if idx in good_jets:
                                    final_perm.append(perm[igood_jet])
                                    igood_jet += 1
                                else:
                                    final_perm.append(-1)

                            if avgmass_w not in mass_to_perm:
                                mass_to_perm[avgmass_w] = []
                            mass_to_perm[avgmass_w].append(final_perm)
                            # result.append(final_perm)
                        else:
                            count_not_ok += 1
    masses = sorted(list(mass_to_perm.keys()))
    for mass in masses:
        result += mass_to_perm[mass]
        if len(result) > 5:
            break
    # print(len(result))
    return result

def get_jet_child_assignments_smart(event, good_jets):
    result = []
    checked_perms = set()
    mass_too_high = []
    mass_too_low = []
    count_not_ok = 0
    mass_to_perm = {}
    n = len(good_jets)
    perms_to_check, _ = Combinatorial(n, n, msk = torch.pow(2, torch.arange(n)))
    import random
    random.shuffle(perms_to_check)
    for perm in perms_to_check:
        # print(perm)
        is_perm_ok = True
        for p in mass_too_high:
            assignment = {k : [idx for idx in p if perm[idx] == k] for k in [0, 1]}
            if len(assignment[0]) == 0 or len(assignment[1])  == 0:
                is_perm_ok = False
                # print('skipping', perm)
                break
        if not is_perm_ok:
            continue
        is_ok = True
        masses_w = []
        for k in [0, 1]:
            tj = [event.TopChildren[good_jets[idx]] for idx in range(len(good_jets)) if perm[idx] == k]
            if len(tj) == 0:
                masses_w.append(0)
            else:
                tjmass = sum(tj).CalculateMass()
                masses_w.append(tjmass)
                # if tjmass - w_mass > 60:
                #     mass_too_high.append([idx for idx in range(len(good_jets)) if perm[idx] == k])
                #     # print('appended to mass_too_high', mass_too_high[-1])
                #     is_ok = False
                #     break
        avgmass_w = np.mean(masses_w) if len(masses_w) != 0 else 0
        # if avgmass_w - w_mass > 20:
        #     is_ok = False
        if is_ok:
            final_perm = []
            for idx in range(len(good_jets)):
                final_perm.append(perm[idx])

            if avgmass_w not in mass_to_perm:
                mass_to_perm[avgmass_w] = []
            mass_to_perm[avgmass_w].append(final_perm)
        else:
            count_not_ok += 1
    masses = sorted(list(mass_to_perm.keys()))
    for mass in masses:
        result += mass_to_perm[mass]
        if len(result) > 5:
            break
    # print(len(result))
    return result

def reconstruct_mtt_children(event, case=0, alpha=1, beta=1, gamma=1):
    b_idx = get_b_child_idx(event)
    jet_idx = [idx for idx, child in enumerate(event.TopChildren) if abs(child.pdgid) in [1, 2, 3, 4]]
    lep_idx = get_lep_child_idx(event)


    if case in [0, 1, 2, 3]:
        lep_assignments = [get_lep_assignment_truth(event, lep_idx)]
    else:
        tops_with_b = [event.TopChildren[idx].TopIndex for idx in b_idx]
        lep_assignments = get_lep_assignments(tops_with_b)

    losses = {}

    for lep_assignment in lep_assignments:
        blep_idx = [idx for idx in b_idx if event.TopChildren[idx].TopIndex in lep_assignment]
        # print(lep_assignment)
        if len(blep_idx) < 2:
            continue


        if case in [2, 3, 5, 6, 8, 9]:
            try:
                # for idx in blep_idx + lep_idx:
                #     print(event.TopChildren[idx])
                bs = [make_4vector(event.TopChildren[idx]) for idx in blep_idx]
                leps = [make_4vector(event.TopChildren[idx]) for idx in lep_idx]
                nu_idx = get_nu_child_idx(event)
                nus = [make_4vector(event.TopChildren[idx]) for idx in nu_idx]
                print(bs)
                print(leps)
                print(event.met, event.met_phi)
                nu_solutions = doubleNeutrinoSolutions((bs[0], bs[1]), (leps[0], leps[1]), (event.met/1000*np.cos(event.met_phi), event.met/1000*np.sin(event.met_phi)))
                print(event.met)
                for sol_pair in nu_solutions.nunu_s:
                    print(sol_pair)
                for nu in bs:
                    print(nu.e, nu.pt, nu.phi, nu.eta)
                for idx in blep_idx:
                    print(event.TopChildren[idx].e, event.TopChildren[idx].pt, event.TopChildren[idx].phi, event.TopChildren[idx].eta)
                # print(event.met, event.met_phi)
                # print(len(nu_solutions.nunu_s))
                if case in [2, 5, 8]:
                    nu_res = select_result_using_nu_truth(nus, nu_solutions.nunu_s)
                else:
                    bs = [event.TopChildren[idx] for idx in blep_idx]
                    leps = [event.TopChildren[idx] for idx in lep_idx]
                    nu_res = select_result_using_loss(bs, leps, nu_solutions.nunu_s)
            except np.linalg.LinAlgError:
                continue
        else:
            nu_idx = get_nu_child_idx(event)
            nu_res = [event.TopChildren[idx] for idx in nu_idx]


        if case in [0, 1, 2, 3, 4, 5, 6]:
            jet_assignments = [get_jet_child_assignment_truth(event, jet_idx)]
            # print(jet_assignments)
        else:
            had_tops = [itop for itop in range(len(event.Tops)) if itop not in lep_assignment]
            jet_assignments = get_jet_child_assignments(event, had_tops)
        # print(case)
        for jet_assignment in jet_assignments:
            tops = {i : [] for i in range(len(event.Tops))}
            for idx in b_idx:
                tops[event.TopChildren[idx].TopIndex].append(event.TopChildren[idx])
            for itop, ilep in zip(lep_assignment, lep_idx):
                tops[itop].append(event.TopChildren[ilep])
            for itop, nu in zip(lep_assignment, nu_res):
                tops[itop].append(nu)
            for itop, ijet in zip(jet_assignment, jet_idx):
                if itop != -1:
                    tops[itop].append(event.TopChildren[ijet])

            if case == 0:
                res_indices = select_resonance_truth_children(tops, event)
            else:
                res_indices = select_resonance_pt(tops, lep_assignment)
            res_products = []
            for itop in res_indices:
                for item in tops[itop]:
                    res_products.append(item)
                    # print(item)
            lep_ok = 1
            had_ok = 1
            for itop in res_indices:
                for obj in tops[itop]:
                    if obj.pdgid == 'children_pdgid':
                        continue
                    if obj.TopIndex != itop:
                        lep_ok -= 1
                        break

            if case in [0, 1, 2, 3]:
                if len(res_products) == 0:
                    return None
                # print('------------------------------')
                # for res_product in res_products:
                #     print(res_product)
                return sum(res_products).CalculateMass(), f'{lep_ok}lep{had_ok}had_right'
            else:
                if len(res_products) == 0:
                    continue
                loss = 0
                for itop in tops:
                    if type(tops[itop][0]) == type(TruthJet()) and tops[itop][0].is_b:
                        b = tops[itop][0]
                        w = tops[itop][1:]
                    else:
                        b = None
                        w = tops[itop]
                    loss += get_loss(b=b, w=w, alpha=alpha, beta=beta, gamma=gamma)
                losses[loss] = {'m' : sum(res_products).CalculateMass(), 'label' : f'{lep_ok}lep{had_ok}had_right'}


    if len(losses) == 0:
        return None
    min_loss = min(losses.keys())
    return losses[min_loss]['m'], losses[min_loss]['label']



### Reco objects

def get_b_jet_idx(event, pt_cut=20000):
    result = [i for i, jet in enumerate(event.Jets) if jet.btagged and len(jet.Tops) != 0 and is_good_jet(jet, pt_cut)]
    return result

def is_one_b_per_top(event, pt_cut=20000):
    for top in event.Tops:
        if sum([1 for jet in top.Jets if jet.btagged and is_good_jet(jet, pt_cut)]) != 1:
            return False
    return True

def is_one_top_for_jet(event):
    if sum([1 for jet in event.Jets if len(jet.Tops) > 1]) != 0:
        return False
    return True

def is_event_ok_jet(event):
    issues = []
    pt_cut = get_pt_cut_jets(event)
    b_idx = get_b_jet_idx(event, pt_cut)
    count_lep_res = 0
    for top in event.Tops:
        if top.FromRes and sum([1 for child in top.Children if abs(child.pdgid) in [11, 13]]) != 0:
            count_lep_res += 1
    if count_lep_res != 1:
        issues.append(f'{count_lep_res}lepfromres')
    if len(event.Tops) != 4:
        issues.append('manytops')
    if not is_one_top_for_jet(event):
        issues.append('mergedjets')
    if len(get_lep_child_idx(event)) != 2:
        issues.append('not2lep')
    if sum([1 for child in event.TopChildren if abs(child.pdgid) == 15]) != 0:
        issues.append('tau')
    if len(issues) == 0:
        issues.append('ok')
    return issues

def get_jet_assignment_truth(event, jet_idx):
    result = []
    for idx in jet_idx:
        result.append(event.Jets[idx].TopIndex[0])
    return result

def is_good_jet(jet, pt_cut=20000):
    # return len(truthjet.Tops) != 0
    return jet.pt >= pt_cut

def get_pt_cut_jets(event, max_njets=11):
    if len(event.Jets) <= max_njets:
        return 20000
    pts = [jet.pt for jet in event.Jets]
    pts = sorted(pts, reverse=True)
    # print(pts)
    # print((pts[9] + pts[10])*0.5)
    return max(20000, (pts[max_njets - 1] + pts[max_njets])*0.5)

def get_jet_assignments(event, had_tops):
    result = []
    checked_perms = set()
    good_jets = [ijet for ijet, jet in enumerate(event.Jets) if not jet.btagged and is_good_jet(jet)]
    count_not_ok = 0
    mass_to_perm = {}
    for i in had_tops:
        for j in had_tops:
            if i != j:
                for combination in itertools.combinations_with_replacement([i, j], len(good_jets)):
                    for perm in itertools.permutations(combination):
                        if perm in checked_perms:
                            continue
                        checked_perms.add(perm)
                        is_ok = True
                        masses_w = []
                        masses_t = []
                        for k in [i, j]:
                            tj = [event.Jets[good_jets[idx]] for idx in range(len(good_jets)) if perm[idx] == k]
                            if len(tj) == 0:
                                masses_w.append(0)
                            else:
                                tjmass = sum(tj).CalculateMass()
                                masses_w.append(tjmass)
                        avgmass_w = np.mean(masses_w) if len(masses_w) != 0 else 0
                        if abs(avgmass_w - w_mass) > 20:
                            is_ok = False
                        if is_ok:
                            final_perm = []
                            for idx in range(len(good_jets)):
                                final_perm.append(perm[idx])

                            if avgmass_w not in mass_to_perm:
                                mass_to_perm[avgmass_w] = []
                            mass_to_perm[avgmass_w].append(final_perm)
                        else:
                            count_not_ok += 1
    masses = sorted(list(mass_to_perm.keys()))
    for mass in masses:
        result += mass_to_perm[mass]
        if len(result) > 3:
            break
    # print(len(result))
    return result

def get_jet_assignments_smart(event, good_jets):
    result = []
    checked_perms = set()
    mass_too_high = []
    mass_too_low = []
    count_not_ok = 0
    mass_to_perm = {}
    perms_to_check = []
    for combination in itertools.combinations_with_replacement([0, 1], len(good_jets)):
        for perm in itertools.permutations(combination):
            if perm in checked_perms:
                continue
            if (1 - i for i in perm) in checked_perms:
                continue
            checked_perms.add(perm)
            perms_to_check.append(perm)
    import random
    random.shuffle(perms_to_check)
    # n = len(good_jets)
    # perms_to_check, _ = Combinatorial(n, n, msk = torch.pow(2, torch.arange(n)))
    import random
    random.shuffle(perms_to_check)
    # print(len(perms_to_check), 'perms in total')
    for perm in perms_to_check:
        # print(perm)
        is_perm_ok = True
        for p in mass_too_high:
            assignment = {k : [idx for idx in p if perm[idx] == k] for k in [0, 1]}
            if len(assignment[0]) == 0 or len(assignment[1])  == 0:
                is_perm_ok = False
                # print('skipping', perm)
                break
        if not is_perm_ok:
            continue
        is_ok = True
        masses_w = []
        for k in [0, 1]:
            tj = [event.Jets[good_jets[idx]] for idx in range(len(good_jets)) if perm[idx] == k]
            if len(tj) == 0:
                masses_w.append(0)
            else:
                tjmass = sum(tj).CalculateMass()
                masses_w.append(tjmass)
                # if tjmass - w_mass > 60:
                #     mass_too_high.append([idx for idx in range(len(good_jets)) if perm[idx] == k])
                #     # print('appended to mass_too_high', mass_too_high[-1])
                #     is_ok = False
                #     break
        avgmass_w = np.mean(masses_w) if len(masses_w) != 0 else 0
        # if avgmass_w - w_mass > 20:
        #     is_ok = False
        if is_ok:
            final_perm = []
            for idx in range(len(good_jets)):
                final_perm.append(perm[idx])

            if avgmass_w not in mass_to_perm:
                mass_to_perm[avgmass_w] = []
            mass_to_perm[avgmass_w].append(final_perm)
        else:
            count_not_ok += 1
    masses = sorted(list(mass_to_perm.keys()))
    for mass in masses:
        result += mass_to_perm[mass]
        if len(result) > 5:
            break
    # print(len(result))
    return result

def get_leptons_reco(event):
    return event.Electrons + event.Muons

def reconstruct_mtt_jets(event, case=0, alpha=1, beta=1, gamma=1):
    pt_cut = get_pt_cut_jets(event)
    b_idx = get_b_jet_idx(event, pt_cut)
    jet_idx = [idx for idx in range(len(event.Jets)) if idx not in b_idx and is_good_jet(event.Jets[idx], pt_cut)]
    lep_idx = get_lep_child_idx(event)
    lep_tops = [event.TopChildren[idx].TopIndex for idx in lep_idx]

    if case in [0, 1, 2, 3]:
        lep_assignments = [get_lep_assignment_truth(event, lep_idx)]
    else:
        tops_with_b = [event.Jets[idx].TopIndex[0] for idx in b_idx]
        lep_assignments = get_lep_assignments(tops_with_b)

    if case in [0, 1, 2, 3, 4, 5, 6]:
        jet_assignments = [get_jet_assignment_truth(event, jet_idx)]
    else:
        # print(len(jet_idx))
        # print([truthjet.TopIndex for truthjet in event.TruthJets])
        jet_assignments_template = get_jet_assignments_smart(event, jet_idx)
        if len(jet_assignments_template) == 0:
            # print('no jet assignment')
            return None
        # print('done')
    losses = {}

    # print(len(lep_assignments))
    for lep_assignment in lep_assignments:
        if case in [4, 5, 6]:
            if sum([1 for idx in lep_assignment if idx not in lep_tops]) != 0:
                # print('lep wrong')
                continue
        blep_idx = [idx for idx in b_idx if event.Jets[idx].TopIndex[0] in lep_assignment]
        if len(blep_idx) < 2:
            # print('not 2 blep')
            continue

        if case in [2, 3, 5, 6, 8, 9]:
            try:
                bs = [make_4vector(event.Jets[idx]) for idx in blep_idx]
                leps = [make_4vector(event.TopChildren[idx]) for idx in lep_idx]
                nu_idx = get_nu_child_idx(event)
                nus = [make_4vector(event.TopChildren[idx]) for idx in nu_idx]
                nu_solutions = doubleNeutrinoSolutions((bs[0], bs[1]), (leps[0], leps[1]), (event.met*np.cos(event.met_phi), event.met*np.sin(event.met_phi)))
                if case in [2, 5, 8]:
                    nu_res = select_result_using_nu_truth(nus, nu_solutions.nunu_s)
                else:
                    bs = [event.Jets[idx] for idx in blep_idx]
                    leps = [event.TopChildren[idx] for idx in lep_idx]
                    nu_res = select_result_using_loss(bs, leps, nu_solutions.nunu_s, alpha=alpha, beta=beta, gamma=gamma)
            except np.linalg.LinAlgError:
                continue
        else:
            nu_idx = get_nu_child_idx(event)
            nu_res = [event.TopChildren[idx] for idx in nu_idx]
        import time
        start = time.time()
        if case not in [0, 1, 2, 3, 4, 5, 6]:
            had_tops = [itop for itop in range(len(event.Tops)) if itop not in lep_assignment]
            # print(had_tops)
            jet_assignments = []
            for jet_assignment in jet_assignments_template:
                # print(jet_assignment)
                jet_assignments.append([had_tops[i] if i != -1 else -1 for i in jet_assignment])
                jet_assignments.append([had_tops[1 - i] if i != -1 else -1 for i in jet_assignment])
                # print(jet_assignments[-1])
                # print(jet_assignments[-2])
        end = time.time()
        # print(case)
        # print(len(jet_assignments), len(jet_idx), end-start)
        for jet_assignment in jet_assignments:
            tops = {i : [] for i in range(len(event.Tops))}
            for idx in b_idx:
                tops[event.Jets[idx].TopIndex[0]].append(event.Jets[idx])
            for itop, ilep in zip(lep_assignment, lep_idx):
                tops[itop].append(event.TopChildren[ilep])
            for itop, nu in zip(lep_assignment, nu_res):
                tops[itop].append(nu)
            for itop, ijet in zip(jet_assignment, jet_idx):
                if itop != -1:
                    tops[itop].append(event.Jets[ijet])
            if case == 0:
                res_indices = select_resonance_truth(tops, event)
            else:
                res_indices = select_resonance_pt(tops, lep_assignment)
            res_products = []
            for itop in res_indices:
                for item in tops[itop]:
                    res_products.append(item)
            lep_ok = 1
            had_ok = 1
            for itop in res_indices:
                if itop in lep_assignment:
                    for obj in tops[itop]:
                        if type(obj) == type(Children()):
                            if obj.pdgid == 'children_pdgid':
                                continue
                            if obj.TopIndex != itop:
                                lep_ok -= 1
                                break
                        else:
                            if obj.TopIndex[0] != -1 and obj.TopIndex[0] != itop:
                                lep_ok -= 1
                                break
                else:
                    for obj in tops[itop]:
                        if type(obj) == type(Children()):
                            if obj.TopIndex != itop:
                                had_ok -= 1
                                break
                        else:
                            if obj.TopIndex[0] != -1 and obj.TopIndex[0] != itop:
                                had_ok -= 1
                                break

            if case in [0, 1, 2, 3]:
                if len(res_products) == 0:
                    # print('no res products')
                    return None
                return sum(res_products).CalculateMass(), f'{lep_ok}lep{had_ok}had_right'
            else:
                if len(res_products) == 0:
                    # print('no res products')
                    continue
                loss = 0
                for itop in tops:
                    if len(tops[itop]) == 0:
                        b = None
                        w = []
                    elif type(tops[itop][0]) == type(Jet()) and tops[itop][0].btagged:
                        b = tops[itop][0]
                        w = tops[itop][1:]
                    else:
                        b = None
                        w = tops[itop]
                    loss += get_loss(b=b, w=w, alpha=alpha, beta=beta, gamma=gamma)


                losses[loss] = {'m' : sum(res_products).CalculateMass(), 'label' : f'{lep_ok}lep{had_ok}had_right'}
                # print('loss', loss, lep_assignment, {itop : [obj.TopIndex for obj in tops[itop]] for itop in tops})
    if len(losses) == 0:
        # print('no lossess')
        return None
    min_loss = min(losses.keys())
    # print('choosing loss', min_loss)
    return losses[min_loss]['m'], losses[min_loss]['label']
