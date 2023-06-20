import torch


class TorchScriptModel(Notification):
    def __init__(self, ModelPath, VerboseLevel=0, **kargs):
        self.VerboseLevel = VerboseLevel
        self.Caller = "TorchScriptModel"
        self.ModelPath = ModelPath

        self.__ExtraFiles()
        self._model = torch.jit.load(self.ModelPath, _extra_files=self.key)
        self.__forward()
        self.__CheckOutpout()

        self._keys = {}

        if len(kargs) == 0:
            kargs = {}
        elif list(kargs.values())[0] == None:
            kargs = {}

        if len(self.Outputs) > 0 and len(kargs) == 0:
            self.Warning("Found Outputs (In order): " + " | ".join(self.Outputs))
        if len(self.keys) > 0 and len(kargs) == 0:
            self.Warning("Found Keys: " + " | ".join(self.keys))
            return

        for i in list(kargs.values())[0]:
            self.AddOutput(**i)

    def __CheckOutpout(self):
        x = [
            str(i).replace(",", "").replace("\n", "")
            for i in self._model.graph.outputs()
        ]
        x = [str(i).replace("(", "").replace(")", "").split("=")[-1] for i in x]
        x = [
            "%" + j.replace(" ", "").split("#")[0] for i in x for j in i.split("%")[1:]
        ]
        self.Outputs = x

    def __ExtraFiles(self):
        key = {
            str(l): ""
            for l in open(self.ModelPath, "rb").readlines()
            if "/extra/" in str(l)
        }
        out = []
        for k in list(
            set(
                [l.split("/")[-1] for t in key for l in t.split("\\") if "/extra/" in l]
            )
        ):
            x = "FB".join(k.split("FB")[:-1])
            if x != "":
                out.append(x)
            x = "PK".join(k.split("PK")[:-1])
            if x != "":
                out.append(x)
        self.key = {k: "" for k in list(set(out))}
        self.keys = {k[2:]: "" for k in self.key}

    def __forward(self):
        x = [i.replace(" ", "") for i in str(self._model.forward.code).split("\n")]
        x = [i.split(":")[0] for i in x if ":Tensor" in i]

        self.forward = self
        self.forward.__code__ = self
        self.forward.__code__.co_varnames = x + ["self"]
        self.forward.__code__.co_argcount = len(x) + 1
        self.Inputs = x

    def AddOutput(self, name, node, loss=None, classifier=None):
        def CheckType(val, typ):
            if typ == "NoneType":
                return None
            if typ == "str":
                return str(val)
            if typ == "bool":
                return bool(val)

        node = node.lstrip("%")
        for i in self._model.graph.nodes():
            f_n = str(i).split(":")[0]

            if node not in f_n:
                continue
            if name in self.keys and loss == None and classifier == None:
                tmp = [
                    self.key[j + name].decode().split("->")
                    for j in ["O_", "L_", "C_"]
                    if j + name in self.key
                ]
                tmp = [CheckType(j[0], j[1]) for j in tmp]
                loss, classifier = tmp[1], tmp[2]

            self.keys[name] = [list(i.outputs())[0], loss, classifier]
            self.Notify(
                "!!!SUCCESSFULLY ADDED: "
                + name
                + " -> "
                + node
                + "| LOSS: "
                + self.keys[name][1]
                + " CLASSIFICATION: "
                + str(self.keys[name][2])
            )
            return
        self.Warning("FAILED TO ADD: " + name + " -> " + node + " NOT FOUND!")

    def ShowNodes(self):
        self.Notify("------------ BEGIN GRAPH NODES -----------------")
        for i in self._model.graph.nodes():
            n = str(i).replace("\n", "").split(" : ")
            f = n[1].split("#")
            string = "Name: " + n[0] + " | Operation: " + f[0]
            if len(f) > 1:
                string += " | Function Call: " + f[1].split("/")[-1]
            self.Notify(string)
        self.Notify("------------ END GRAPH NODES -----------------")

    def Finalize(self):
        it = len(list(self._model.graph.outputs()))
        for i in self.keys:
            setattr(self, "O_" + i, None)
            setattr(self, "L_" + i, self.keys[i][1])
            setattr(self, "C_" + i, self.keys[i][2])
            self._model.graph.registerOutput(self.keys[i][0])
            self._keys["O_" + i] = it
            it += 1
        self._model.graph.makeMultiOutputIntoTuple()

    def train(self):
        self._model.train()

    def eval(self):
        self._model.eval()

    def __call__(self, **kargs):
        if len(self._keys) == 0:
            self.Finalize()
        out = self._model(**{key: kargs[key] for key in self.Inputs})
        for i in self._keys:
            setattr(self, i, out[self._keys[i]])

    def to(self, device):
        self._model.to(device)
