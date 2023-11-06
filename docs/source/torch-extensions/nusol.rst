.. role:: python(code)
   :language: python 

Single/Double Neutrino Reconstruction
*************************************

This module is related to the analytical neutrino reconstruction algorithm published under **1305.1878v2**.
The paper discuses an analytical approach to reconstructing single and double neutrino momenta in the context of top-quark decay modes.
Based on the event's missing transverse energy, leptons and b-quarks, possible neutrinos are modeled using ellipses. 
In the single neutrino case, possible neutrino solutions are constrained by selecting the lowest :math:`\chi^2`, given the W-boson, top-quark and neutrino masses.
As for the double neutrino case, pairs of b-quarks and leptons are used to model two ellipses, where the intersection of these indicates possible neutrino candidates.

The module is a complete reimplementation of the pre-existant source code provided by the authors in native C++ and CUDA, thus enhacing the computational speeds of the algorithm, making it viable for machine learning purposes.
Similar to other modules of this package, input arguments are split into combined and separate particle tensors, without incurring performance penalities.


Single Neutrino Reconstruction
______________________________

.. py:function:: pyc.NuSol.Polar.Nu(pmu_b, pmu_mu, met_phi, masses, sigma, null = 10e-10) -> list[torch.tensor]

    Computes candidate neutrino 3-vector solutions of a given b-quark/jet and matched lepton.
    The return type is a list of tensors, with the following index values:

    * :python:`list[0]`: Candidate neutrino solution 3-vector.
    * :python:`list[1]`: The resulting chi2 value of the respective neutrino candidate.

    :param torch.tensor pmu_b: The four vector of the b-quark/b-jet (pt, eta, phi, e)
    :param torch.tensor pmu_mu: The four vector of the lepton matched to the b-quark/b-jet (pt, eta, phi, e)
    :param torch.tensor met_phi: The scalar value of missing transverse energy and the azimuthal angle.


    :param torch.tensor masses: The masses of the W-boson (80.385 GeV), top-quark (172.62 GeV), neutrino (0 GeV).
    :param torch.tensor sigma: An uncertainty matrix of the missing transverse energy resolution of the event (example: [[100, 0, 0, 100]])
    :param float null: An adjustable parameter indicating the cut-off chi2 values.
    :return list[torch.tensor]: List of solutions and associated chi2 values.    


.. py:function:: pyc.NuSol.Polar.Nu(pt_b, eta_b, phi_b, e_b, pt_mu, eta_mu, phi_mu, e_mu, met, phi, masses, sigma, float null = 10e-10) -> list[torch.tensor]

    Computes candidate neutrino 3-vector solutions of a given b-quark/jet and matched lepton.
    The return type is a list of tensors, with the following index values:

    * :python:`list[0]`: Candidate neutrino solution 3-vector.
    * :python:`list[1]`: The resulting chi2 value of the respective neutrino candidate.


    :param torch.tensor pt_b: The transverse momenta of the b-quark/jet.
    :param torch.tensor eta_b: The pseudo-rapidity of the b-quark/jet.
    :param torch.tensor phi_b: The Azimuthal angle of the b-quark/jet.
    :param torch.tensor e_b: The energy of the b-quark/jet.

    :param torch.tensor pt_mu: The transverse momenta of the matched lepton.
    :param torch.tensor eta_mu: The pseudo-rapidity of the matched lepton.
    :param torch.tensor phi_mu: The Azimuthal angle of the matched lepton.
    :param torch.tensor e_mu: The energy of the matched lepton.

    :param torch.tensor met: The scalar value of the missing transverse energy.
    :param torch.tensor phi: The azimuthal angle of the missing transverse energy.

    :param torch.tensor masses: The masses of the W-boson (80.385 GeV), top-quark (172.62 GeV), neutrino (0 GeV).
    :param torch.tensor sigma: An uncertainty matrix of the missing transverse energy resolution of the event (example: [[100, 0, 0, 100]])
    :param float null: An adjustable parameter indicating the cut-off chi2 values.
    :return list[torch.tensor]: List of solutions and associated chi2 values.    


