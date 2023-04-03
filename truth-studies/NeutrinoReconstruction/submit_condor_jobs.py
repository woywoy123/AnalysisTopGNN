import os

common_dir = '/eos/home-t/tnommens/Processed/Dilepton/ttH_tttt_m1000'

files = os.listdir(common_dir)

for filename in files:
    with open('condor/submission.sub', 'w') as file:
        file.write(f'cwd = /eos/user/e/elebouli/BSM4tops/FourTopsAnalysis/models_save/NeutrinoReconstruction\n')
        file.write(f'executable = $(cwd)/condor/execute_job.sh\n')
        file.write(f'arguments = {common_dir}/{filename}\n')
        file.write(f'output = $(cwd)/condor/output/{filename}.out\n')
        file.write(f'error = $(cwd)/condor/error/{filename}.err\n')
        file.write(f'log = $(cwd)/condor/log/{filename}.log\n')
        file.write(f'initialdir = $(cwd)\n')
        file.write('should_transfer_files = YES\n')
        file.write('when_to_transfer_output = ON_EXIT\n')
        file.write(f'transfer_output_remaps = "mtt_data.pkl = condor/mtt_data/{filename}.pkl"\n')
        file.write('+JobFlavour = "tomorrow"\n')
        file.write('queue\n')
    os.system('condor_submit condor/submission.sub')

