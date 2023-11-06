from AnalysisG.IO import UpROOT
import uproot
import numpy as np

root1 = "./samples/sample1/smpl1.root"
root2 = "./samples/sample1/smpl2.root"


def test_uproot_read():
    io = UpROOT([root1, root2])
    io.Trees = ["nominal", "nominal-1"]
    io.Branches = ["children_index", "hello"]
    io.Leaves = ["children_index", "nothing"]
    io.ScanKeys()

    root1_, root2_ = list(io.Keys)
    assert "nominal-1" in io.Keys[root1_]["missed"]["Trees"]
    assert "nominal-1" in io.Keys[root2_]["missed"]["Trees"]

    assert "hello" in io.Keys[root1_]["missed"]["Branches"]
    assert "hello" in io.Keys[root2_]["missed"]["Branches"]

    assert "nothing" in io.Keys[root1_]["missed"]["Leaves"]
    assert "nothing" in io.Keys[root2_]["missed"]["Leaves"]

    io = UpROOT([root1, root2])
    io.Trees = ["nominal"]
    io.Branches = ["children_index"]
    io.Leaves = ["met_met"]
    assert len(io) == 165

    io = UpROOT([root1, root2])
    io.Trees = ["nominal", "truth"]
    io.Leaves = ["weight_mc", "weight_pileup", "met_phi"]

    len_nom, len_truth = 0, 0
    for i in io:
        if "truth/weight_mc" in i:
            assert "truth/weight_mc" in i
            assert "truth/weight_pileup" in i
            assert "truth/met_phi" not in i
            len_truth += 1
        if "nominal/weight_mc" in i:
            assert "nominal/weight_mc" in i
            assert "nominal/weight_pileup" in i
            assert "nominal/met_phi" in i
            len_nom += 1
    assert len_truth == 2000
    assert len_nom == 165

if __name__ == "__main__":
    test_uproot_read()
    pass
