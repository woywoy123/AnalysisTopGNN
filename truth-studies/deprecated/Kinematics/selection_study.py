from AnalysisTopGNN.Generators import Analysis
from AnalysisTopGNN.Events import Event
from TruthTops import *
from TopChildren import *
from TruthMatching import *
from mtt_study import *
import plotly.express as px
# from Event import Event
common_dir = '/nfs/dust/atlas/user/sitnikov/ntuples_for_classifier'
samples = {'mc16d' : 'user.tnommens.312446.MadGraphPythia8EvtGen.DAOD_TOPQ1.e7743_a875_r10201_p4031.bsm4t-GNN-bsmh-mcd_output_root', 'mc16e' : 'user.tnommens.312446.MadGraphPythia8EvtGen.DAOD_TOPQ1.e7743_a875_r10724_p4031.bsm4t-GNN-bsmh-mce_output_root', 'mc16a' : 'user.tnommens.312446.MadGraphPythia8EvtGen.DAOD_TOPQ1.e7743_a875_r9364_p4031.bsm4t-GNN-bsmh-mca_output_root'}

Ana = Analysis()
for sample in samples:
    Ana.InputSample(sample, common_dir + '/' + samples[sample])
# Ana.InputSample("tttt", direc)
Ana.Event = Event
# Ana.EventStop = 100
# Ana.chnk = 100
Ana.EventCache = True
Ana.DumpPickle = True
Ana.Launch()
#
# 0. there are exactly 4 tops
# 1. all tops decay either hadronically (only quarks) or leptonically (e or mu) - this gets rid of all taus and maybe some other stuff
# 2. there are exactly 2 had tops and 2 lep tops
# 3. one had top and one lep top are from resonance
# 4. All truthjets are matched to 1 or 0 tops
# 5. exactly 1 truthjet is matched to lep tops
# 6. All had tops have at least 1 truthjet matched to them


truthjet_count = 0
loss = {i : 0 for i in range(7)}
loss_tom = {i : 0 for i in range(7)}
lep_ids = [11, 12, 13, 14]
had_ids = [i for i in range(1, 10)]
accept_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
n_diff = 0
tom_5_alt_loss = 0

for i in Ana:
    event = i.Trees['nominal']
    truthjet_count += len(event.TruthJets)
    if len(event.Tops) != 4:
        loss[0] += 1
        loss_tom[1] +=1

    # Tom's code
    C1_fail = False
    stringR = {"Lep" : [], "Had" : []}
    for t in event.Tops:
        if len([k.pdgid for k in t.Children if abs(k.pdgid) not in accept_ids]) > 0:
            C1_fail = True
            continue
        lp = "Lep" if sum([1 for k in t.Children if abs(k.pdgid) in lep_ids]) > 0 else "Had"
        stringR[lp].append(t)
    nlep_tom = len(stringR["Lep"])
    if C1_fail:
        loss_tom[1] += 1
    if len([1 for k in stringR if len(stringR[k]) != 2]) > 0:
        loss_tom[2] += 1
    res = {k : t for k in stringR for t in stringR[k] if t.FromRes == 1}
    if len(res) != 2:
        loss_tom[3] += 1
    if len([1 for tj in event.TruthJets if len(tj.Tops) > 1]):
        loss_tom[4] += 1
    if "Lep" not in res or len(res["Lep"].TruthJets) != 1:
        loss_tom[5] += 1
    if len([1 for t in stringR["Lep"] if len(t.TruthJets) != 1]) != 0:
        tom_5_alt_loss += 1
    if len([1 for t in stringR["Had"] if len(t.TruthJets) == 0]) != 0:
        loss_tom[6] += 1


    # My code

    lep_tops = []
    had_tops = []
    res_lep = 0
    res_had = 0
    for itop, top in enumerate(event.Tops):
        pdgids = [abs(child.pdgid) for child in top.Children]
        if sum([1 for pdgid in pdgids if pdgid not in accept_ids]) != 0:
            continue
        if sum([1 for pdgid in pdgids if pdgid in lep_ids]) != 0:
            lep_tops.append(top)
            if top.FromRes:
                res_lep += 1
        if sum([1 for pdgid in pdgids if pdgid in had_ids]) == len(top.Children):
            had_tops.append(top)
            if top.FromRes:
                res_had += 1
    nlep_me = len(lep_tops)
    if len(lep_tops) + len(had_tops) != len(event.Tops):
        loss[1] += 1
    if len(lep_tops) != 2 or len(had_tops) != 2:
        loss[2] += 1
    if res_lep != 1 or res_had != 1:
        loss[3] += 1
    merged_truthjets = [1 for truthjet in event.TruthJets if len(truthjet.index) != 1]
    if len(merged_truthjets) != 0:
        loss[4] += 1
    if sum([1 for top in lep_tops if len(top.TruthJets) != 1]) != 0:
        loss[5] += 1
    if sum([1 for top in had_tops if len(top.TruthJets) == 0]) != 0:
        loss[6] += 1

    # is_break = False
    # if nlep_me != nlep_tom:
    #     n_diff += 1
    #     print(nlep_me, nlep_tom)
    #     for top in event.Tops:
    #         print([child.pdgid for child in top.Children])
    #     is_break = True
    # if is_break:
    #     break


print(truthjet_count, 'truthjets')
print('me', loss)
print('tom', loss_tom)
print('lat 5 loss', tom_5_alt_loss)
print(f'in {n_diff} cases nlep is different')
