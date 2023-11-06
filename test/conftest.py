import pytest
import os

@pytest.fixture(autouse=True)
def change_test_dir(request):
    os.chdir(request.fspath.dirname)
    yield
    os.chdir(request.config.invocation_params.dir)