.. py:function:: pyc.NuSol.Cartesian.Nu(pmc_b, pmc_mu, met_xy, masses, sigma, null = 10e-10) -> list[torch.tensor]

    Computes candidate neutrino 3-vector solutions of a given b-quark/jet and matched lepton.
    The return type is a list of tensors, with the following index values:

    * :python:`list[0]`: Candidate neutrino solution 3-vector.
    * :python:`list[1]`: The resulting chi2 value of the respective neutrino candidate.

    :param torch.tensor pmc_b: The four vector of the b-quark/b-jet (px, py, pz, e)
    :param torch.tensor pmc_mu: The four vector of the lepton matched to the b-quark/b-jet (px, py, pz, e)
    :param torch.tensor met_xy: The scalar value of missing transverse energy in the x and y direction of the detector.

    :param torch.tensor masses: The masses of the W-boson (80.385 GeV), top-quark (172.62 GeV), neutrino (0 GeV).
    :param torch.tensor sigma: An uncertainty matrix of the missing transverse energy resolution of the event (example: [[100, 0, 0, 100]])
    :param float null: An adjustable parameter indicating the cut-off chi2 values.
    :return list[torch.tensor]: List of solutions and associated chi2 values. 


.. py:function:: pyc.NuSol.Cartesian.Nu(px_b, py_b, pz_b, e_b, px_mu, py_mu, pz_mu, e_mu, met_x, met_y, masses, sigma, float null = 10e-10) -> list[torch.tensor]

    Computes candidate neutrino 3-vector solutions of a given b-quark/jet and matched lepton.
    The return type is a list of tensors, with the following index values:

    * :python:`list[0]`: Candidate neutrino solution 3-vector.
    * :python:`list[1]`: The resulting chi2 value of the respective neutrino candidate.

    :param torch.tensor px_b: The momenta of the b-quark/jet in the x direction.
    :param torch.tensor py_b: The momenta of the b-quark/jet in the y direction.
    :param torch.tensor pz_b: The momenta of the b-quark/jet in the z direction.
    :param torch.tensor e_b: The energy of the b-quark/jet.

    :param torch.tensor px_mu: The momenta of the matched lepton in the x direction.
    :param torch.tensor py_mu: The momenta of the matched lepton in the y direction.
    :param torch.tensor pz_mu: The momenta of the matched lepton in the z direction.
    :param torch.tensor e_mu: The energy of the matched lepton.

    :param torch.tensor met_x: The missing transverse energy in the x direction.
    :param torch.tensor met_y: The missing transverse energy in the y direction.

    :param torch.tensor masses: The masses of the W-boson (80.385 GeV), top-quark (172.62 GeV), neutrino (0 GeV).
    :param torch.tensor sigma: An uncertainty matrix of the missing transverse energy resolution of the event (example: [[100, 0, 0, 100]])
    :param float null: An adjustable parameter indicating the cut-off chi2 values.
    :return list[torch.tensor]: List of solutions and associated chi2 values.    


Double Neutrino Reconstruction
______________________________

.. py:function:: pyc.NuSol.Polar.NuNu(pmu_b1, pmu_b2, pmu_mu1, pmu_mu2, met_phi, masses, null = 10e-10) -> list[torch.tensor]

    Computes candidate neutrino 3-vector solutions of a given b-quark/jet and matched lepton pairs.
    The return type is a list of tensors, with the following index values:

    * :python:`list[0]`: Candidate neutrino 3-vector solutions for the first b-quark/jet and lepton pair.
    * :python:`list[1]`: Candidate neutrino 3-vector solutions for the second b-quark/jet and lepton pair.
    * :python:`list[2]`: Diagonal distance values for the respective solution pairs.
    * :python:`list[3]`: The normal vector used to derive the neutrino 3-vectors (n_perp).
    * :python:`list[4]`: The perpendicular neutrino 3-vector solution set for the first b-quark/jet and lepton pair (H_perp1).
    * :python:`list[5]`: The perpendicular neutrino 3-vector solution set for the second b-quark/jet and lepton pair (H_perp2).
    * :python:`list[6]`: A boolean mask indicating no solutions were found given the specified null limit.

    :param torch.tensor pmu_b1: The four vector of the first b-quark/b-jet (pt, eta, phi, e)
    :param torch.tensor pmu_b2: The four vector of the second b-quark/b-jet (pt, eta, phi, e)

    :param torch.tensor pmu_mu1: The four vector of the first lepton matched to the b-quark/b-jet (pt, eta, phi, e)
    :param torch.tensor pmu_mu2: The four vector of the second lepton matched to the b-quark/b-jet (pt, eta, phi, e)

    :param torch.tensor met_phi: The scalar value of missing transverse energy and the azimuthal angle.
    :param torch.tensor masses: The masses of the W-boson (80.385 GeV), top-quark (172.62 GeV), neutrino (0 GeV).

    :param float null: An adjustable parameter indicating the cut-off distance value.
    :return list[torch.tensor]: List of neutrino solutions. 

