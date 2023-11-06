from .Notification import Notification


class _ModelWrapper(Notification):
    def __init__(self):
        pass

    def _check_broken_model(self):
        if not self.failure: return False
        self.Failure(self.error_message)
        return True

    def _dress(self, inpt):
        if inpt.startswith("G_T"): return "(Graph Truth): " + inpt[4:]
        if inpt.startswith("N_T"): return "(Node Truth): " + inpt[4:]
        if inpt.startswith("E_T"): return "(Edge Truth): " + inpt[4:]

        if inpt.startswith("G_"): return "(Graph): " + inpt[2:]
        if inpt.startswith("N_"): return "(Node): " + inpt[2:]
        if inpt.startswith("E_"): return "(Edge): " + inpt[2:]
        return "(Other Feature): " + inpt

    def _iscompatible(self, smpl):
        for i in self.in_map:
            try: smpl[i]
            except KeyError:
                self.Warning("Missing -> " + self._dress(i))
                continue

            dress = self._dress(i)
            if "Truth):" in dress: self.Warning("Detected Truth Input -> " + dress)
            else: self.Success("-> " + dress)

        self.Success("-> " + self.RunName + " <- Inputs Ok!")
        for i, j in self.out_map.items():
            try: smpl[i]
            except KeyError:
                self.Warning("Missing -> " + self._dress(i))
                continue
            self.Success("-> " + self._dress(i) + " => " + j)

        self.Success(self.RunName + ":: <- Outputs Ok!")
        self.Success("Inference Ok!")

        if not len(self.KinematicMap): return True
        self.match_reconstruction(smpl.to_dict())
        if "graphs" not in self(smpl): return False
        if len(self.error_message): self.Failure(self.error_message)
        msg = "Detected Mass Reconstruction Mapping: "
        msg += "\n -> ".join([""] + [key + ": " + " ".join(self.KinematicMap[key]) for key in self.KinematicMap])
        self.Success(msg)
        return True

    def _failed_model_load(self):
        self.FailureExit("-> Failed to Load Model")
