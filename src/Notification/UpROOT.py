from .Notification import Notification


class _UpROOT(Notification):
    def __init__(self):
        pass

    def InvalidROOTFileInput(self):
        self.Failure("Invalid Input. Provide either a string/list of ROOT file/s")

    def FailedAMI(self):
        self.Warning("PyAMI not available... Skipping...")

    def NoVOMSAuth(self):
        self.Failure(
            "No VOMS session was found. Make sure you authenticate. Skipping MetaData"
        )

    def FoundMetaData(self, smpl, dsid, generator=False):
        msg = "METADATA " + self.filename(smpl) + " -> DSID: " + str(dsid)
        if generator:
            msg += " Generator: " + generator
        self.Success(msg)

    def ReadingFile(self, Name):
        x = ", ".join(
            [t + " - " + str(self._Reader[t].num_entries) for t in self.Trees]
        )
        self.Success("!!!(Reading) -> " + Name.split("/")[-1] + " (" + x + ")")

    def CheckValidKeys(self, requested, found, Type):
        if len(requested) == 0: return
        for i in requested:
            if len([k for k in found if i in k]) > 0:
                continue
            if Type not in self._missed: self._missed[Type] = []
            self._missed[Type].append(i)
            self.Warning("SKIPPED: " + Type + "::" + i)

    def AllKeysFound(self, fname):
        if len([i for t in self._missed for i in self._missed[t]]) == 0:
            self.Success("!!!All requested keys were found for " + fname)
            return None
        return self.Failure("Missing keys detected in: " + fname)
