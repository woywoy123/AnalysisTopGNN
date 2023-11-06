import AnalysisG.Templates.Features.TruthTop as T
import AnalysisG.Templates.Features.TruthTopChildren as TC
import AnalysisG.Templates.Features.TruthJet as TJ
import AnalysisG.Templates.Features.Jet as J


def TruthTops():
    # Edge: Truth
    ET = {"res_edge": T.Edge.res_edge}

    # Node: Truth
    NT = {"res_node": T.Node.res_node}

    # Graph: Truth
    GT = {
        "signal": T.Graph.signal,
        "ntops": T.Graph.ntops,
    }

    # Node: Feature
    NF = {
        "eta": T.Node.eta,
        "energy": T.Node.energy,
        "pT": T.Node.pT,
        "phi": T.Node.phi,
    }

    # Graph: Feature
    GF = {
        "met": T.Graph.met,
        "phi": T.Graph.phi,
    }

    Features = {}
    Features.update(AddFeature("ET", ET))
    Features.update(AddFeature("NT", NT))
    Features.update(AddFeature("GT", GT))

    Features.update(AddFeature("NF", NF))
    Features.update(AddFeature("GF", GF))

    return Features


def TruthChildren():
    # Edge: Truth
    ET = {
        "res_edge": TC.Edge.res_edge,
        "top_edge": TC.Edge.top_edge,
        "lep_edge": TC.Edge.lep_edge,
    }

    # Node: Truth
    NT = {
        "res_node": TC.Node.res_node,
    }

    # Graph: Truth
    GT = {
        "signal": TC.Graph.signal,
        "ntops": TC.Graph.ntops,
        "n_nu": TC.Graph.n_nu,
    }

    # Node: Feature
    NF = {
        "eta": TC.Node.eta,
        "energy": TC.Node.energy,
        "pT": TC.Node.pT,
        "phi": TC.Node.phi,
        "is_b": TC.Node.is_b,
        "is_lep": TC.Node.is_lep,
        "is_nu": TC.Node.is_nu,
    }

    # Graph: Feature
    GF = {
        "met": TC.Graph.met,
        "phi": TC.Graph.phi,
        "n_lep": TC.Graph.n_lep,
        "n_jets": TC.Graph.n_jets,
    }

    Features = {}
    Features.update(AddFeature("ET", ET))
    Features.update(AddFeature("NT", NT))
    Features.update(AddFeature("GT", GT))

    Features.update(AddFeature("NF", NF))
    Features.update(AddFeature("GF", GF))

    return Features


def TruthJets():
    # Edge: Truth
    ET = {
        "res_edge": TJ.Edge.res_edge,
        "top_edge": TJ.Edge.top_edge,
        "lep_edge": TJ.Edge.lep_edge,
    }

    # Node: Truth
    NT = {
        "res_node": TJ.Node.res_node,
        "one_top": TJ.Node.one_top,  # <-- non merged top truth jets
        "top_node": TJ.Node.top_node,  # <-- including merged top truth jets
    }

    # Graph: Truth
    GT = {
        "signal": TJ.Graph.signal,
        "ntops": TJ.Graph.ntops,
        "n_nu": TJ.Graph.n_nu,
    }

    # Node: Feature
    NF = {
        "eta": TJ.Node.eta,
        "energy": TJ.Node.energy,
        "pT": TJ.Node.pT,
        "phi": TJ.Node.phi,
        "is_b": TJ.Node.is_b,
        "is_lep": TJ.Node.is_lep,
        "is_nu": TJ.Node.is_nu,
    }

    # Graph: Feature
    GF = {
        "met": TJ.Graph.met,
        "phi": TJ.Graph.phi,
        "n_lep": TJ.Graph.n_lep,
        "n_jets": TJ.Graph.njets,
    }
    Features = {}
    Features.update(AddFeature("ET", ET))
    Features.update(AddFeature("NT", NT))
    Features.update(AddFeature("GT", GT))

    Features.update(AddFeature("NF", NF))
    Features.update(AddFeature("GF", GF))

    return Features


def Jets():
    # Edge: Truth
    ET = {
        "res_edge": J.Edge.res_edge,
        "top_edge": J.Edge.top_edge,
        "lep_edge": J.Edge.lep_edge,
    }

    # Node: Truth
    NT = {
        "res_node": J.Node.res_node,
        "top_node": J.Node.top_node,  # <-- including merged top truth jets
    }

    # Graph: Truth
    GT = {
        "signal": J.Graph.signal,
        "ntops": J.Graph.ntops,
        "n_nu": J.Graph.n_nu,
    }

    # Node: Feature
    NF = {
        "eta": J.Node.eta,
        "energy": J.Node.energy,
        "pT": J.Node.pT,
        "phi": J.Node.phi,
        "is_b": J.Node.is_b,
        "is_lep": J.Node.is_lep,
        "is_nu": J.Node.is_nu,
    }

    # Graph: Feature
    GF = {
        "met": J.Graph.met,
        "phi": J.Graph.phi,
        "n_lep": J.Graph.n_lep,
        "n_jets": J.Graph.njets,
    }
    Features = {}
    Features.update(AddFeature("ET", ET))
    Features.update(AddFeature("NT", NT))
    Features.update(AddFeature("GT", GT))

    Features.update(AddFeature("NF", NF))
    Features.update(AddFeature("GF", GF))

    return Features


def AddFeature(Prefix, dic):
    return {Prefix + "_" + i: dic[i] for i in dic}


def ApplyFeatures(A, Level=None):
    if Level is None:
        name = A.Graph.__name__
        if "Tops" in name: Level = "TruthTops"
        elif "Children" in name: Level = "TruthChildren"
        elif "TruthJet" in name: Level = "TruthJets"
        elif "GraphJet" in name or "Detector" in name: Level = "Jets"
        else: Level = ""

    if Level == "TruthTops": Features = TruthTops()
    elif Level == "TruthChildren": Features = TruthChildren()
    elif Level == "TruthJets": Features = TruthJets()
    elif Level == "Jets": Features = Jets()
    else:
        print("ApplyFeatures::INVALID CHOICE!")
        exit()
    for i in Features:
        base = "_".join(i.split("_")[1:])
        fx = Features[i]
        if "EF" in i: A.AddEdgeFeature(fx, base)
        elif "NF" in i: A.AddNodeFeature(fx, base)
        elif "GF" in i: A.AddGraphFeature(fx, base)
        elif "ET" in i: A.AddEdgeTruthFeature(fx, base)
        elif "NT" in i: A.AddNodeTruthFeature(fx, base)
        elif "GT" in i: A.AddGraphTruthFeature(fx, base)
