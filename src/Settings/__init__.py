from subprocess import Popen, PIPE, STDOUT
from AnalysisG.Tools import Tools
from threading import Thread
from pwinput import pwinput
import subprocess
import pathlib
import sys

def _getcmd(cmd):

    return subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True).decode(
        "UTF-8"
    )


def CONFIG_PYAMI():
    print("------- CONFIGURING PYAMI -------")
    print(_getcmd('echo "y" | ami_atlas_post_install'))
    print("-------- FINISHED PYAMI ---------")

def AUTH_PYAMI():
    print("Please specify the directory where your .globus directory is located.")
    globu = input("(default: ~/.globus): ")
    globu = "~/.globus/" if globu == "" else globu
    print("Provide the password to decrypt the PEM files. Leave blank and press enter for no password.")
    execute = " ".join(["voms-proxy-init", "-certdir", globu, "-pwstdin"])
    code = pwinput("Password: ")
    execute = 'echo "' + code + '" | ' + execute
    try: _getcmd(execute)
    except subprocess.CalledProcessError: pass

    test = ["ami_atlas", "show", "dataset", "info", "data13_2p76TeV.00219364.physics_MinBias.merge.NTUP_HI.f519_m1313"]
    if "logicalDatasetName" in _getcmd(" ".join(test)): return print("SUCCESS!!!")
    print("Incorrect permissions on your .pem files.")
    print("Try the following:")
    print("-> chmod -R a+rwX <your .pem directory> #<- this will give everyone access to the .pem!")
    print("The commands below will fix the global access issue.")
    print("-> chmod 0600 <directory>/usercert.pem")
    print("-> chmod 0400 <directory>/userkey.pem")


def POST_INSTALL_PYC():
    def stdout():
        for line in p.stdout: print(line.decode("UTF-8").replace("\n", ""))

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

def make_analysis():
    tool = Tools()
    this_dir = tool.pwd()
    tool.mkdir("Analysis")
    tool.mkdir("Analysis/Objects")

    event = [
            "from AnalysisG.Templates import EventTemplate",
            "from Particles import MyParticle", 
            "",
            "class MyEvent(EventTemplate):",
            "",
            "   def __init__(self)",
            "       EventTemplate.__init__(self)",
            "       self.Objects = {'SomeParticle' : MyParticle}",
            "       self.Trees = ['<some tree>']",
            "       self.Branches = ['<some branches (optional)>']",
            "       self.index = '<some index leaf name>'",
            "       self.CommitHash = '<some hash (optional)>'",
            "",
            "   def CompileEvent(self):",
            "",
            "       # add some matching logic (optional)",
            "       #print the particles in this event",
            "       print(self.SomeParticle)",
    ]

    f = open(this_dir + "/Analysis/Objects/Event.py", "w")
    f.write("\n".join(event))
    f.close()

    particle = [
            "from AnalysisG.Templates import ParticleTemplate",
            "",
            "class MyParticle(ParticleTemplate):",
            "",
            "   def __init__(self):",
            "       ParticleTemplate.__init__(self)",
            "       self.Type = 'some particle type'",
            "       self.pt = self.Type  + '_' + <ROOT leaf string>",
            "       self.eta = self.Type + '_' + <ROOT leaf string>",
            "       self.phi = self.Type + '_' + <ROOT leaf string>",
            "       self.e   = self.Type + '_' + <ROOT leaf string>",
    ]

    f = open(this_dir + "/Analysis/Objects/Particles.py", "w")
    f.write("\n".join(particle))
    f.close()


    graph = [
            "from AnalysisG.Templates import GraphTemplate",
            "",
            "class MyGraph(GraphTemplate):",
            "",
            "   def __init__(self, Event = None):",
            "       GraphTemplate.__init__(self)",
            "       self.Event = Event",
            "       self.Particles += self.Event.SomeParticle",
    ]

    f = open(this_dir + "/Analysis/Objects/Graph.py", "w")
    f.write("\n".join(graph))
    f.close()

    selection = [
            "from AnalysisG.Templates import SelectionTemplate",
            "",
            "class Selection(SelectionTemplate):",
            "",
            "   def __init__(self, Event = None):",
            "       SelectionTemplate.__init__(self)",
            "       self.SomeDictionary = {}",
            "       self.SomeList = []",
            "",
            "   def Selection(self, event):",
            "       return True",
            "",
            "   def Strategy(self, event):",
            "       pass"
    ]

    f = open(this_dir + "/Analysis/Objects/Selection.py", "w")
    f.write("\n".join(selection))
    f.close()

    analysis = [
            "from AnalysisG import Analysis",
            "from Objects.Event import MyEvent",
            "from Objects.Graph import MyGraph", 
            "",
            "Ana = Analysis()",
            "Ana.Event = MyEvent", 
            "Ana.Graph = MyGraph", 
            "Ana.EventCache = True # Creates hdf5 files", 
            "Ana.DataCache = True # Creates hdf5 files for graphs", 
            "Ana.Launch()"
    ]

    f = open(this_dir + "/Analysis/main.py", "w")
    f.write("\n".join(analysis))
    f.close()
