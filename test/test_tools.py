from AnalysisG.Tools import Hash, Tools, Code
from AnalysisG.IO import PickleObject, UnpickleObject

directory = "./samples/test/"


def test_hash():
    assert Hash("test") == "0xd1d16a4a0a7a19fb"


def test_pickle():
    x = {"...": ["test"]}
    PickleObject(x, "Test")
    p = UnpickleObject("Test")
    assert x == p
    T = Tools()
    T.rm("./_Pickle")


def test_merge_data():
    x1 = {"All": [2], "a": 1, "b": {"test1": 0}}
    x2 = {"All": [1], "a": 2, "b": {"test2": 0}}
    x_t = {"All": [2, 1], "a": 3, "b": {"test1": 0, "test2": 0}}
    T = Tools()
    out = T.MergeData(x1, x2)
    assert out == x_t

    x1 = {"a": 1, "b": {"test1": 0}}
    x2 = {"All": [1], "a": 2, "b": {"test2": 0}}
    x_t = {"All": [1], "a": 3, "b": {"test1": 0, "test2": 0}}
    T = Tools()
    out = T.MergeData(x1, x2)
    assert x_t == out


def test_ls_files():
    I = Tools()
    F = I.lsFiles(directory)
    for i in range(3):
        assert directory + "Dir" + str(i + 1) in F
    assert len(I.lsFiles(directory + "Dir1", ".txt")) == 3


def test_ls():
    I = Tools()
    F = I.lsFiles(directory)
    for i in range(3):
        assert directory + "Dir" + str(i + 1) in F
    if I.ls("FakeDirectory") != []:
        return False


def test_is_file():
    I = Tools()
    for i in range(3):
        assert (
            I.IsFile(directory + "Dir" + str(i + 1) + "/" + str(i + 1) + ".txt") == True
        )
    assert I.IsFile(directory + "Dir1") == False


def test_list_files_in_dir():
    D = {
        directory + "/Dir1": ["1.txt"],
        directory + "/Dir2": "2.txt",
        directory + "/Dir3/": "*",
    }
    I = Tools()
    O = I.ListFilesInDir(D, ".txt")
    assert "1.txt" in O[I.abs(directory + "/Dir1")]
    assert "2.txt" in O[I.abs(directory + "/Dir2")]
    assert "1.txt" in O[I.abs(directory + "/Dir3")]
    assert "2.txt" in O[I.abs(directory + "/Dir3")]
    assert "3.txt" in O[I.abs(directory + "/Dir3")]


class HelloWorld:
    def __init__(self, hello, world="world"):
        pass

    def Test(self):
        return True


def test_source_code_extraction():
    H = HelloWorld("H")
    assert "HelloWorld" in Code(H)._Name
    assert Code(H)._FileCode == "".join(open("./test_tools.py", "r").readlines())


def test_data_merging():
    T = Tools()
    d = {
        "1": [["1", "2"], ["3", "4"], ["5", "6"], [["2"]]],
        "2": ["5", "6"],
        "3": [["1", "2"], ["3", "4"]],
    }
    assert T.MergeListsInDict(d) == [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "2",
        "5",
        "6",
        "1",
        "2",
        "3",
        "4",
    ]
    l = [["1", "2"], ["3", "4"], ["5", "6"], [["2"]]]
    assert T.MergeNestedList(l) == ["1", "2", "3", "4", "5", "6", "2"]


if __name__ == "__main__":
    # test_hash()
    # test_pickle()
    test_merge_data()
    test_data_merging()
    # test_ls_files()
    # test_is_file()
    # test_list_files_in_dir()
    # test_source_code_extraction()
