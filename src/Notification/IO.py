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
            self.Success(
                "!!Files Found in Directory: " + i + "\n -> " + "\n -> ".join(Files[i])
            )

    def PickleOutput(self):
        x = self.abs()

    def DumpingObjectName(self, Name):
        if self.Filename.endswith(self._ext) == False:
            self.Filename += self._ext
        self.Success("!!!Dumping: " + Name + " to " + self.Filename)
