Truth Matching Studies for AnalysisTop n-tuples 
===============================================

Commit hash: 
- `master@7d70c412a65160d897d0253cbb42e5accf2c5bcf`

Glossary
________
- **Truth Tops**: Tops-Quarks within the sample which have already emitted gluons (Final State Radiation).
- **Truth Top Children (Truth Children)**: Particles originating from the Truth Tops, if any of the particles are a W-Boson, then its children are used.
- **Truth Jets**: Partons after they undergo hadronization without any detector convolutions. 
- **Jets**: Partons after they undergo hadronization with detector convolutions.
- **Signal/Resonance Tops**: Top-Quarks produced from the Z/H Beyond Standard Model Particle.
- **Spectator Tops**: Tops-Quarks which are the by-product of producing a Z/H boson.

Figure Naming Convention
________________________

Figures are generally given the naming/numbering scheme **Figure_(truth level).(sub-figure)(figure)**. 
The Truth level starts from 0 and goes to 4, with the former being event information and the latter jets. 

Studies
_______

- **ZPrimeMatrix**: This study creates a 2D plot of the PT vs Mass of the Z/H-Resonance for tops, truth children, truth jets and jets.
- **ZPrimeMatrix-TruthTops**: A 2D figure depicating the Z/H transverse momenta as a function of invariant mass from truth tops.
- **ZPrimeMatrix-TruthChildren**: A 2D figure depicting the Z/H transverse momenta as a function of invariant mass from truth children.
- **ZPrimeMatrix-TruthJets**: A 2D figure depicting the Z/H transverse momenta as a function of invariant mass from truth jets.
- **ZPrimeMatrix-Jets**: A 2D figure depicting the Z/H transverse momenta as a function of invariant mass from jets.

ResonanceDecayModes
___________________

Provides information about how the tops involved in the resonance decay. 

- **Figure_1.1a**: Number of hadronic and leptonically decaying resonance tops (a resonance is classified as hadronic if all tops decay hadronically)
- **Figure_1.1b**: Decay channels of the tops, this is an extension of **Figure 1.1a**.

ResonanceMassFromTops
_____________________

Reconstructs the signal resonance from truth tops after Final State Radiation. 

