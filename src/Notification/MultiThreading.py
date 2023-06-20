from .Notification import Notification


class _MultiThreading(Notification):
    def __init__(self):
        pass

    def RecoveredThread(self, w):
        self.Warning("A Thread has failed. Switching to main thread. Worker: " + str(w))

    def AlertOnEmptyList(self):
        self._lock = False
        if len(self._lists) == 0:
            self.Failure("Can't process an empty list. Skipping...")
            self._lock = True
