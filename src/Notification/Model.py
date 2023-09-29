from .Notification import Notification


class _ModelWrapper(Notification):
    def __init__(self):
        pass

    def _dress(self, inpt):
        if inpt.startswith("G_T"):
            return "(Graph Truth): " + inpt[4:]
        if inpt.startswith("N_T"):
            return "(Node Truth): " + inpt[4:]
        if inpt.startswith("E_T"):
            return "(Edge Truth): " + inpt[4:]

        if inpt.startswith("G_"):
            return "(Graph): " + inpt[2:]
        if inpt.startswith("N_"):
            return "(Node): " + inpt[2:]
        if inpt.startswith("E_"):
            return "(Edge): " + inpt[2:]
        return inpt

    def _iscompatible(self):
        run = 0
        inpt = len(self._inputs) == len(self.i_mapping)
        if inpt:
            self.Success(self.RunName + ":: -> INPUT Ok! <-")
        else:
            for i in self._inputs:
                try:
                    self.Success("-> " + self._dress(self.i_mapping[i]))
                except KeyError:
                    self.Warning("Missing -> " + self._dress(i))
            return False

        inpt = len(self._outputs) == len(self.o_mapping)
        if inpt and self._train:
            self.Success(self.RunName + ":: <- Outputs Ok! ->")
        elif not self._train and len(self._outputs) != 0:
            return self.Success("Inference Ok!")
        else:
            for i in self._outputs:
                try:
                    self.Success("-> " + self._dress(self.o_mapping[i]))
                except KeyError:
                    self.Warning("Missing -> " + self._dress(i))
            return False
        return True
