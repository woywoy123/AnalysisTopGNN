from AnalysisG import Analysis
from AnalysisG.Events.Events.CommonSM4topEvent import Event
from Strategy import Common
from AnalysisG.Submission import Condor
from AnalysisG.IO import UnpickleObject
from plotting import PlotEfficiency
import copy
from mtt_reconstruction import MttReconstructor
from Strategy import Common
import uproot
import numpy as np
import os


def submit_jobs():
    # direc = "/home/tnom6927/Downloads/samples/Dilepton/ttH_tttt_m1000"#"/atlasgpfs01/usatlas/data/eleboulicaut/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root"
    root_dir = "/nfs/dust/atlas/user/sitnikov/signal-comparison/common-fw_tag212120/final"
    mc_cpgn = {
                "mc16a" : root_dir + "/mc16a/2lss3lge1DL1r",
                "mc16d" : root_dir + "/mc16d/2lss3lge1DL1r",
                "mc16e" : root_dir + "/mc16e/2lss3lge1DL1r",
                "data"  : root_dir + "/data/2lss3lge1DL1r",
                "QmisID" : root_dir + "/QmisID"
    }
    Quant = 1

    # Create the event cache.
    waitforme = []
    for mc in mc_cpgn:
        Ana = Analysis()
        this_pth = mc_cpgn[mc]
        smpls = Ana.ListFilesInDir(this_pth, ".root")
        Ana = Ana.Quantize(smpls[this_pth], Quant)
        for i in Ana:
            print(i)
            name = f"{mc}_{i[0].split('.')[0]}"
            inner_dirs = os.listdir(f"Analysis_{name}") if os.path.exists(f"Analysis_{name}") else []
            if 'Selections' in inner_dirs or mc != 'QmisID':
                print('Selection is already present, skipping')
                continue
            T = Condor()
            T.ProjectName = f"Analysis_{name}"
            T.PythonVenv = "/nfs/dust/atlas/user/sitnikov/analysistopgnn/setup-scripts/source_this.sh"
            ana = Analysis()
            ana.Event = Event
            ana.EventCache = False
            ana.chnk = 10
            ana.Threads = 12
            ana.InputSample(mc, {this_pth : i})
            ana.AddSelection("bsm", Common)
            ana.MergeSelection("bsm")
            # ana.EventStop = int(ana.chnk * ana.Threads)
            T.AddJob(name, ana, "16GB", "40h")
            T.DumpCondorJobs
            os.system(f'condor_submit Analysis_{name}/CondorDump/{name}/{name}.submit')
            


from AnalysisG.Plotting import TH1F, TH2F, CombineTH1F

def TemplatePlotsTH1F():
    Plots = {
                # "NEvents" : x.NEvents, 
                "ATLASLumi" : 1, 
                "Style" : "ATLAS", 
                "LaTeX": False,
                "OutputDirectory" : "./Figures/", 
                "yTitle" : "Entries (a.u.)", 
                "yMin" : 0, "xMin" : 0
            }
    return Plots