- **Figure_1.1c**: Split into whether the children tops decay leptonically and hadronically or both (Top decay channel shouldn't impact the mass, but just to be sure)
- **ResonanceDeltaRTops**: Aims to identify shape differences between spectator and signal tops using :math:`\Delta R` distributions.
- **Figure_1.1d**: :math:`\Delta R` between process truth tops  (Here we check whether the spectator tops are separated from resonance tops)

ResonanceTopKinematics
______________________

Depicts the various kinematics of the spectator/signal tops being produced from the signal Z/H-Resonance.

- **Figure_1.1e**: PT Distribution of tops 
- **Figure_1.1f**: Energy Distribution of tops
- **Figure_1.1g**: Pseudorapidity of tops 
- **Figure_1.1h**: Azimuthal angle of tops
- **Figure_1.1i**: A TH2F plot of the truth top's pT and energy 
- **Figure_1.1j**: A TH2F plot of the truth top's pT and pseduo-rapidity

EventNTruthJetAndJets
_____________________

This study aims to identify the loss in truth jets by having off-diagonal elements in a 2D plot. 
It also explores the MET vs n-Lepton correlations.

- **Figure_0.1a**: 
  A plot, depicting on a per event basis, the number of truth jets vs reconstructed jets (i.e. observed jets). 
  Ideally, this would be as diagonal as possible to indicate no truth jet loss

- **Figure_0.1b**: A plot illustrating how the number of leptonically decaying tops contribute to the missing transverse momenta of the event.

EventMETImbalance
_________________

A set of plots which explore the missing transverse discrepancy between measurement from the detector simulation and the truth neutrinos.

- **Figure_0.1c**: 
  A 2D plot illustrating non-zero PT components from the 4-top system. 
  This is due to the samples not capturing the partons originating from the colliding protons. 

- **Figure_0.1d**: 
  The angle between the Pz component and the PT of the 4-top system. 
  Ideally, a strong clustering around the 0-rad mark should be observed, anything else is indicating that not all the MET can be accounted for by only looking at truth neutrinos.

- **Figure_0.2d**: 
  The angle between the Pz component and the PT of the 4-top system, after rotating the system according to the imbalance angle.
  This plot is majorly a closure test to assure the rotation was implemented correctly and should yield a peak at 0.

- **Figure_0.1e**: 
  A plot illustrating the distributions of the Missing Energy in the Transverse direction as measured in simulation and reconstructed from Truth Neutrinos.

- **Figure_0.2e**: 
  A plot illustrating the distribution of the missing Energy in the Transverse direction as measured in simulation, but with the truth neutrinos being rotated into a reference frame where the 4-top system momentum balance is zero.
  The observed difference between measurement and truth neutrinos.

- **Figure_0.3e**: 
  A composite plot illustrating a change in the difference between the missing ET (measured) and the truth neutrinos.
  For one of the plots, the truth neutrinos are rotated into the 4-Top reference frame, where as the other has not been rotated.

EventNuNuSolutions
__________________

This study aims to investigate the number of double neutrino solutions obtained when rotating the 4-top system such that, the z-component of the 4-vector points down the beam-pipe.
The number of solutions obtained after rotation is compared to a non-rotation operation.
Only events containing exactly two neutrinos and b-quarks originating from two truth tops are considered, regardless of whether these originate from the resonance.

- **Figure_2.1a**: Number of returned neutrino solutions with and without rotation of the 4-top system.

- **Figure_2.1b**: A TH2F plot of the missing energy in the x and y direction without rotating the truth children into the 4-top system

- **Figure_2.2b**: A TH2F plot of the missing energy in the x and y direction with after rotating the truth children into the 4-top system
  
- **Figure_2.1c**: 
  A mass difference plot of the truth mass and the reconstructed top from neutrino solutions. 
  This plot aims to identify potential patterns when not rotating the reference frame of the truth children into the 4-top system.

- **Figure_2.2c**: A mass difference plot of the truth mass and the reconstructed top from neutrino solutions. 
  This plot aims to identify potential patterns when rotating the reference frame of the truth children into the 4-top system.

- **Figure_2.1d**: A TH2F plot of the MET and truth neutrino's pt with and without rotation.


TopDecayModes
_____________

Plots indicating to which children the Top-Quark decays into. 

- **Figure_2.1a**: A plot depicting the fraction by which the Top-Quark decays into. 

- **Figure_2.1b**: A plot of the reconstructed invariant mass of the tops from their corresponding truth children.

ResonanceMassFromChildren
_________________________

Plots relating to the resonance being reconstructed from the top truth children, where the resonance tops decay either Hadronically, Leptonically or Hadronically-Leptonically.

- **Figure_2.1c**: A plot of the reconstructed resonance from truth children.


TruthChildrenKinematics
_______________________

This selection implementation aims to investigate the delta-R dependency of the parent top PT and how closely clustered the children are together. 

- **Figure_2.1d**: A plot illustrating the :math:`\Delta R` between truth children originating from a common top, but partitioned into resonance/spectator tops.

- **Figure_2.1e**: A plot illustrating the :math:`\Delta R` between originating truth top and decay children partitioned into leptonic and hadronic top decay channels.

- **Figure_2.1f**:
  A plot illustrating the overlap in :math:`\Delta R` between truth children originating and not originating from mutual top. 
  This aims to identify whether only using the delta-R to cluster children causes falsely matched children.
  From the legend, ``False`` implies the parent tops are not equal.

- **Figure_2.1g**: 
  A TH2F plot of the originating top's PT and only hadronically decaying top children delta-R. 
  This aims to verify whether a correlation between the top's PT and the clustering of children is present. 

- **Figure_2.1h**: 
  A TH2F plot of the originating top's PT and only Leptonically decaying top children delta-R. 
  This aims to verify whether a correlation between the top's PT and the clustering of children is present. 

- **Figure_2.1i**: A plot illustrating the fractional PT being transferred to truth children from associated top.

- **Figure_2.1j**: A plot illustrating the fraction of energy being transmitted to the truth children from parent top.


ResonanceMassTruthJets
______________________

Plots the invariant Mass of the injected resonance using truth jets and associated truth leptons.

Event Selection Criteria
------------------------

The general event selections to produce these plots are as follows:

- The event needs to have exactly two tops originating from a resonance 
- If any of the truth jets from a resonant top also contains a non-resonant top contribution, the event is rejected.
- However, if a truth jet contains two tops, and both are marked as resonant, then the event is included.

Figures
-------

- **Figure_3.1a**: 
  A plot of the truth matched reconstructed resonance from truth jets. 
  If the resonance had leptonic tops, the truth lepton and neutrino were added to the truth jets.

- **Figure_3.1b**: 
  A plot of the cutflow statistics. With cutflow keys being:
  - "REJECT -> NOT-TWO-TOPS": Cases where the event passed the initial selection criteria, but the truth jets being selected didn't have a total of two tops. 
  - "Rejected::Selection": Event failed the selection criteria 
  - "Passed::Selection": Event passed the selection criteria 

- **Figure_3.(x)c**: Plots of the truth jet resonance for each decay mode overlaid with the associated truth tops. 
- **Figure_3.1d**: A plot of the number of Truth Jets contributing to the respective resonance decay topology.

ResonanceMassTruthJetsNoSelection
_________________________________

Similar to **ResonanceMassTruthJets** except that no selection criteria is applied (except the basic 4-top event and 2-Resonant tops). 
A few additional kinematic plots are also created, e.g. :math:`\Delta R` between truth jets, n-Tops merged, etc.

- **Figre_3.(x)e**:
  A collection of plots illustrating the invariant mass of the resonance derived from the Truth Jets (with associated leptons and neutrinos if tops decay leptonically) and truth tops. 

- **Figure_3.1f**:
  An invariant mass plot of the resonance formed via different number of top contributions to matched truth jets. 
  This plot aims to identify whether spectator tops merging with signal tops is a significant issue.

- **Figure_3.1g**: 
  A plot which breaks down the above by decay channel, where Had-Had, Had-Lep, Lep-Lep are referring to the purely hadronic, hadronic with leptonic and purely leptonic resonant top decay modes, respectively.


TopMassTruthJets
________________

This study focuses on using truth jets to reconstruct the invariant mass of the originating Truth Top parton. 
For this study, no selections were applied to the sample.

- **Figure_3.1a**: 
  A plot depicting the reconstructed invariant mass of the tops from truth jets via different decay channels. 

- **Figure_3.(x)b**:
  A collection of plots illustrating the invariant mass distribution of reconstructed tops with different number of truth jet contributions.

- **Figure_3.1c**:
  A TH2F plot summarizing plots **Figure_3.(x)b**.

- **Figure_3.1d**:
  A plot showcasing the reconstructed invariant mass dependency on number of tops merging into matched truth jets.

TopTruthJetsKinematics
______________________

A study focused around the kinematics of truth matched truth jets to tops. 

- **Figure_3.1f**:
  A plot depicting the :math:`\Delta R` between truth jets matched to a mutual top, compared to background (non mutual).
  Background in this context implies the :math:`\Delta R` of truth jets not matched to a mutual top.

- **Figure_3.1g**:
  A TH2F plot of the :math:`\Delta R` as a function of the truth top transverse momentum.

- **Figure_3.1h**:
  A TH2F plot of the :math:`\Delta R` as a function of the truth top energy.

- **Figure_3.1i**:
  A composite plot of the :math:`\Delta R` between the truth jet's ghost matched partons partitioned into their pdgid symbol (only for truth jets which are matched to tops).

- **Figure_3.2i**:
  A TH2F plot of the parton's :math:`\Delta R` relative to the truth jet, as a function of :math:`\eta`.
  The region is defined to be this large because it is a closure test of the :math:`\Delta R` calculation between particles.

- **Figure_3.3i**:
  A TH2F plot of the parton's :math:`\Delta R` relative to the truth jet, as a function of :math:`\phi`.
  The region is defined to be this large because it is a closure test of the :math:`\Delta R` calculation between particles.

- **Figure_3.1j**:
  A composite plot of the Energy contributed from Ghost Matched Partons to the Truth Jet.

- **Figure_3.1k**:
  A composite plot illustrating the invariant mass of the top quark derived from truth jets, where truth jets only containing **gluons** have been ignored.

- **Figure_3.1l**:
  A composite plot illustrating the invariant mass of the truth jet, categorized by the number of tops contributing to the associated truth jet.


ResonanceMassJets
_________________

A study focused on using the reco jets to reconstruct the invariant mass of the resonance. 
If the resonant tops decay leptonically, then the truth children leptons are used. 
The selection for this study is set to only pass events with exactly two resonant tops and overall 4-tops at truth level.

- **Figure_4.1a**:
  A plot of the truth matched reconstructed resonance from reco jets. 
  If resonant tops decay leptonically, the truth lepton and neutrino are used along with the associated jets.

- **Figure_4.(x)b**:
  A collection of individual plots of **Figure_4.1a**, with comparable distributions to truth tops and truth jets.

- **Figure_4.1c**:
  A plot illustrating the n-jet composition of individual decay topologies. 
  It is expected that for events where the resonant tops decaying leptonically, fewer jets are contributing to the reconstruction, whereas only hadronic decays would produce more jets.

- **Figure_4.2c**:
  An extension plot of **Figure_4.1c**, where the invariant resonance mass is partitioned into the number of jets contributing to the reconstruction. 

- **Figure_4.1d**:
  A plot illustrating how a given decay topology of the resonant tops impacts cases where associated jets have different tops contributing to them.
  Ideally, each decay topology produces jets which only have one top contributing to the jet, or only two resonant top contributions. 
  Worst case is when both spectator and resonant tops are contributing to the same jet, thus contaminating the reconstructed resonance mass. 
  Ideal cases are marked with a ( * ).

- **Figure_4.2d**:
  A TH2F version of **Figure_4.1d**. 
  Ideal cases are marked with a ( * ).

TopMassJets
___________

A study focusing mostly on reconstructing top quarks from detector based jets and comparing the reconstruction to truth jets. 

- **Figure_4.1a**:
  A plot illustrating the reconstructed invariant top mass from (truth) jets according to their decay topology.

- **Figure_4.1b**:
  A plot indicating the number of (truth) jets contributing to a reconstructed top.
  This plot is used to check whether the number of truth jets and detector jets contributing to a top are similar. 

- **Figure_4.1c**:
  A stack plot of the reconstructed invariant top mass split into the number of jet contributions, along with the decay topology. 

- **Figure_4.1d**:
  A plot of the reconstructed invariant top mass using the leptonic decay mode with truth children leptons and detector leptons (with truth neutrinos).

- **Figure_4.1e**:
  A plot of the reconstructed invariant top mass using only the hadronic decay mode, partitioned into the number of jet contributions.

- **Figure_4.(x)f**:
  A collection of TH2F plots where the average clustering (:math:`\Delta R`) is plotted against the reconstructed invariant top mass. 
  The plots are sorted by decay mode where, Hadronic/Leptonic only are first and second respectively, followed by a combined plot.

MergedTopsTruthJets
___________________

A study dedicated to understanding the parton content of truth matched jets in which multiple tops contribute. 
The primary focus is on hadronically decaying tops, since these appear to be poorly reconstructed. 

- **Figure_3.1a**:
  A plot illustrating the transverse momentum distribution of partons contained in truth jet with multiple top contributions.

- **Figure_3.2a**:
  A plot illustrating the energy distribution of partons contained in truth jet with multiple top contributions.

- **Figure_3.3a**:
  A plot of the :math:`\Delta R` distribution between the truth jet axis and the contributing partons.

- **Figure_3.4a**:
  A heat map of the :math:`\Delta R` between the Truth Jet Axis and the contributing partons as a function of the Parton's energy, where only Gluons are considered.

- **Figure_3.5a**:
  A heat map of the :math:`\Delta R` between the Truth Jet Axis and the contributing partons as a function of the Parton's energy, where Gluons are excluded.

- **Figure_3.1b**:
  A plot illustrating the transverse momentum distribution of truth children matched to truth jets via the contributing partons for truth jet with multiple top contributions.

- **Figure_3.2b**:
  A plot illustrating the energy distribution of truth children matched to truth jets with multiple top contributions.

- **Figure_3.3b**:
  A plot of the :math:`\Delta R` distribution between the contributing parton and matched truth child.

- **Figure_3.4b**:
  A plot of the :math:`\Delta R` distribution between the truth jet axis and matched truth children.

- **Figure_3.5b**:
  A heat map of the :math:`\Delta R` between contributing Partons and the matched Truth Child as a function of the Truth Child's energy, where only Gluons are considered.

- **Figure_3.6b**:
  A heat map of the :math:`\Delta R` between contributing Partons and the matched Truth Child as a function of the Truth Child's energy, where Gluons excluded.
  hlsearch)M

