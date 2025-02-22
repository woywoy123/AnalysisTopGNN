from AnalysisG.Tools import Tools

class DataSets:
    def __init__(self, path = None):
        self.path = path
        self.paths = {}
        self.Mapping = {
                "SM_tttt" : {
                    "412043"
                },
                "tttt_aMcAtNloHerwig7_AFII" : {
                    "412044"
                },
                "tttt_LOInclusive_AFII" : {
                    "500326"
                },
                "tttt_Sh2211" : {
                    "700355"
                },
                "3top" : {
                    "304014"
                },
                "3top_5F" : {
                    "516978"
                },
                "ttW" : {
                    "700000",
                    "700706"
                },
                "ttW_Sh2210" : {
                    "700168"
                },
                "ttW_EWK_Sh2210" : {
                    "700205"
                },
                "ttW_aMcAtNloPy8EG" : {
                    "410155"
                },
                "ttW_MGPy8EG_EWttWsm" : {
                    "525137"
                },
                "ttW_aMCPy8EG_FxFx01jNLO" : {
                    "501720"
                },
                "ttll" : {
                    "410156", "410157", "410218", "410219", "410220", "410276",
                    "410277", "410278"
                },
                "ttll_NLO" : {
                    "504330", "504334", "504342", "504346", "504338"
                },
                "ttll_Sh2211" : {
                    "700309"
                },
                "ttll_Var3cDown" : {
                    "504335", "504343", "504331"
                },
                "ttll_Var3cUp" : {
                    "504332", "504336", "504344"
                },
                "ttll_H7" : {
                    "504329", "504333", "504341", "504337", "504345"
                },
                "ttH" : {
                    "346344","346345"
                },
                "ttH_PhH7EG" : {
                    "602485","602486"
                },
                "ttbar_PhPy8_FS" : {
                    "410470","410472"
                },
                "ttbar_PhPy8_FS_HT_sliced" : {
                    "407342","407343","407344"
                },
                "SingleTop" : {
                    "410658","410659","410644","410645","410646","410647","410560",
                    "410408","512059"
                },
                "ttWW" : {
                    "410081"
                },
                "ttWZ" : {
                    "500463"
                },
                "ttHH" : {
                    "500460"
                },
                "ttWH" : {
                    "500461"
                },
                "ttZZ" : {
                    "500462"
                },
                "Vjets_Sherpa221" : {
                    "364100","364101","364102","364103","364104","364105","364138",
                    "364106","364107","364108","364109","364110","364111","364160",
                    "364112","364113","364114","364115","364116","364117","364168",
                    "364118","364119","364120","364121","364122","364123","364176",
                    "364124","364125","364126","364127","364128","364129","364130",
                    "364131","364132","364133","364134","364135","364136","364137",
                    "364139","364140","364141","364156","364157","364158","364159",
                    "364161","364162","364163","364164","364165","364166","364167",
                    "364169","364170","364171","364172","364173","364174","364175",
                    "364177","364178","364179","364180","364181","364183","364184",
                    "364186","364187","364188","364189","364190","364191","364192",
                    "364194","364196","364197","364198","364199","364200","364201",
                    "364185","364203","364204","364205","364206","364207","364208",
                    "364209","364193","364210","364211","364212","364213","364214",
                    "364215","364202"
                },
                "Vjets_Sherpa_2211" : {
                    "700320","700321","700322","700323","700324","700325","700326",
                    "700327","700328","700329","700330","700331","700332","700333",
                    "700334","700335","700336","700337","700338","700339","700340",
                    "700341","700342","700343","700344","700345","700346","700347",
                    "700348","700349"
                },
                "VH" : {
                    "346646","346647","346645"
                },
                "VV" : {
                    "364250","364253","364254","364255","364283","364284","364285",
                    "364286","364287","364288","364289","364290","345705","345706",
                    "345723","363355","363356","363357","363358","363360","363489"
                },
                "VVV" : {
                    "364242","364243","364244","364245","364246","364247","364248",
                    "364249"
                }
        }

    def CheckThis(self, inpt):
        found = False
        if inpt == "All": return inpt
        if self.path not in self.paths: self.paths[self.path] = Tools().lsFiles(self.path)
        all_ = self.paths[self.path]
        for i, j in self.Mapping.items():
            for pth in all_:
                if inpt not in pth: continue
                for x in j:
                    if x not in pth: continue
                    return i
        return found