.. py:function:: pyc.NuSol.Polar.NuNu(pt_b1, eta_b1, phi_b1, e_b1, pt_b2, eta_b2, phi_b2, e_b2, pt_mu1, eta_mu1, phi_mu1, e_mu1, pt_mu2, eta_mu2, phi_mu2, e_mu2, met, phi, masses, null = 10e-10) -> list[torch.tensor]

    Computes candidate neutrino 3-vector solutions of a given b-quark/jet and matched lepton pairs.
    The return type is a list of tensors, with the following index values:

    * :python:`list[0]`: Candidate neutrino 3-vector solutions for the first b-quark/jet and lepton pair.
    * :python:`list[1]`: Candidate neutrino 3-vector solutions for the second b-quark/jet and lepton pair.
    * :python:`list[2]`: Diagonal distance values for the respective solution pairs.
    * :python:`list[3]`: The normal vector used to derive the neutrino 3-vectors (n_perp).
    * :python:`list[4]`: The perpendicular neutrino 3-vector solution set for the first b-quark/jet and lepton pair (H_perp1).
    * :python:`list[5]`: The perpendicular neutrino 3-vector solution set for the second b-quark/jet and lepton pair (H_perp2).
    * :python:`list[6]`: A boolean mask indicating no solutions were found given the specified null limit.

    :param torch.tensor pt_b1: The transverse momenta of the b-quark/jet.
    :param torch.tensor eta_b1: The pseudo-rapidity of the b-quark/jet.
    :param torch.tensor phi_b1: The Azimuthal angle of the b-quark/jet.
    :param torch.tensor e_b1: The energy of the b-quark/jet.

    :param torch.tensor pt_b2: The transverse momenta of the b-quark/jet.
    :param torch.tensor eta_b2: The pseudo-rapidity of the b-quark/jet.
    :param torch.tensor phi_b2: The Azimuthal angle of the b-quark/jet.
    :param torch.tensor e_b2: The energy of the b-quark/jet.


    :param torch.tensor pt_mu1: The transverse momenta of the matched lepton.
    :param torch.tensor eta_mu1: The pseudo-rapidity of the matched lepton.
    :param torch.tensor phi_mu1: The Azimuthal angle of the matched lepton.
    :param torch.tensor e_mu1: The energy of the matched lepton.

    :param torch.tensor pt_mu2: The transverse momenta of the matched lepton.
    :param torch.tensor eta_mu2: The pseudo-rapidity of the matched lepton.
    :param torch.tensor phi_mu2: The Azimuthal angle of the matched lepton.
    :param torch.tensor e_mu2: The energy of the matched lepton.

    :param torch.tensor met: The scalar value of the missing transverse energy.
    :param torch.tensor phi: The azimuthal angle of the missing transverse energy.

    :param torch.tensor masses: The masses of the W-boson (80.385 GeV), top-quark (172.62 GeV), neutrino (0 GeV).

    :param float null: An adjustable parameter indicating the cut-off distance value.
    :return list[torch.tensor]: List of neutrino solutions. 