- **Figure_3.1c**:
  A composite plot of how frequently a given parton symbol occurs within a truth jet for top merged jets.

- **Figure_3.2c**:
  A composite plot of the reconstructed invariant top mass from only hadronically decaying tops, partitioned into the number of tops contributing to truth jets.

- **Figure_3.3c**:
  A composite plot of the reconstructed invariant top mass from only hadronically decaying tops, partitioned into the number of tops contributing to truth jets. 
  This plot is used for visualizing a possible bug during sample production. 
  Some truth jets were found to not contain any partons.

- **Figure_3.4c**:
  A composite plot of the fractional energy contributed to a truth jet from a top's parton.
  This plot aims to identify whether there are cases where a given top might be matched to a truth jet, but its energy contribution is insignificant and should probably be unmatched to this truth jet. 

- **Figure_3.5c**:
  A composite plot of the invariant top mass using different energy fraction cuts as shown in **Figure_3.4c**. 
  Considered truth top jets are required to have at least one truth jet with more than one top contribution.

MergedTopsJets
______________

A study dedicated to understanding the parton content of truth matched jets in which multiple tops contribute. 
The primary focus is on hadronically decaying tops, since these appear to be poorly reconstructed. 

- **Figure_4.1a**:
  A plot illustrating the transverse momentum distribution of partons contained in jet with multiple top contributions.

