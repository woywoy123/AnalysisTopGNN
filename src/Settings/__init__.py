from .Settings import Settings


def _getcmd(cmd):
    import subprocess

    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode(
        "UTF-8"
    )


def CONFIG_PYAMI():
    print("------- CONFIGURING PYAMI -------")
    print(_getcmd('echo "y" | ami_atlas_post_install'))
    print("-------- FINISHED PYAMI ---------")


def POST_INSTALL_PYTORCH():
    print(_getcmd("pip install torch"))

    try:
        cu = "cu" + _getcmd("python -c 'import torch; print(torch.version.cuda)'")
        avail = _getcmd("python -c 'import torch; print(torch.cuda.is_available())'")
        ver = _getcmd("python -c 'import torch; print(torch.version.__version__)'")
    except:
        cu = "cu" + _getcmd("python3 -c 'import torch; print(torch.version.cuda)'")
        avail = _getcmd("python3 -c 'import torch; print(torch.cuda.is_available())'")
        ver = _getcmd("python3 -c 'import torch; print(torch.version.__version__)'")

    cu = cu.replace(".", "").replace("\n", "")
    avail = bool(avail.replace("\n", ""))
    ver = ver.split("+")[0]
    if not avail:
        cu = "cpu"
    if "2.0" not in ver:
        ver = "1.13.0"
    else:
        ver = "2.0.0"
    return ver + "+" + cu


def POST_INSTALL_PYG(device=""):
    _pkgs = [
        "pyg_lib",
        "torch_scatter",
        "torch_sparse",
        "torch_cluster",
        "torch_spline_conv",
    ]
    _torch = (
        "pip install "
        + " ".join(_pkgs)
        + " -f https://data.pyg.org/whl/torch-"
        + device
        + ".html"
    )

    print(_getcmd(_torch))
    print(_getcmd("pip install torch_geometric"))


def POST_INSTALL_PYC():
    def stdout():
        for line in p.stdout:
            print(line.decode("UTF-8").replace("\n", ""))

    import subprocess
    import sys
    from threading import Thread
    import pathlib

    print("------- CONFIGURING TORCH-EXTENSIONS (PYC) -------")
    p = subprocess.Popen(
        [sys.executable, "-m", "pip", "install", "-v", "./torch-extensions/"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    t = Thread(target=stdout, daemon=True)
    t.start()
    t.join()
    print("------- DONE CONFIGURING TORCH-EXTENSIONS (PYC) -------")


def CHECK_CUDA():
    print("------- CONFIGURING PYTORCH -------")
    cu = POST_INSTALL_PYTORCH()
    print("-------- FINISHED PYTORCH ---------")

    print("------- CONFIGURING PYG -------")
    print("+++++> Suggested Installer: " + cu)
    POST_INSTALL_PYG(cu)
    print("-------- FINISHED PYG ---------")
