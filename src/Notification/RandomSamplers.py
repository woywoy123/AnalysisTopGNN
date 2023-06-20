from .Notification import Notification


class _RandomSamplers(Notification):
    def __init__(self):
        pass

    def NotEnoughEvents(self, Given, Requested):
        self.Failure(
            "More events are requested than available. Returning given events but shuffled."
        )
        self.Failure("Given: " + str(len(Given)) + " Requested: " + str(Requested))

    def RandomizingSamples(self, SampleSize, TrainingSize):
        self.Success("Given sample size: " + str(SampleSize))
        self.Success(
            "!!!Generating: "
            + str(TrainingSize)
            + "(%) as training and "
            + str(100 - TrainingSize)
            + "(%) as test sample."
        )

    def RandomizingSize(self, train, test):
        self.Success(
            "!!!Generating: Events "
            + str(train)
            + " as training and "
            + str(test)
            + " as test sample."
        )

    def ExpectedDictionarySample(self, Type):
        return self.Failure("Expected a dictionary of samples, but got: " + str(Type))
