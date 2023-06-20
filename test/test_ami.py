from AnalysisG.IO import UpROOT
from conftest import clean_dir


def test_pyami():
    smpl = UpROOT("samples/dilepton/")
    meta = smpl.GetAmiMeta
    assert len(meta) == 1
    f = next(iter(meta))
    assert meta[f].isMC
    assert len(meta[f].Files) == 1
    try:
        assert meta[f].cross_section
    except AttributeError:
        pass
    try:
        assert meta[f].DatasetName
    except AttributeError:
        pass
    smpl.Trees = ["nominal"]
    smpl.Leaves = ["weight_mc"]

    f = "mc16_13TeV.312446.MadGraphPythia8EvtGen_noallhad_ttH_tttt_m1000"
    for i in smpl:
        assert f in i["MetaData"].Files[0][0]
    clean_dir()


def test_ami_injection():
    smpl = UpROOT("samples/dilepton/")
    smpl.Trees = ["nominal"]
    smpl.Leaves = ["weight_mc", "eventNumber"]

    lst = []
    for i in smpl:
        meta = i["MetaData"]
        assert "dilepton" not in meta.GetDAOD(i["nominal/eventNumber"])[0]
    clean_dir()


if __name__ == "__main__":
    test_pyami()
    test_ami_injection()
    pass
