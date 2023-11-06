from .Notification import Notification

class _RandomSamplers(Notification):
    def __init__(self): pass
    def NotEnoughEvents(self, Given, Requested):
        msg =  "More events are requested than available. "
        msg += "Returning given events but shuffled."
        self.Failure(msg)
        self.Failure("Given: " + str(len(Given)) + " Requested: " + str(Requested))

    def RandomizingSamples(self, SampleSize, TrainingSize):
        self.Success("Given sample size: " + str(SampleSize))
        msg =  "!!!Generating: " + str(TrainingSize)
        msg += "(%) as training and " + str(100 - TrainingSize)
        msg += "(%) as test sample."
        self.Success(msg)

    def RandomizingSize(self, train, test):
        msg =  "!!!Generating: Events " + str(train)
        msg += " as training and " + str(test)
        msg += " as test sample."
        self.Success(msg)

    def ExpectedDictionarySample(self, Type):
        msg = "Expected a dictionary of samples, but got: " + str(Type)
        return self.Failure(msg)
