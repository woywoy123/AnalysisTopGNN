from .Notification import Notification
import sys


class _FeatureAnalysis(Notification):
    def __init__(self):
        pass

    def FeatureFailure(self, name, mode, EventIndex):
        fail = str(sys.exc_info()[1]).replace("'", "").split(" ")
        self.Failure(
            "(" + mode + "): " + name + " ERROR -> " + " ".join(fail) + EventIndex
        )

    def TotalFailure(self):
        string = "Feature failures detected... Exiting"
        self.Failure("=" * len(string))
        self.Failure(string)
        return self.Failure("=" * len(string))

    def PassedTest(self, name, mode):
        self.Success("!!!(" + mode + ") Passed: " + name)
