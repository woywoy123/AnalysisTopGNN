import Templates.ParticleGeneric.EdgeFeature as ef
import Templates.ParticleGeneric.NodeFeature as nf
import Templates.ParticleGeneric.GraphFeature as gf

def AddFeature(Prefix, dic):
    return {Prefix + "_" + i : dic[i] for i in dic} 

def TruthJets():
    import Templates.TruthJet.EdgeFeature as tj_ef
    import Templates.TruthJet.NodeFeature as tj_nf
    import Templates.TruthJet.GraphFeature as tj_gf

    # Node: Generic Particle Properties
    GenPartNF = {
            "eta" : nf.eta, 
            "energy" : nf.energy, 
            "pT" : nf.pT, 
            "phi" : nf.phi, 
            "mass" : nf.mass, 
            "islep" : nf.islepton, 
            "charge" : nf.charge, 
    }
    
    # Graph: Generic Particle Properties
    GenPartGF = {
            "mu" : gf.mu, 
            "met" : gf.met, 
            "met_phi" : gf.met_phi, 
            #"pileup" : gf.pileup, 
            "njets" : gf.nTruthJets, 
            #"nlep" : gf.nLeptons,
    }
    
    # Truth Edge: Truth Jet Properties
    TruthJetTEF = {
            "edge" : tj_ef.Index, 
    } 
    
    # Truth Node: Truth Jet Properties
    TruthJetTNF = {
            "tops_merged" : tj_nf.TopsMerged, 
            "from_top" : tj_nf.FromTop, 
    } 
    
    # Truth Node: Generic Paritcle Properties
    GenPartTNF = {
            "from_res" : nf.FromRes
    }
    
    # Truth Graph: Generic Paritcle Properties
    GenPartTGF = {
            #"mu_actual" : gf.mu_actual,
            "nTops" : gf.nTops, 
            "signal_sample" : gf.SignalSample
    }
    
    Features = {}
    Features |= AddFeature("NF", GenPartNF)
    Features |= AddFeature("GF", GenPartGF)
    Features |= AddFeature("ET", TruthJetTEF)
    Features |= AddFeature("NT", TruthJetTNF)    
    Features |= AddFeature("NT", GenPartTNF)
    Features |= AddFeature("GT", GenPartTGF)
    return Features

def TruthTopChildren():
    import Templates.TruthTopChildren.NodeFeature as tc_nf
    
    # Node: Generic Particle Properties
    GenPartNF = {
            "eta" : nf.eta, 
            "energy" : nf.energy, 
            "pT" : nf.pT, 
            "phi" : nf.phi, 
            "mass" : nf.mass, 
            "islep" : nf.islepton, 
            "charge" : nf.charge, 
    }
    
    # Graph: Generic Particle Properties
    GenPartGF = {
            "mu" : gf.mu, 
            "met" : gf.met, 
            "met_phi" : gf.met_phi, 
    }
    
    # Truth Edge: Truth Children Properties
    ChildrenTEF = {
            "edge" : ef.Index, 
    } 
    
    # Truth Node: Truth Children Properties
    ChildrenTNF = {
            "from_res" : tc_nf.FromRes, 
    } 
    
    # Truth Graph: Generic Paritcle Properties
    GenPartTGF = {
            "nTops" : gf.nTops, 
            "signal_sample" : gf.SignalSample
    }
    
    Features = {}
    Features |= AddFeature("NF", GenPartNF)
    Features |= AddFeature("GF", GenPartGF)
    Features |= AddFeature("ET", ChildrenTEF)
    Features |= AddFeature("NT", ChildrenTNF)    
    Features |= AddFeature("GT", GenPartTGF)

    return Features
 

def ApplyFeatures(A, Level):
    if Level == "TruthChildren":
        Features = TruthTopChildren()

    if Level == "TruthJets":
        Features = TruthJets()

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
