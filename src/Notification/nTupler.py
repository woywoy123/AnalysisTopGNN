from .Notification import Notification

class _nTupler(Notification):

    def __init__(self):
        pass
 
    def _KeyNotFound(self, var, inpt, others):
        msg = "Specified key/variable not found (" + var + "::" + inpt + "). "
        msg += "Keys available are: \n->"
        msg += "\n->".join(others)
        self.Warning(msg)
        self.Warning("Skipping for now...")
