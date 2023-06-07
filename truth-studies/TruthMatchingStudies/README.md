# Truth Matching Studies for AnalysisTop n-tuples 
## Commit hash: 
- `master@7d70c412a65160d897d0253cbb42e5accf2c5bcf`

## Glossary:
- **Truth Tops**: 
Tops-Quarks within the sample which have already emitted gluons (Final State Radiation).
- **Truth Top Children (Truth Children)**: 
Particles originating from the Truth Tops, if any of the particles are a W-Boson, then its children are used.
- **Truth Jets**: 
Partons after they undergo hadronization without any detector convolutions. 
- **Jets**:
Partons after they undergo hadronization with detector convolutions.
- **Signal/Resonance Tops**:
Top-Quarks produced from the Z/H Beyond Standard Model Particle.
- **Spectator Tops**
Tops-Quarks which are the by-product of producing a Z/H boson.

## Studies: 
- **ZPrimeMatrix**: 
This study creates a 2D plot of the PT vs Mass of the Z/H-Resonance for tops, truth children, truth jets and jets.
- **ResonanceDecayModes**:
Provides information about how the tops involved in the resonance decay. 
- **ResonanceMassFromTops**: 
Reconstructs the signal resonance from truth tops after Final State Radiation. 
- **ResonanceDeltaRTops**:
Aims to identify shape differences between spectator and signal tops using deltaR distributions.
- **ResonanceTopKinematics**:
Depicts the various kinematics of the spectator/signal tops being produced from the signal Z/H-Resonance.
- **EventNTruthJetAndJets**:
This study aims to identify the loss in truth jets by having off-diagonal elements in a 2D plot. 
It also explores the MET vs n-Lepton correlations.
- **EventMETImbalance**:
A set of plots which explore the missing transverse discrepancy between measurement from the detector simulation and the truth neutrinos.
- **EventNuNuSolutions**:
This study aims to investigate the number of double neutrino solutions obtained when rotating the 4-top system such that, the z-component of the 4-vector points down the beam-pipe.
The number of solutions obtained after rotation is compared to a non-rotation operation.
Only events containing exactly two neutrinos and b-quarks originating from two truth tops are considered, regardless of whether these originate from the resonance.
- **TopDecayModes**:
Plots indicating to which children the Top-Quark decays into. 
- **ResonanceMassFromChildren**:
Plots relating to the resonance being reconstructed from the top truth children, where the resonance tops decay either Hadronically, Leptonically or Hadronically-Leptonically.
- **TruthChildrenKinematics**:
This selection implementation aims to investigate the delta-R dependency of the parent top PT and how closely clustered the children are together. 


## Figures Produced:
### ZPrimeMatrix:
- **ZPrimeMatrix-TruthTops**: 
A 2D figure depicating the Z/H transverse momenta as a function of invariant mass from truth tops.
- **ZPrimeMatrix-TruthChildren**: 
A 2D figure depicting the Z/H transverse momenta as a function of invariant mass from truth children.
- **ZPrimeMatrix-TruthJets**: 
A 2D figure depicting the Z/H transverse momenta as a function of invariant mass from truth jets.
- **ZPrimeMatrix-Jets**: 
A 2D figure depicting the Z/H transverse momenta as a function of invariant mass from jets.

### ResonanceDecayModes:
- **Figure_1.1a**:
Number of hadronic and leptonically decaying resonance tops (a resonance is classified as hadronic if all tops decay hadronically)
- **Figure_1.1b**:
Decay channels of the tops, this is an extension of Figure 1.1a.

