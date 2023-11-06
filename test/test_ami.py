from AnalysisG.IO import UpROOT
import uproot

def test_pyami():

    smpl = UpROOT("samples/dilepton/")
    smpl.Trees = ["nominal"]
    smpl.Leaves = ["weight_mc"]
    smpl.ScanKeys()
    smpl.EnablePyAMI = False
    assert len(smpl) == 1098
    meta = smpl.GetAmiMeta()
    assert len(meta) == 1
    f = next(iter(meta))
    assert meta[f].isMC
    assert len(meta[f].Files) == 1

    data = "mc16_13TeV.312446.MadGraphPythia8EvtGen_noallhad_ttH_tttt_m1000"
    assert meta[f].crossSection >= 0
    assert data in meta[f].DatasetName

    assert len([i for i in smpl]) > 0
    for i in smpl:
        assert data in i["MetaData"].DatasetName


def test_ami_injection():
    smpl = UpROOT("samples/dilepton/")
    smpl.Trees = ["nominal"]
    smpl.Leaves = ["weight_mc", "eventNumber"]
    smpl.StepSize = 10
    file = {"samples/dilepton/DAOD_TOPQ1.21955717._000001.root" : "nominal"}
    inst = { "files" : file, "step_size" : 10000, "library" : "np", "how" : dict}
    inst["expressions"] = ["weight_mc", "eventNumber"]
    x = next(uproot.iterate(**inst))
    x = {key : x[key].tolist() for key in x}
    assert len(x["weight_mc"]) == len(smpl)

    lst = []
    for i in smpl:
        meta = i["MetaData"]
        evnt = i["EventIndex"]
        evnt_nr = i["nominal/eventNumber"]
        assert evnt_nr == x["eventNumber"][evnt]
        assert "dilepton" not in meta.IndexToSample(i["nominal/eventNumber"])
        lst.append(1)
    assert len(lst) == len(smpl)

if __name__ == "__main__":
    test_pyami()
    test_ami_injection()
    pass
