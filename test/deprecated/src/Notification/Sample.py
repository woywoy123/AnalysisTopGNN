from .Notification import Notification


class SampleContainer(Notification):
    def __init__(self):
        pass

    def RegisteredDirectory(self, Direct):
        self.Success("!Registered: " + Direct)
        self.Success(
            "!! Files: \n" + "\n -> ".join(self.EventInfo[self.Caller][Direct])
        )
