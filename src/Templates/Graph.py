import torch
import networkx as nx
from torch_geometric.data import Data


class NoneEvent:
    def __init__(self):
        pass

    def __getattr__(self, inpt):
        return []


class GraphTemplate:
    def __init__(self):
        self.Particles = []
        self.SelfLoop = False
        self.FullyConnect = True
        self.EdgeAttr = {}
        self.NodeAttr = {}
        self.GraphAttr = {}
        self._Event = None
        self.Particles = []
        self.index = -1

    def Escape(self, ev):
        new_self = self.__new__(self.__class__)
        try: new_self.__init__()
        except: pass
        return new_self

    @property
    def Event(self):
        return self._Event

    @Event.setter
    def Event(self, val):
        if val is not None: self._Event = val
        else: self._Event = NoneEvent()

    def CreateParticleNodes(self):
        self.G = nx.Graph()
        self.Nodes = []
        self.NodeParticleMap = {}
        for i in range(len(self.Particles)):
            self.Nodes.append(i)
            self.NodeParticleMap[i] = self.Particles[i]
        self.G.add_nodes_from(self.Nodes)

    def CreateEdges(self):
        self.Edges = []
        for i in self.Nodes:
            for j in self.Nodes:
                if self.SelfLoop == False and i == j:
                    continue
                if self.FullyConnect == False and i != j:
                    continue
                self.Edges.append([i, j])
        self.G.add_edges_from(self.Edges)

    def ConvertToData(self):
        # Anticipates Errors when certain particles dont have an attribute
        def ErrorHandler(fx, *args):
            try:
                if len(args) == 1:
                    return fx(args[0])
                return fx(args[0], args[1])
            except AttributeError:
                return 0

        def ApplyToGraph(Dict, Map2=None, Preprocess=False):
            for key in Dict:
                if key[:2] != "P_" and Preprocess == True:
                    continue
                elif key[:2] == "P_" and Preprocess == False:
                    continue

                fx = Dict[key]
                attr_v = []
                kl = fx.__code__.co_argcount

                if Map2 == None:
                    attr_v += [[ErrorHandler(fx, self.Event)]]
                    k = "G_"
                elif kl == 1:
                    attr_v += [
                        [ErrorHandler(fx, self.NodeParticleMap[n])] for n in Map2
                    ]
                    k = "N_"
                else:
                    attr_v += [
                        [
                            ErrorHandler(
                                fx,
                                self.NodeParticleMap[n[0]],
                                self.NodeParticleMap[n[1]],
                            )
                        ]
                        for n in Map2
                    ]
                    k = "E_"
                if Preprocess == True:
                    continue
                setattr(self.Data, k + key, torch.tensor(attr_v, dtype=torch.float))

        self.CreateParticleNodes()
        self.CreateEdges()

        edge_index = torch.tensor(self.Edges, dtype=torch.long).t()
        self.Data = Data(edge_index=edge_index)

        # Do some preprocessing
        ApplyToGraph(self.GraphAttr, Preprocess=True)
        ApplyToGraph(self.NodeAttr, self.NodeParticleMap, Preprocess=True)
        ApplyToGraph(self.EdgeAttr, self.Edges, Preprocess=True)

        # Apply to graph
        ApplyToGraph(self.GraphAttr)
        ApplyToGraph(self.NodeAttr, self.NodeParticleMap)
        ApplyToGraph(self.EdgeAttr, self.Edges)

        self.Data.num_nodes = torch.tensor(len(self.Particles))
        setattr(
            self.Data,
            "ni",
            torch.tensor([[self.index] for k in range(len(self.Particles))]),
        )
        setattr(self.Data, "i", torch.tensor(self.index))
        setattr(self.Data, "weight", torch.tensor(self.Event.weight))

    def purge(self):
        self.__Clean(self.Particles)
        self.__Clean(self.Event.__dict__)
        del self.GraphAttr
        del self.NodeAttr
        del self.EdgeAttr
        del self._Event
        del self.G
        del self.Nodes
        del self.Edges
        setattr(self.Data, "__name__", self.__class__.__name__)
        return self.Data

    def __Clean(self, obj):
        if isinstance(obj, list):
            for k in obj:
                self.__Clean(k)
            return
        elif isinstance(obj, dict):
            k = []
            k += list(obj.keys())
            k += list(obj.values())
            return self.__Clean(k)
        del obj

    def __SetAttribute(self, c_name, fx, container):
        container[c_name] = fx

    def SetEdgeAttribute(self, c_name, fx):
        self.__SetAttribute(c_name, fx, self.EdgeAttr)

    def SetNodeAttribute(self, c_name, fx):
        self.__SetAttribute(c_name, fx, self.NodeAttr)

    def SetGraphAttribute(self, c_name, fx):
        self.__SetAttribute(c_name, fx, self.GraphAttr)
