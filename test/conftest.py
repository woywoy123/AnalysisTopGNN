import pytest
import shutil
import os


@pytest.fixture(autouse=True)
def change_test_dir(request):
    os.chdir(request.fspath.dirname)
    yield
    os.chdir(request.config.invocation_params.dir)


def clean_dir():
    lst = [
        "UNTITLED",
        "_Project",
        "Project",
        "tmp",
        "_Test",
        "Project_ML",
        "TestFeature",
        "TestOptimizer",
        "TestOptimizerAnalysis",
        "jets",
        "events",
        "NeutrinoProject",
        "Plots",
    ]
    for i in lst:
        try:
            shutil.rmtree(i)
        except:
            pass
