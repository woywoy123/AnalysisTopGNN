from .Notification import Notification


class Evaluator(Notification):
    def __init__(self):
        pass

    def NoSamplesFound(self):
        string = "Length of provided sample is 0. Make sure to provide the 'TrainingSampleName'"
        self.Failure("=" * len(string))
        self.FailureExit(string)

    def StartModelEvaluator(self):
        smpl = {"Train": 0, "Test": 0, "All": 0, "None": 0}
        for i in self:
            if i.Compiled == False:
                continue
            m = "Train" if i.Train == True else ""
            m = "Test" if i.Train == False else m
            m = "None" if i.Train == None else m
            smpl[m] += 1
            smpl["All"] += 1

        if sum(list(smpl.values())) == 0:
            self.NoSamplesFound()

        string = "--- Starting Model Evaluation ---"
        self.Success("=" * len(string))
        self.Success(string)
        self.Success("=" * len(string))

        models = "!!Models Provided (Epochs):"
        models += " | ".join(
            [
                i + " (" + str(len(self._ModelDirectories[i])) + ")"
                for i in self._ModelDirectories
            ]
        )
        self.Success("!!" + "-" * len(models))
        self.Success(models)
        self.Success("!!" + "-" * len(models))

        sample = "!!Samples found: " + " | ".join(
            [i + " (" + str(smpl[i]) + ")" for i in smpl]
        )
        self.Success("!!" + "-" * len(sample))
        self.Success(sample)
        self.Success("!!" + "-" * len(sample))

    def FileNotFoundWarning(self, Directory, Name):
        pass

    def MakingCurrentJob(self, make, name, ep):
        String = "!!!> Sample Type: " + make + " Model: " + name + " Epoch: " + str(ep)
        self.Success(String)

    def MakingPlots(self, string):
        self.WhiteSpace()
        self.Success("=" * len(string))
        self.Success(string)
        self.Success("=" * len(string))

    def NewModel(self, ModelName):
        self.Success("!" + "-" * 3 + "> New Model: " + ModelName + " <" + "-" * 3)
