from AnalysisG.Templates import ParticleTemplate

# Define your particles here
class Jet(ParticleTemplate):
    
    def __init__(self):
        
        # Inherit the base class from the framework
        ParticleTemplate.__init__(self)
       
        # Add attributes 
        self.Type = "jet" # <- Optional 
        self.pt = self.Type + "_pt"
        self.e = self.Type + "_e"
        self.eta = self.Type + "_eta"
        self.phi = self.Type + "_phi"
    
