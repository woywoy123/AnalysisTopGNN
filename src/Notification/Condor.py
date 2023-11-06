from .Notification import Notification


class _Condor(Notification):
    def __init__(self):
        pass

    def ProjectInheritance(self, instance):
        if self.Verbose: instance.Verbose = self.Verbose
        if not self.ProjectName:
            self.Warning("Inheriting the project name: " + instance.ProjectName)
            self.ProjectName = instance.ProjectName
        if self.ProjectName != instance.ProjectName:
            msg = "Renaming incoming project name. "
            msg += "If this is unintentional, make sure to instantiate "
            msg += "a new Condor instance with the other project name."
            instance.ProjectName = self.ProjectName
            self.Warning(msg)

        if self.OutputDirectory: instance.OutputDirectory = self.abs(self.OutputDirectory)
        elif instance.OutputDirectory: self.OutputDirectory = self.abs(instance.OutputDirectory)

    def DumpedJob(self, name, direc): self.Success("Dumped Job: " + name + " to: " + direc)

    def _CheckEnvironment(self):
        if self.PythonVenv: return
        if self.CondaVenv: return
        messages = [
            "No Environment set! Please specify the environment to use.",
            "- For Conda: set the condor instance attribute <condor>.CondaVenv = <some name>",
            "- For PyVenv: set the condor instance attribute <condor>.PythonVenv = <some path> or $<bashrc alias>",
        ]
        m = max([len(i) for i in messages])
        self.Failure("=" * m)
        for i in messages[:-1]: self.Failure(i)
        self.FailureExit(messages[-1])

    def _CheckWaitFor(self, start, key):
        if start not in key: return True
        message = "The key for one of the waitfor variables is incorrect"
        message += " (Circular dependency): " + start
        self.Warning(message)
        return False
