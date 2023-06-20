class String:
    def __init__(self):
        pass

    def RemoveTrailing(self, inpt, symbol):
        if inpt.endswith(symbol):
            inpt = symbol.join(inpt.split(symbol)[:-1])
        return inpt

    def AddTrailing(self, inpt, symbol):
        if inpt.endswith(symbol) == False:
            inpt += symbol
        return inpt
