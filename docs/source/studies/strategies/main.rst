Double Leptonic Resonance Decay Analysis
========================================

This small analysis script aims to reconstruct the mass of the heavy vector/scalar H/Z boson, using a primitive grouping algorithm. 

Selection Criteria
------------------

Events are required to have at least two leptons and four b-jets. 

Grouping Strategy
-----------------

To seed the grouping, the two leading order, b-tagged partons are used to indicate the presence of at least 2-tops. 
The seeded b-tagged partons are considered as the `Resonance` top pairs, which are emitted from the heavy resonance. 
For candidate seeds closest to an adjacent quark parton (or jet), then the associated object will be marked as a hadronically decaying top quark. 
Whereas, if the :math:`\Delta R` is lowest between a leptonic object, then the b-tagged object will be tagged as originating from a leptonically decaying top quark. 
This procedure is repeated for all b-tagged objects, until no further clustering is possible. 
If there are two leptonically decaying tops, then the double neutrino reconstruction algorithm will be invoked to restore the neutrino momenta. 

Multiple Neutrino Reconstruction Solutions
------------------------------------------

If the event yields multiple solutions for the single or double neutrino reconstruction, then the neutrino with the lowest chi2 is chosen and others are neglected.
For no solution events, the entire event is rejected.

Parameters
----------

- **btagger**: 
  This selects the btagging algorithm which should be used on the particles.
  Options are: 
  
  - ``is_b``: Nominal method on truth children 
  - ``btag_DL1r_60``: Use the Deep Learning algorithm -r at a working point of 60
  - ``btag_DL1r_77``: Use the Deep Learning algorithm -r at a working point of 77
  - ``btag_DL1r_85``: Use the Deep Learning algorithm -r at a working point of 85
  - ``btag_DL1_60``: Use the Deep Learning algorithm at a working point of 60
  - ``btag_DL1_77``: Use the Deep Learning algorithm at a working point of 77
  - ``btag_DL1_85``: Use the Deep Learning algorithm at a working point of 85

- **truth**: 
  This selects the truth level to apply the analysis on. 
  Options are limited to; 

  - ``truth``
  - ``jets+truthleptons``
  - ``detector``