### ResonanceMassFromTops:
- **Figure_1.1c**:
Split into whether the children tops decay leptonically and hadronically or both (Top decay channel shouldn't impact the mass, but just to be sure)

### ResonanceDeltaRTops:
- **Figure_1.1d**:
DeltaR between process truth tops  (Here we check whether the spectator tops are separated from resonance tops)

### ResonanceTopKinematics:
- **Figure_1.1e**:
PT Distribution of tops 
- **Figure_1.1f**:
Energy Distribution of tops
- **Figure_1.1g**:
Pseudorapidity of tops 
- **Figure_1.1h**:
Azimuthal angle of tops

### EventNTruthJetAndJets:
- **N-TruthJets_n-Jets**:
A plot, depicting on a per event basis, the number of truth jets vs reconstructed jets (i.e. observed jets).
Ideally, this would be as diagonal as possible to indicate no truth jet loss
- **MissingET_n-TruthLep**:
A plot illustrating how the number of leptonically decaying tops contribute to the missing transverse momenta of the event.

### EventMETImbalance:
- **4-TopSystem-Pz_PT**:
A 2D plot illustrating non-zero PT components from the 4-top system. 
This is due to the samples not capturing the partons originating from the colliding protons. 
- **AngleRelativeToBeamPipe**:
The angle between the Pz component and the PT of the 4-top system. 
Ideally, a strong clustering around the 0-rad mark should be observed, anything else is indicating that not all the MET can be accounted for by only looking at truth neutrinos.
- **AngleRelativeToBeamPipe-Rotated**:
The angle between the Pz component and the PT of the 4-top system, after rotating the system according to the imbalance angle.
This plot is majorly a closure test to assure the rotation was implemented correctly and should yield a peak at 0.
- **MissingET**:
A plot illustrating the distributions of the Missing Energy in the Transverse direction as measured in simulation and reconstructed from Truth Neutrinos.
- **difference-MissingET**:
The observed difference between measurement and truth neutrinos.
- **MissingET-Rotated**:
A plot illustrating the distribution of the missing Energy in the Transverse direction as measured in simulation, but with the truth neutrinos being rotated into a reference frame where the 4-top system momentum balance is zero.
- **difference-MissingET-Rotated**:
The observed difference between measurement and rotated truth neutrinos.

### EventNuNuSolutions:
- **Number-of-solutions**:
Number of returned neutrino solutions with and without rotation of the 4-top system.
- **Delta-Missing-MET-NoRotation**:
A TH2F plot of the missing energy in the x and y direction without rotating the truth children into the 4-top system
- **Delta-Missing-MET-Rotation**:
A TH2F plot of the missing energy in the x and y direction with rotating the truth children into the 4-top system
- **Top-Mass-Delta-NoRotation**:
A mass difference plot of the truth mass and the reconstructed top from neutrino solutions. 
This plot aims to identify potential patterns when not rotating the reference frame of the truth children into the 4-top system.
- **Top-Mass-Delta-Rotation**:
A mass difference plot of the truth mass and the reconstructed top from neutrino solutions. 
This plot aims to identify potential patterns when rotating the reference frame of the truth children into the 4-top system.
- **MET-Ratio**:
A TH2F plot of the MET and truth neutrino's pt with and without rotation.

### TopDecayModes:
- **Figure_2.1a**:
A plot depicting the fraction by which the Top-Quark decays into. 
- **Figure_2.1b**:
A plot of the reconstructed invariant mass of the tops from their corresponding truth children.

### ResonanceMassFromChildren:
- **Figure_2.1c**:
A plot of the reconstructed resonance from truth children.

### TruthChildrenKinematics:
- **Figure_2.1d**:
A plot illustrating the delta-R between truth children originating from a common top, but partitioned into resonance/spectator tops.
- **Figure_2.1e**:
A plot illustrating the delta-R between originating truth top and decay children partitioned into leptonic and hadronic top decay channels.
- **Figure_2.1f**:
A plot illustrating the overlap in delta-R between truth children originating and not originating from mutual top. 
This aims to identify whether only using the delta-R to cluster children causes falsely matched children.
From the legend, 'False' implies the parent tops are not equal.
- **Figure_2.1g**:
A TH2F plot of the originating top's PT and only hadronically decaying top children delta-R. 
This aims to verify whether a correlation between the top's PT and the clustering of children is present. 
- **Figure_2.1h**:
A TH2F plot of the originating top's PT and only Leptonically decaying top children delta-R. 
This aims to verify whether a correlation between the top's PT and the clustering of children is present. 
- **Figure_2.1i**:
A plot illustrating the fractional PT being transferred to truth children from associated top.

<!--
-> Figure 3.1:
a: PDGID of Truth Jet parton contributions - These are derived from the GhostPartons that define the truth jet
b: Fraction of parton PT contribution to truth jet
c: DeltaR between parton contributions and truth jet axis
d: Truth Jet PT classified into from top or background
e: Inefficiency of truth jet parton matching based on truth child PDGID (This is based on the truth partons contained in the truth jet.). 
- To elaborate further what this plot tries to demonstrate, it is the percentage lost of each child type. 
- This is calculated by counting the respective top child pdgid and taking the ratio when using truth jet partons matched to the top child. 
- For example; (truth) t -> b + q + qbar this should yield in an ideal world 1 b and 2 q's but from the truth jet partons, this list might only contain b + q, meaning all 'b' were collected, but one of the q's has been lost. 
- A plot of this would therefore have b (0%) and q (50%) (due to the lost qbar). 
f: Reconstructed Invariant Top Mass from Truth Jets - Split into Lepton (+ using the neutrino from truth children - Just to double check that the jets are consistent) and hadronic
g: Z-Prime from Had-Had, Had-Lep, Lep-Lep (again including neutrino)

h: Counting merged truth jets from Signal and Spectator tops. 
i: DeltaR Distribution between truth jets originating from the same truth top. This assumed NO Truth Jets shared different tops.
j: DeltaR Distribution between truth jets originating from different truth tops. This assumed NO Truth Jets shared different tops.


#-----\/ --- needs reworking
-> Figure 4: (x) Not Complete yet.... Jets
+Do as above but add deltaR between jet and truth jet 

-> Figure 5: (x) Not Complete yet....
+ Do Bruce Analysis.
+ Selection criteria:
~> Leptonic t: This is spectator 1
~> 2 Hardest b-tagged jets: these correspond to the Z' daughter tops
~> attach two other jets to each <somehow> (I use deltaR)
~> You now have the Z' -> ttbar daughters
~> Remaining jets are your 2nd spectators 
~> Form M(Z')
~> Fit fit M(Z') 

-->