def make_plots():
    import random
    import pandas as pd
    if not os.path.exists('data_frame.pkl'):
        dfs = []
        dirnames = os.listdir()
        for dirname in dirnames:
            if 'Analysis' not in dirname:
                continue
            job_name = dirname.split('_')[1:]
            mc_campaign = job_name[0]
            filename = '_'.join(job_name[1:])
            print(dirname, mc_campaign, filename)
            f = uproot.open(f'fit/mtt_ntuples/{mc_campaign}/{filename}.root')
            data = f['nominal_Loose'].arrays(['jet_isbtagged_DL1r_77', 'mass', 'BSMBDT_1000', 'mcChannelNumber', 'nJets', 'nElectrons', 'nMuons'], library='np')
            isSignal = 'BSM' in filename or 'ttZp' in filename
            dfs.append(pd.DataFrame({
                'filename' : [filename for mass in data['mass']],
                'mass' : data['mass'],
                'mcChannelNumber' : data['mcChannelNumber'],
                'BDT' : data['BSMBDT_1000'],
                'btagged' : data['jet_isbtagged_DL1r_77'],
                'nElectrons' : data['nElectrons'],
                'nMuons' : data['nMuons'],
                'nJets' : data['nJets']
                }))

            dfs

        df = pd.concat(dfs)
        df['isBSM'] = df.apply(lambda x: 'BSM' in x['filename'] or 'ttZp' in x['filename'], axis=1)
        df['isSignal'] = df.apply(lambda x: x['mcChannelNumber'] == 312446 and x['isBSM'], axis=1)
        df['nLeptons'] = df.apply(lambda row: row['nMuons'] + row['nElectrons'], axis=1)
        df['nbJets'] = df.apply(lambda row : sum(row['btagged'], start=0), axis=1)
        df['naddJets'] = df.apply(lambda row : sum([i == 0 for i in row['btagged']], start=0), axis=1)
        df['diff_njets'] = df.apply(lambda row : row['nJets'] - row['nbJets'] - row['naddJets'], axis=1)
        df.to_pickle('data_frame.pkl')
    df = pd.read_pickle('data_frame.pkl')
    df_signal = df.query('isSignal == True')
    df_background = df.query('isBSM == False')
    print(df_signal.shape, df_background.shape)

    
    import plotly.graph_objects as go
    def make_plot(data, xaxis, bins, name):
        fig = go.Figure()
        fig.add_traces([
            go.Histogram(x=data[key]['df'][data[key]['column_name']], name=f'{key} {len(data[key]["df"][data[key]["column_name"]])}') for key in data
            ])
        fig.update_layout(barmode='overlay', xaxis_title_text=xaxis)
        fig.update_traces(opacity=0.75, histnorm='percent', xbins=bins)
        fig.write_image(f'Plots/{name}')

    def make_multiple_plots(df_background, df_signal, suffix):
        make_plot(
            {
            'Background' : {'df' : df_background, 'column_name' : 'BDT'},
            'Signal' : {'df' : df_signal, 'column_name' : 'BDT'}
            },
            'BSMBDT_1000',
            {'start' : 0, 'end' : 1, 'size' : 0.01},
            f'BDT_{suffix}.png'
            )
        make_plot(
            {
            'Background' : {'df' : df_background, 'column_name' : 'mass'},
            'Signal' : {'df' : df_signal, 'column_name' : 'mass'}
            },
            'resonancce mass, GeV',
            {'start' : 0, 'end' : 2000, 'size' : 50},
            f'resonance_mass_{suffix}.png'
            )
        make_plot(
            {
            'Background' : {'df' : df_background, 'column_name' : 'nJets'},
            'Signal' : {'df' : df_signal, 'column_name' : 'nJets'}
            },
            'number of jets',
            {'start' : 0, 'end' : 15, 'size' : 1},
            f'njets_{suffix}.png'
            )
        make_plot(
            {
            'Background' : {'df' : df_background, 'column_name' : 'nbJets'},
            'Signal' : {'df' : df_signal, 'column_name' : 'nbJets'}
            },
            'number of b-jets',
            {'start' : 0, 'end' : 10, 'size' : 1},
            f'nbjets_{suffix}.png'
            )
        make_plot(
            {
            'Background' : {'df' : df_background, 'column_name' : 'naddJets'},
            'Signal' : {'df' : df_signal, 'column_name' : 'naddJets'}
            },
            'number of non-b-jets',
            {'start' : 0, 'end' : 10, 'size' : 1},
            f'naddjets_{suffix}.png'
            )
        make_plot(
            {
            'Background' : {'df' : df_background, 'column_name' : 'nLeptons'},
            'Signal' : {'df' : df_signal, 'column_name' : 'nLeptons'}
            },
            'number of leptons',
            {'start' : 0, 'end' : 10, 'size' : 1},
            f'nleptons_{suffix}.png'
            )

    make_multiple_plots(df_background, df_signal, 'nocut')

    df_signal_new = df_signal.query(f'mass != 0')
    df_background_new = df_background.query(f'mass != 0')
    make_multiple_plots(df_background_new, df_signal_new, 'nocut_no0')

    cut_BDT = 0.7
    df_signal_new = df_signal.query(f'BDT > {cut_BDT}')
    df_background_new = df_background.query(f'BDT > {cut_BDT}')
    make_multiple_plots(df_background_new, df_signal_new, 'cut07')

    df_signal_new = df_signal_new.query(f'mass != 0')
    df_background_new = df_background_new.query(f'mass !=0')
    make_multiple_plots(df_background_new, df_signal_new, 'cut07_no0')




