from AnalysisTopGNN.Tools import Tools

directory = "./TestCaseFiles/Tools/TestFiles/"
def test_ls_files():
    I = Tools()
    print("Testing listing sub-directories...")
    F = I.lsFiles(directory)
    for i in range(3):
        assert directory + "Dir" + str(i+1) in F
    print("Testing listing files with extension .txt")
    assert len(I.lsFiles(directory + "Dir1", ".txt")) == 3

def test_ls():
    I = Tools()
    print("Testing listing directories")
    F = I.lsFiles(directory)
    for i in range(3):
        assert directory + "Dir" + str(i+1) in F
    if I.ls("FakeDirectory") != []:
        return False

def test_is_file():
    I = Tools()
    for i in range(3):
        assert I.IsFile(directory + "Dir" + str(i+1) + "/" + str(i+1) + ".txt") == True
    assert I.IsFile(directory + "Dir1") == False

def test_list_files_in_dir():
    D = {directory + "/Dir1" : ["1.txt"], directory + "/Dir2" : "2.txt", directory + "/Dir3/" : "*"}
    I = Tools()
    O = I.ListFilesInDir(D, ".txt")
    assert "1.txt" in O[I.abs(directory + "/Dir1")]
    assert "2.txt" in O[I.abs(directory + "/Dir2")]
    assert "1.txt" in O[I.abs(directory + "/Dir3")]
    assert "2.txt" in O[I.abs(directory + "/Dir3")]
    assert "3.txt" in O[I.abs(directory + "/Dir3")]

def test_source_code_extraction():

    class HelloWorld:
        def __init__(self, hello, world = "world"):
            pass
        
        def Test(self):
            return True

    T = Tools()
    H = HelloWorld("H")
    assert "HelloWorld" in T.GetSourceCode(H) and "AnalysisTopGNN" not in T.GetSourceCode(H)
    assert T.GetSourceFile(H) == "".join(open("./test_io.py", "r").readlines())

def test_data_merging():
    
    T = Tools()
    d = {"1": [["1", "2"], ["3", "4"], ["5", "6"], [["2"]]], "2": ["5", "6"], "3": [["1", "2"], ["3", "4"]]}
    assert T.MergeListsInDict(d) == ["1", "2", "3", "4", "5", "6", "2", "5", "6", "1", "2", "3", "4"]
    l = [["1", "2"], ["3", "4"], ["5", "6"], [["2"]]]
    assert T.MergeNestedList(l) == ["1", "2", "3", "4", "5", "6", "2"]
