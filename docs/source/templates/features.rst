.. role:: python(code)
   :language: python 

Applying Graph Features
***********************

A simple feature function which has pre-defined edge/node/graph feature functions that automatically populate a graph based on truth level.
This function can be easily extended as will be highlighted later in the documentation.


.. py:function:: ApplyFeatures(Analysis inpt, Level = None)

    :param Analysis inpt: The Analysis instance to which a **GraphTemplate** is attached.
    :param None, str Level: The truth level of the **GraphTemplate** particles. Options are:

        * :python:`TruthTops`: 
          Expects a graph containing truth tops. If none are present, the graph will be empty.

        * :python:`TruthChildren`:
          Expects truth tops to be matched to their direct decay products (known as their children). 
          Similar to the tops, if none are present in the event, the graph will be empty and skipped.

        * :python:`TruthJets`:
          Expects a **GraphTemplate** containing truth jets. These are the non-detector convoluted jets.

        * :python:`Jets`:
          Expects a **GraphTemplate** containing detector based jets.


A collection of pre-built **GraphTemplate** implementations compatible with the above inputs can be found under; **src/Events/Graphs/EventGraphs.py**.
Since collection Graphs are part of the package, they can be imported via :python:`from AnalysisG.Events import *`.
A short description of these is given below:

- :python:`GraphTops`:
  An implementation using only event truth tops. These are considered to be the generator particles.

- :python:`GraphChildren`: 
  The implementation uses the immediate decay products of the generator tops, if the top decays leptonically, the immediate decay products of the **W** boson are used, for example neutrinos and leptons.

- :python:`GraphChildrenNoNu`:
  A graph implementation similar to **GraphChildren**, but without neutrinos.

- :python:`GraphTruthJet`:
  Replaces the children, except the leptons and neutrinos, with truth jets of the detector.

- :python:`GraphTruthJetNoNu`:
  A graph implementation similar to **GraphTruthJet**, but without neutrinos.

- :python:`GraphJet`:
  Replaces the children, except the leptons and neutrinos, with jets of the detector.

- :python:`GraphJetNoNu`:
  A graph implementation similar to **GraphJet**, but without neutrinos.

- :python:`GraphDetector`:
  The final graph version as would be expected in real data. No truth particles are used.

Applied Features to Each Graph Category
_______________________________________

This section highlights the expected graph features, which are automatically added to the aforementioned graph objects.
The usual syntax also applies to these graphs where, **E**, **N** and **G** prefixes imply **edge**, **node** and **graph** features.
Features containing a **T** are dedicated for truth information, that is used to train a supervised neural network.

.. py:class:: TruthTops

    This section indicates the truth graph features used to train the neural network against.

    :param torch.tensor E_T_res_edge: Indicates whether the edge connecting the tops are from a resonance particle.
    :param torch.tensor N_T_res_node: Indicates whether the given particle is from a resonance particle.
    :param torch.tensor G_T_signal: Indicates whether the event as a whole is a signal graph.
    :param torch.tensor G_T_ntops: Indicates the number of tops within the graph.

    This section reserved for features used as input to the neural network.
    
    :param torch.tensor N_eta: The pseudo-rapidity of the particle.
    :param torch.tensor N_energy: The energy of the particle.
    :param torch.tensor N_pT: The transverse momenta of the particle.
    :param torch.tensor N_phi: The azimuthal angle of the particle within the detector.

    :param torch.tensor G_met: The missing transverse energy of the ATLAS detector. This contribution is expected to be associated with neutrino production.
    :param torch.tensor G_phi: The azimuthal angle of the missing transverse energy.

.. py:class:: GraphChildren

    This section indicates the truth children graph features used to train the neural network against.
        
    :param torch.tensor E_T_res_edge: Indicates whether the edge connecting the children are from a resonance top.
    :param torch.tensor E_T_top_edge: Indicates whether the children come from a mutual top.
    :param torch.tensor E_T_lep_edge: Indicates whether the children have a leptonic decay mode.

    :param torch.tensor N_T_res_node: Indicates whether this particle is from a resonance.

    :param torch.tensor G_T_signal: Indicates if the event has a resonance particle.
    :param torch.tensor G_T_ntop: Number of tops in the event.
    :param torch.tensor G_T_n_nu: Number of neutrinos within the event.

    :param torch.tensor N_eta: The pseudo-rapidity of the particle.
    :param torch.tensor N_energy: The energy of the particle.
    :param torch.tensor N_pT: The transverse momenta of the particle.
    :param torch.tensor N_phi: The azimuthal angle of the particle within the detector.

    :param torch.tensor N_is_b: Whether the given particle is a b-quark.
    :param torch.tensor N_is_lep: Whether the given particle is a lepton.
    :param torch.tensor N_is_nu: Whether the given particle is a neutrino.

    :param torch.tensor G_met: The missing transverse energy of the ATLAS detector. This contribution is expected to be associated with neutrino production.
    :param torch.tensor G_phi: The azimuthal angle of the missing transverse energy.
    :param torch.tensor G_n_lep: Number of leptons within the event.
    :param torch.tensor G_n_jets: Number of jets within the event.


