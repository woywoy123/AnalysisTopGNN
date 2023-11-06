from .Notification import Notification


class _IO(Notification):
    def __init__(self):
        pass

    def FileNotFoundWarning(self, Directory, Name):
        self.Warning("File: " + Name + " not found in " + Directory)

    def EmptyDirectoryWarning(self, Directory):
        self.Warning(
            "No samples found in " + Directory.replace("//", "/") + " skipping."
        )

    def FoundFiles(self, Files):
        for i in Files:
            l, x = len(Files[i]), Files[i]
            if l > 5: x, l = Files[i][:5], l - 5
            mg = "!!Files Found in Directory: " + i + "\n -> " + "\n -> ".join(x)
            if l > 5: mg += " (... " + str(l) + " other files)"
            self.Success(mg)

    def PickleOutput(self):
        x = self.abs()

    def DumpingObjectName(self, Name):
        if self.Filename.endswith(self._ext) == False:
            self.Filename += self._ext
        self.Success("!!!Dumping: " + Name + " to " + self.Filename)