- **Figure_4.2a**:
  A plot illustrating the energy distribution of partons contained in jet with multiple top contributions.

- **Figure_4.3a**:
  A plot of the :math:`\Delta R` distribution between the jet axis and the contributing partons.

- **Figure_4.4a**:
  A heat map of the :math:`\Delta R` between the Jet Axis and the contributing partons as a function of the Parton's energy, where only Gluons are considered.

- **Figure_4.5a**:
  A heat map of the :math:`\Delta R` between the Jet Axis and the contributing partons as a function of the Parton's energy, where Gluons are excluded.

- **Figure_4.1b**:
  A plot illustrating the transverse momentum distribution of truth children matched to jets via the contributing partons for jet with multiple top contributions.

- **Figure_4.2b**:
  A plot illustrating the energy distribution of truth children matched to jets with multiple top contributions.

- **Figure_4.3b**:
  A plot of the :math:`\Delta R` distribution between the contributing parton and matched truth child.

- **Figure_4.4b**:
  A plot of the :math:`\Delta R` distribution between the jet axis and matched truth children.

- **Figure_4.5b**:
  A heat map of the :math:`\Delta R` between contributing Partons and the matched Truth Child as a function of the Truth Child's energy, where only Gluons are considered.

- **Figure_4.6b**:
  A heat map of the :math:`\Delta R` between contributing Partons and the matched Truth Child as a function of the Truth Child's energy, where Gluons excluded.

- **Figure_4.1c**:
  A composite plot of how frequently a given parton symbol occurs within a jet for top merged jets.

- **Figure_4.2c**:
  A composite plot of the reconstructed invariant top mass from only hadronically decaying tops, partitioned into the number of tops contributing to jets.

- **Figure_4.3c**:
  A composite plot of the reconstructed invariant top mass from only hadronically decaying tops, partitioned into the number of tops contributing to jets. 
  This plot is used for visualizing a possible bug during sample production. 
  Some jets were found to not contain any partons.

- **Figure_4.4c**:
  A composite plot of the fractional energy contributed to a jet from a top's parton, partitioned into the number of tops contributing to given jet.
  This plot aims to identify whether there are cases where a given top is matched to a jet but its energy contribution might be insignificant and should probably be unmatched to this jet. 

- **Figure_4.5c**:
  A composite plot of the invariant top mass using different energy fraction cuts as shown in **Figure_4.4c**. 
  Considered truth top jets are required to have at least one jet with more than one top contribution.

