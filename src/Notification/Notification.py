import os


class Base:
    def __init__(self):
        pass

    def Format(self, Color, Message, State):
        Message = self.Verbosity(Message)
        if Message == False: return False
        txt = "\033[0;9" if self.Caller == "" else "\033[1;9"
        txt += str(Color) + "m"
        txt += "" if self.Caller == "" else self.Caller.upper() + "::"
        txt += State + "::"
        txt += Message if self.Caller == "" else "\033[0;9" + str(Color) + "m" + Message
        txt += "\033[0m"
        print(txt)
        return True

    def Verbosity(self, message):
        lvl = len(message) - len(message.lstrip("!"))
        if lvl > self.Verbose: return False
        return message.lstrip("!")

    def WhiteSpace(self):
        print()


class __Failure(Base):
    def __init__(self):
        self.Base.__init__(self)

    def Failure(self, Message):
        return self.Format(1, Message.lstrip("!"), "FAILURE")

    def FailureExit(self, Message):
        self.Format(1, Message.lstrip("!"), "FAILURE")
        self.Format(1, "=" * len(Message.lstrip("!")), "FAILURE")
        os._exit(1)


class __Success(Base):
    def __init__(self):
        self.Base.__init__(self)

    def Success(self, Message):
        return self.Format(2, Message, "SUCCESS")

    def FinishExit(self, Message=""):
        self.Format(2, Message, "FINISHED")
        os._exit(1)


class __Warning(Base):
    def __init__(self):
        self.Base.__init__(self)

    def Warning(self, Message):
        return self.Format(3, Message.lstrip("!"), "WARNING")


class Notification(__Failure, __Success, __Warning):
    def __init__(self, verb=3, caller=""):
        self.Verbose = verb
        self.Caller = caller
