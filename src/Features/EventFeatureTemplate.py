def AddFeature(Prefix, dic):
    return {Prefix + "_" + i : dic[i] for i in dic} 

def TruthTops():
    import AnalysisTopGNN.Features.TruthTop.EdgeFeature as t_ef
    import AnalysisTopGNN.Features.TruthTop.NodeFeature as t_nf
    import AnalysisTopGNN.Features.TruthTop.GraphFeature as t_gf

    # Node: Kinematics 
    NF = {
            "eta" : t_nf.eta, 
            "energy" : t_nf.energy, 
            "pT" : t_nf.pT, 
            "phi" : t_nf.phi,
            "mass" : t_nf.mass
        }
    
    NT = {"res" : t_nf.FromRes}
    GT = {"signal" : t_gf.SignalEvent}
    GF = {"ntops" : t_gf.nTops}
    ET = {"edge" : t_ef.edge}

    Features = {}
    Features |= AddFeature("NF", NF)
    Features |= AddFeature("NT", NT)
    Features |= AddFeature("GF", GF)
    Features |= AddFeature("GT", GT)
    Features |= AddFeature("ET", ET)
    return Features       

def TruthTopChildren():
    import AnalysisTopGNN.Features.TruthTopChildren.GraphFeature as tc_gf
    import AnalysisTopGNN.Features.TruthTopChildren.NodeFeature as tc_nf
    import AnalysisTopGNN.Features.TruthTopChildren.EdgeFeature as tc_ef

    NF = {
            "eta"    : tc_nf.eta, 
            "energy" : tc_nf.energy, 
            "pT"     : tc_nf.pT, 
            "phi"    : tc_nf.phi, 
            "mass"   : tc_nf.mass, 
            "charge" : tc_nf.charge, 
    }
    
    GF = {
 
            "met"     : tc_gf.MET, 
            "met_phi" : tc_gf.MET_Phi
        }

    
    GT = {
            "signal"  : tc_gf.Signal, 
            "ntops"   : tc_gf.nTops,
            "nlep"    : tc_gf.nLeptons, 
            "nNu"     : tc_gf.nNeutrinos,
        }

    NT = {
            "node_res" : tc_nf.FromRes, 
            "top" : tc_nf.FromTop, 
            "islep"  : tc_nf.islepton, 
            "isNu"   : tc_nf.isneutrino, 
        }
    
    ET = {
            "edge_res"  : tc_ef.ResEdge,
            "edge" : tc_ef.edge
        }
    
    Features = {}
    Features |= AddFeature("GF", GF)
    Features |= AddFeature("NF", NF)
    Features |= AddFeature("ET", ET)
    Features |= AddFeature("NT", NT)
    Features |= AddFeature("GT", GT)
    return Features

def TruthJets():
    import AnalysisTopGNN.Features.TruthJet.EdgeFeature as tj_ef
    import AnalysisTopGNN.Features.TruthJet.NodeFeature as tj_nf
    import AnalysisTopGNN.Features.TruthJet.GraphFeature as tj_gf

    # Node: Generic Particle Properties
    NF = {
            "eta"    : tj_nf.eta, 
            "energy" : tj_nf.energy, 
            "pT"     : tj_nf.pT, 
            "phi"    : tj_nf.phi, 
            "mass"   : tj_nf.mass, 
            "charge" : tj_nf.charge, 
            "islep"  : tj_nf.islepton, 

    }
   
    NT = {
            "mrgT"   : tj_nf.mergedTop, 
            "top"    : tj_nf.FromTop, 
            "res"    : tj_nf.FromRes, 
    }

    ET = {
            "edge"   : tj_ef.edgeTop, 
            "edgeCh" : tj_ef.edgeChild, 
            "res"    : tj_ef.edgeRes, 
    }
    
    GF = {
            "nJ"     : tj_gf.nJets, 
            "nL"     : tj_gf.nLeptons, 
            "met"    : tj_gf.MET, 
            "met_phi" : tj_gf.MET_Phi,
    }
    
    GT = {
            "ntops"     : tj_gf.nTops, 
            "signal"     : tj_gf.Signal, 
    }
 

    Features = {}
    Features |= AddFeature("NF", NF)
    Features |= AddFeature("NT", NT)
    Features |= AddFeature("ET", ET)
    Features |= AddFeature("GF", GF)
    Features |= AddFeature("GT", GT)
    return Features

def ApplyFeatures(A, Level):
    if Level == "TruthTops":
        Features = TruthTops()
    elif Level == "TruthChildren":
        Features = TruthTopChildren()
    elif Level == "TruthJets":
        Features = TruthJets()
    else:
        print("failed")
        exit()


    for i in Features:
        base = "_".join(i.split("_")[1:])
        fx = Features[i]
        
        if "EF" in i:
            A.AddEdgeFeature(fx, base)
        elif "NF" in i:
            A.AddNodeFeature(fx, base)
        elif "GF" in i:
            A.AddGraphFeature(fx, base)

        elif "ET" in i:
            A.AddEdgeTruth(fx, base)
        elif "NT" in i:
            A.AddNodeTruth(fx, base)
        elif "GT" in i:
            A.AddGraphTruth(fx, base)