.. py:function:: pyc.NuSol.Cartesian.NuNu(pmc_b1, pmc_b2, pmc_mu1, pmc_mu2, met_xy, masses, null = 10e-10) -> list[torch.tensor]

    Computes candidate neutrino 3-vector solutions of a given b-quark/jet and matched lepton pairs.
    The return type is a list of tensors, with the following index values:

    * :python:`list[0]`: Candidate neutrino 3-vector solutions for the first b-quark/jet and lepton pair.
    * :python:`list[1]`: Candidate neutrino 3-vector solutions for the second b-quark/jet and lepton pair.
    * :python:`list[2]`: Diagonal distance values for the respective solution pairs.
    * :python:`list[3]`: The normal vector used to derive the neutrino 3-vectors (n_perp).
    * :python:`list[4]`: The perpendicular neutrino 3-vector solution set for the first b-quark/jet and lepton pair (H_perp1).
    * :python:`list[5]`: The perpendicular neutrino 3-vector solution set for the second b-quark/jet and lepton pair (H_perp2).
    * :python:`list[6]`: A boolean mask indicating no solutions were found given the specified null limit.

    :param torch.tensor pmc_b1: The four vector of the first b-quark/b-jet (px, py, pz, e)
    :param torch.tensor pmc_b2: The four vector of the second b-quark/b-jet (px, py, pz, e)

    :param torch.tensor pmc_mu1: The four vector of the first lepton matched to the b-quark/b-jet (px, py, pz, e)
    :param torch.tensor pmc_mu2: The four vector of the second lepton matched to the b-quark/b-jet (px, py, pz, e)

    :param torch.tensor met_xy: The scalar value of missing transverse energy in the x and y direction of the detector.
    :param torch.tensor masses: The masses of the W-boson (80.385 GeV), top-quark (172.62 GeV), neutrino (0 GeV).

    :param float null: An adjustable parameter indicating the cut-off distance value.
    :return list[torch.tensor]: List of neutrino solutions. 

.. py:function:: pyc.NuSol.Cartesian.NuNu(px_b1, py_b1, pz_b1, e_b1, px_b2, py_b2, pz_b2, e_b2, px_mu1, py_mu1, pz_mu1, e_mu1, px_mu2, py_mu2, pz_mu2, e_mu2, met_x, met_y, masses, null = 10e-10) -> list[torch.tensor]

    Computes candidate neutrino 3-vector solutions of a given b-quark/jet and matched lepton pairs.
    The return type is a list of tensors, with the following index values:

    * :python:`list[0]`: Candidate neutrino 3-vector solutions for the first b-quark/jet and lepton pair.
    * :python:`list[1]`: Candidate neutrino 3-vector solutions for the second b-quark/jet and lepton pair.
    * :python:`list[2]`: Diagonal distance values for the respective solution pairs.
    * :python:`list[3]`: The normal vector used to derive the neutrino 3-vectors (n_perp).
    * :python:`list[4]`: The perpendicular neutrino 3-vector solution set for the first b-quark/jet and lepton pair (H_perp1).
    * :python:`list[5]`: The perpendicular neutrino 3-vector solution set for the second b-quark/jet and lepton pair (H_perp2).
    * :python:`list[6]`: A boolean mask indicating no solutions were found given the specified null limit.

    :param torch.tensor px_b1: The momenta of the b-quark/jet in the x direction.
    :param torch.tensor py_b11: The momenta of the b-quark/jet in the y direction.
    :param torch.tensor pz_b1: The momenta of the b-quark/jet in the z direction.
    :param torch.tensor e_b1: The energy of the b-quark/jet.

    :param torch.tensor px_b2: The momenta of the matched lepton in the x direction.
    :param torch.tensor py_b2: The momenta of the matched lepton in the y direction.
    :param torch.tensor pz_b2: The momenta of the matched lepton in the z direction.
    :param torch.tensor e_b2: The energy of the matched lepton.

    :param torch.tensor px_mu1: The momenta of the b-quark/jet in the x direction.
    :param torch.tensor py_mu1: The momenta of the b-quark/jet in the y direction.
    :param torch.tensor pz_mu1: The momenta of the b-quark/jet in the z direction.
    :param torch.tensor e_mu1: The energy of the b-quark/jet.

    :param torch.tensor px_mu2: The momenta of the matched lepton in the x direction.
    :param torch.tensor py_mu2: The momenta of the matched lepton in the y direction.
    :param torch.tensor pz_mu2: The momenta of the matched lepton in the z direction.
    :param torch.tensor e_mu2: The energy of the matched lepton.

    :param torch.tensor met_x: The missing transverse energy in the x direction.
    :param torch.tensor met_y: The missing transverse energy in the y direction.

    :param torch.tensor masses: The masses of the W-boson (80.385 GeV), top-quark (172.62 GeV), neutrino (0 GeV).

    :param float null: An adjustable parameter indicating the cut-off distance value.
    :return list[torch.tensor]: List of neutrino solutions. 


