Neutrino Reconstruction
***********************
The aim of this study is to benchmark the performance of the neutrino reconstruction algorithm found under [1].

Selection Criteria:
___________________

Events are required to have no more than two leptonically decaying tops. 
These are filtered at truth level (TruthChildren). 
The neutrino algorithm ``zero`` value is being set to 1e-10, since anything below this value creates large differences between C++ and Python floating point definitions.

Particle Definitions:
_____________________

Leptons and neutrinos are defined as:

- electrons
- muons 
- taus

Created Plots:
______________

- ``neutrino-solutions``:
    This will be a TH1F plot which aims to identify differences in using MeV and GeV when executing the reconstruction algorithm on dilepton top decay modes.  reconstructing dilepton top decay modes. 

- ``top-dilepton``:
    This plot illustrates how the reconstructed invariant top mass changes with MeV and GeV in the context to a dilepton :math:`t\bar{t}` decay mode. 
    Using MeV seems to return more solutions. 

- ``top-singlelepton``:
    A plot illustrating the reconstructed invariant top mass in single leptonic top decay modes. 

- ``H-dilepton``:
    A plot illustrating the reconstructed heavy scalar H boson, with both resonant tops decay leptonically. 

- ``top-double-kin-px_py-mev``:
    A TH2F plot used to check whether the kinematic momentum vector in the x and y direction (i.e. PT) of the reconstructed tops are consistent with that of the truth tops.
    The error is calculated based on the absolute difference between truth and prediction, and normalized by the truth vector.
    Mathematically:
    :math:`\frac{(px_{truth} - px_{pred})}{px_{truth}} \times 100`

- ``top-double-kin-px_py-gev``:
    Same as above, but using GeV for the particle's 4-vector.

- ``top-double-kin-pz_e-mev``
    Same as above, but using MeV and using the pz and energy of the particle.
    The energy will be correlated, since the neutrino is assumed to have no mass.

- ``top-double-kin-pz_e-gev``
    Same as above, but using GeV and using the pz and energy of the particle.
    The energy will be correlated, since the neutrino is assumed to have no mass.


[1]. **Analytic solutions for neutrino momenta in decay of top quarks** (arXiv: 1305.1878v2)