def process():
    count_no_selection = 0
    dirnames = os.listdir()
    no_selection = []
    if not os.path.exists('mtt_ntuples'):
        os.makedirs('mtt_ntuples')
    for dirname in dirnames:
        if 'Analysis' not in dirname:
            continue
        anapath = dirname
        # if os.path.exists(f'{dirname}/CondorDump/{dirname}'):
        #     anapath = f'{dirname}/CondorDump/{dirname}'
        # else:
        #     anapath  = dirname
        inner_dirs = os.listdir(anapath)
        if 'Selections' not in inner_dirs:
            print(dirname, 'no selection')
            count_no_selection += 1
            no_selection.append(dirname)
            continue
        # if not os.path.exists(f'{dirname}/Selections/Merged'):
        #     print(dirname, 'no merged')
        #     continue
        # continue
        jobname = '_'.join(dirname.split('_')[1:])
        print(dirname, jobname)
        is_merged = os.path.exists(f'{anapath}/Selections/Merged/bsm.pkl')
        if not is_merged:
            mrg = Analysis()
            mrg.MergeSelection("bsm1")
            mrg.ProjectName = anapath
            mrg.Threads = 5
            mrg.Launch
        # filenames = os.listdira('Analysis/CondorDump/Analysis/Selections/bsm')
        # for filename in filenames:
        is_merged = os.path.exists(f'{anapath}/Selections/Merged/bsm.pkl')
        if not is_merged:
            print('OOPS could not merge the selection')
            count_no_selection += 1
            continue
        x = UnpickleObject(f"{anapath}/Selections/Merged/bsm")
        print(x.CutFlow)
        data = {'runNumber1' : [], 'eventNumber1' : [], 'mass' : []}
        with open(f'fit/txt_files/{jobname}.root.txt', 'r') as f:
            for line in f.readlines():
                items = line[:-1].split(' ');
                data['runNumber1'].append(int(items[0]))
                data['eventNumber1'].append(int(items[1]))
                data['mass'].append(0)
        
        for ROOTName in x.masses:
            # print(ROOTName)
            filename = ROOTName.split('/')[-1]
            if 'mc16a' in ROOTName:
                dir = 'mc16a'
            elif 'mc16e' in ROOTName:
                dir = 'mc16e'
            elif 'mc16d' in ROOTName:
                dir = 'mc16d'
            elif 'data' in ROOTName:
                dir = 'data'
            elif 'QmisID' in ROOTName:
                dir = 'QmisID'
            else:
                dir = ''
            if not os.path.exists('mtt_ntuples/' + dir):
                os.makedirs('mtt_ntuples/' + dir)
            rn_en = {}
            for i in range(len(x.masses[ROOTName])):
                rn = x.runNumbers[ROOTName][i]
                en = x.eventNumbers[ROOTName][i]
                if rn not in rn_en:
                    rn_en[rn] = {}
                rn_en[rn][en] = i
            for i in range(len(data['runNumber1'])):
                try:
                    rn = data['runNumber1'][i]
                    en = data['eventNumber1'][i]
                    data['mass'][i] = x.masses[ROOTName][rn_en[rn][en]]*0.001
                except KeyError:
                    pass
            with uproot.recreate(f'mtt_ntuples/{dir}/{filename}') as file:
                file['tree'] = data
                #file['tree'] = {'mass' : [mass/1000 for mass in x.masses[ROOTName]], 'eventNumber' : x.eventNumbers[ROOTName], 'runNumber' : x.runNumbers[ROOTName], 'mcChannelNumber' : x.mcChannelNumbers[ROOTName]}
            
    print(count_no_selection, 'no selections')
    for i in no_selection:
        print(i)


make_plots()
# submit_jobs()
#process()





# for y in x.masses['Jet'][9]:
#     print(y)

# print(x._CutFlow)
# print(x._Residual)
# print(x._TimeStats)
# import json
# print(json.dumps(x.masses, indent=1))
# print(Ana[x._hash[0]]) #< returns the event of this given hash.

# PlotEfficiency(x, "case")
# PlotEfficiency(x, "object")
# out_string = ""
# for object_type in x.efficiency_avg.keys():
#     for case_num in x.efficiency_avg[object_type].keys():
#         for method in x.efficiency_avg[object_type][case_num].keys():
#             out_string += f"Average event efficiency for object type {object_type}, case {case_num}, method {method} is {sum(x.efficiency_avg[object_type][case_num][method]) / len(x.efficiency_avg[object_type][case_num][method])}\n"

# print(out_string)
# f = open("avg_efficiencies.txt", "w")
# f.write(out_string)
# f.close()
                


# Here is an example Condor Submission scripter. Basically remove Ana.Launch() to compile this.
#T = Condor()
#T.ProjectName = "Analysis"
#T.CondaEnv = None 
#T.PythonVenv = "/nfs/dust/atlas/user/sitnikov/analysistopgnn/setup-scripts/source_this.sh"
#T.AddJob("bsm-1000", Ana, memory = None, time = None)
#T.DumpCondorJobs
# T.TestCondorShell
#T.SubmitToCondor
# T.LocalDryRun()
