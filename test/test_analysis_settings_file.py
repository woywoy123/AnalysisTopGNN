from AnalysisG.Generators import Analysis 
import json 
import shutil
import os

def dump_settings_file(settings):
    with open('test_settings.json', 'w') as settings_file:
        settings_file.write(json.dumps(settings, indent=1))

def delete_created_files():
    try:
        os.remove('test_settings.json')
        shutil.rmtree('TestProject')
    except:
        pass

def get_working_settings():
    settings = {
            'ProjectName' : 'TestProject',
            'OutputDirectory' : './',
            'EventCache' : False,
            'EventStop' : 1,
            'wrong_parameter' : None,
            'InputSample' : ['name', "/nfs/dust/atlas/user/sitnikov/ntuples_for_classifier/ttH_tttt_m1000/DAOD_TOPQ1.21955717._000001.root"],
            'Event' : 'Event',
            'AddSelection' : ['bsm', 'Common'],
            'MergeSelection' : 'bsm',
            'include' : {
                'paths' : ['/nfs/dust/atlas/user/sitnikov/analysistopgnn/signal-reconstruction'],
                'modules' : [{
                        'module_name' : 'AnalysisG.Events.Events.Event',
                        'class_name' : 'Event'
                    },
                    {
                        'module_name' : 'Strategy',
                        'class_name' : 'Common'
                    }
                    ]
            }
        }
    return settings 

def test_loading_working_settings():
    settings = get_working_settings()
    dump_settings_file(settings)
    Ana = Analysis()
    result = Ana.ReadSettings('test_settings.json')
    assert result 
    for key in settings:
        if key in ['include', 'AddSelection', 'MergeSelection', 'InputSample', 'Event']:
            continue 
        assert getattr(Ana, key) == settings[key]
    delete_created_files()

def test_loading_not_working_settings():
    settings = get_working_settings()
    settings['Event'] = 'NonExistingClass'
    dump_settings_file(settings)
    Ana = Analysis()
    settings['include']['modules'][0]['class_name'] = 'NonExistingClass'
    dump_settings_file(settings)
    assert not Ana.ReadSettings('test_settings.json')
    settings = get_working_settings()
    settings['include']['modules'][0]['module_name'] = 'NonExistingModule'
    dump_settings_file(settings)
    assert not Ana.ReadSettings('test_settings.json')
    settings = get_working_settings()
    settings['Event'] = 'NonExistingClass'
    dump_settings_file(settings)
    assert not Ana.ReadSettings('test_settings.json')

if __name__ == "__main__":
    test_loading_working_settings()
    test_loading_not_working_settings()
