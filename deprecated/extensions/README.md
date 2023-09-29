# PyTorchCustom
## Introduction:
This part of the AnalysisTopGNN repository is used to write PyTorch extension code in a modular way. 
The primary focus is to port and unify already written code in the repository into one single package, such that alternative algorithms can easily integrate highly optimized Physics centric CUDA/C++ code.

## Packages:
- Transform: A namespace used to transform between ATLAS's coordinate system back to cartesian and vice versa.
- Operators: Optimized PyTorch code used to apply to arbitrary vectors, and speed up common function calls, such as dot products. 
- Physics: A namesapce used to write Physics centric functions, that are used to extract relevant quantities from vectors.
- NuRecon: A namespace dedicated to Single and Double Neutrino reconstruction. The algorithm is a reimplementation of arXiv: 1305.1878v2.

## How To Use:
```bash 
pip install . 
```

## Python Importation Directory:
### Transform:
- PyC.Transform.Floats
- PyC.Transform.Tensors
- PyC.Transform.CUDA

#### Functions:
- Description: Conversion to Cartesian System
```python 
Px(pt, phi) -> Tensor(n x 1)
```
```python 
Py(pt, phi) -> Tensor(n x 1)
```
```python 
Pz(pt, eta) -> Tensor(n x 1)
```
- Description: Conversion to Cartesian System simultaneously 
```python 
PxPyPz(pt, eta, phi) -> Tensor(n x 3 - (Px, Py, Pz))
```

- Description: Conversion to ATLAS System
```python 
PT(px, py) -> Tensor(n x 1)
```
```python 
Eta(px, py, pz) -> Tensor(n x 1)
```
```python 
Phi(px, py) -> Tensor(n x 1)
```

- Description: Conversion to ATLAS System simultaneously 
```python 
PtEtaPhi(px, py, pz) -> Tensor(n x 3 - (Pt, Eta, Phi))
```

### Operators:
- PyC.Operators.Tensors
- PyC.Operators.CUDA 

#### Functions:
- Description: Computes the Dot product of a n x d tensor 
```python 
Dot(tensor v1, tensor v2) -> Tensor(n x 1)
```

- Description: Computes the CosTheta/SinTheta between two vectors 
```python 
CosTheta(tensor v1, tensor v2) -> Tensor(n x 1)
```
```python 
SinTheta(tensor v1, tensor v2) -> Tensor(n x 1)
```

- Description: Computes a n x 3 x 3 Rotation matrix.
```python 
Rx(tensor angle)
```
```python 
Ry(tensor angle)
```
```python 
Rz(tensor angle)
```

- (CUDA Only) Description: Computes the Cofactors of a n x 3 x 3 matrix.
```python 
Cofactor(tensor v1) -> Tensor(n x 3 x 3)
```
- (CUDA Only) Description: Computes the Determinant of a matrix from Cofactors.
```python 
Determinant(tensor Cofactors, tensor Matrix) -> Tensor(n x 1)
```
- (CUDA Only) Description: Computes the Inverse of a n x 3 x 3 matrix.
```python 
Inverse(tensor Cofactors, tensor Determinant) -> Tensor(n x 3 x 3)
```
- (CUDA Only) Description: Computes the Inverse of a n x 3 x 3 matrix.
```python 
Inv(tensor Matrix) -> Tensor(n x 3 x 3)
```
- (CUDA Only) Description: Computes the Determinant of a n x 3 x 3 matrix.
```python 
Det(tensor Matrix) -> Tensor(n x 1)
```

### Physics:
- PyC.Physics.Tensors.Cartesian
- PyC.Physics.Tensors.Polar 
- PyC.Physics.CUDA.Cartesian 
- PyC.Physics.CUDA.Polar 

#### Functions:
- Description: Computes the magnitude (Square) of the vector.
```python 
P2(tensor px, tensor py, tensor pz) -> Tensor(n x 1)
P2(tensor pt, tensor eta, tensor phi) -> Tensor(n x 1)
```
```python 
P(tensor px, tensor py, tensor pz) -> Tensor(n x 1)
P(tensor pt, tensor eta, tensor phi) -> Tensor(n x 1)
```
- Description: Computes the ratio (Square) between the velocity and the speed of light.
```python 
Beta2(tensor px, tensor py, tensor pz, tensor e) -> Tensor(n x 1)
Beta2(tensor pt, tensor eta, tensor phi, tensor e) -> Tensor(n x 1)
```
```python 
Beta(tensor px, tensor py, tensor pz, tensor e) -> Tensor(n x 1)
Beta(tensor pt, tensor eta, tensor phi, tensor e) -> Tensor(n x 1)
```

- Description: Computes the invariant mass (Square) of particle vector.
```python 
M2(tensor px, tensor py, tensor pz, tensor e) -> Tensor(n x 1)
M2(tensor pt, tensor eta, tensor phi, tensor e) -> Tensor(n x 1)
```
```python 
M(tensor px, tensor py, tensor pz, tensor e) -> Tensor(n x 1)
M(tensor pt, tensor eta, tensor phi, tensor e) -> Tensor(n x 1)
```
```python 
Mass(tensor Pmu(px, py, pz, e)) -> Tensor(n x 1)
Mass(tensor Pmu(pt, eta, phi, e)) -> Tensor(n x 1)
```
- Description: Computes the transverse mass (Square) of particle vector.
```python 
Mt2(tensor pz, tensor e) -> Tensor(n x 1)
Mt2(tensor pt, tensor eta, tensor e) -> Tensor(n x 1)
```
```python 
Mt(tensor pz, tensor e) -> Tensor(n x 1)
Mt(tensor pt, tensor eta, tensor e) -> Tensor(n x 1)
```

- Description: Computes the angle of a vector.
```python 
Theta(tensor px, tensor py, tensor pz)) -> Tensor(n x 1)
Theta(tensor pt, tensor eta, tensor phi)) -> Tensor(n x 1)
```

- Description: Computes the deltaR between two particle vectors.
```python 
DeltaR(tensor px1, tensor px2, tensor py1, tensor py2, tensor pz1, tensor pz2)) -> Tensor(n x 1)
DeltaR(tensor eta1, tensor eta2, tensor phi1, tensor phi2)) -> Tensor(n x 1)
```

### NuRecon:
- PyC.NuSol.Tensors
- PyC.NuSol.CUDA

#### Functions:
- Description: Analytically computes the Single Neutrino from the collision event's missing ET, b-quark, lepton and uncertainty matrix S.
```python 
NuPtEtaphiE(tensor b(pt, eta, phi, e), tensor lep(pt, eta, phi, e), 
	    tensor met, tensor met_phi, tensor Sxx, tensor Sxy, tensor Syx, tensor Syy, 
	    tensor massTop, tensor massW, tensor massNu, double cutoff) -> list(Tensor) -> [SkipEvent, neutrino cartesian momentum 3-vector, Chi2, Other unsorted Solutions]

NuPxPyPzE(tensor b(px, py, pz, e), tensor lep(px, py, pz, e), 
	  tensor met_x, tensor met_y, tensor Sxx, tensor Sxy, tensor Syx, tensor Syy, 
	  tensor massTop, tensor massW, tensor massNu, double cutoff) -> list(Tensor) -> [SkipEvent, neutrino cartesian momentum 3-vector, Chi2, Other unsorted Solutions]

NuDoublePtEtaPhiE(double b_pt, double b_eta, double b_phi, double b_e, 
		  double lep_pt, double lep_eta, double lep_phi, double lep_e, 
		  double met, double met_phi, double Sxx, double Sxy, double Syx, double Syy, 
		  double massTop, double massW, double massNu, double cutoff) -> list(Tensor) -> [SkipEvent, neutrino cartesian momentum 3-vector, Chi2, Other unsorted Solutions]

NuDoublePxPyPzE(double b_px, double b_py, double b_pz, double b_e, 
		double lep_px, double lep_py, double lep_pz, double lep_e, 
		double met_px, double met_py, double Sxx, double Sxy, double Syx, double Syy, 
		double massTop, double massW, double massNu, double cutoff) -> list(Tensor) -> [SkipEvent, neutrino cartesian momentum 3-vector, Chi2, Other unsorted Solutions]

NuListDoublePtEtaPhiE([[b_pt, b_eta, b_phi, b_e]], [[lep_pt, lep_eta, lep_phi, lep_e]], 
		      [[met, met_phi]], [[Sxx, Sxy, Syx, Syy]], [[massTop, massW, massNu]], 
		      double cutoff) -> list(Tensor) -> [SkipEvent, neutrino cartesian momentum 3-vector, Chi2, Other unsorted Solutions]

NuListDoublePxPyPzE([[b_px, b_py, b_pz, b_e]], [[lep_px, lep_py, lep_pz, lep_e]], 
		      [[met_px, met_py]], [[Sxx, Sxy, Syx, Syy]], [[massTop, massW, massNu]], 
		      double cutoff) -> list(Tensor) -> [SkipEvent, neutrino cartesian momentum 3-vector, Chi2, Other unsorted Solutions]

```
- Description: Analytically Reconstructs two Neutrinos from the collision event's missing ET, b-quarks and leptons.
```python 
NuNuPtEtaphiE(tensor b1(pt, eta, phi, e), tensor b2(pt, eta, phi, e), tensor lep1(pt, eta, phi, e), tensor lep2(pt, eta, phi, e), 
	    tensor met, tensor met_phi, tensor massTop, tensor massW, tensor massNu, 
	    double cutoff) -> list(Tensor) -> [SkipEvent, neutrino1 cartesian momentum 3-vector, neutrino2 cartesian momentum 3-vector, neutrino1 perpendicular vector, neutrino2 perpendicular vector, transverse plane n_, unsorted neutrino1 solutions, unsorted neutrino2 solutions]

NuNuPxPyPzE(tensor b1(px, py, pz, e), tensor b2(px, py, pz, e), tensor lep1(px, py, pz, e), tensor lep2(px, py, pz, e), 
	    tensor met_x, tensor met_y, tensor massTop, tensor massW, tensor massNu, 
	    double cutoff) -> list(Tensor) -> [SkipEvent, neutrino1 cartesian momentum 3-vector, neutrino2 cartesian momentum 3-vector, neutrino1 perpendicular vector, neutrino2 perpendicular vector, transverse plane n_, unsorted neutrino1 solutions, unsorted neutrino2 solutions]

NuNuDoublePtEtaphiE(double b1_pt, double b1_eta, double b1_phi, double b1_e, double b2_pt, double b2_eta, double b2_phi, double b2_e, 
		    double lep1_pt, double lep1_eta, double lep1_phi, double lep1_e, double lep2_pt, double lep2_eta, double lep2_phi, double lep2_e,
	    	    double met, double met_phi, double massTop, double massW, double massNu, 
	    	    double cutoff) -> list(Tensor) -> [SkipEvent, neutrino1 cartesian momentum 3-vector, neutrino2 cartesian momentum 3-vector, neutrino1 perpendicular vector, neutrino2 perpendicular vector, transverse plane n_, unsorted neutrino1 solutions, unsorted neutrino2 solutions]

NuNuDoublePxPyPzE(double b1_px, double b1_py, double b1_pz, double b1_e, double b2_px, double b2_py, double b2_pz, double b2_e, 
		  double lep1_px, double lep1_py, double lep1_pz, double lep1_e, double lep2_px, double lep2_py, double lep2_pz, double lep2_e,
	    	  double met_px, double met_py, double massTop, double massW, double massNu, 
	    	  double cutoff) -> list(Tensor) -> [SkipEvent, neutrino1 cartesian momentum 3-vector, neutrino2 cartesian momentum 3-vector, neutrino1 perpendicular vector, neutrino2 perpendicular vector, transverse plane n_, unsorted neutrino1 solutions, unsorted neutrino2 solutions]

NuNuListPtEtaPhiE([[b1_pt, b1_eta, b1_phi, b1_e]], [[b2_pt, b2_eta, b2_phi, b2_e]], 
		  [[lep1_pt, lep1_eta, lep1_phi, lep1_e]], [[lep2_pt, lep2_eta, lep2_phi, lep2_e]], 
	    	  [[met_px, met_py]], [[massTop, massW, massNu]], 
	    	  double cutoff) -> list(Tensor) -> [SkipEvent, neutrino1 cartesian momentum 3-vector, neutrino2 cartesian momentum 3-vector, neutrino1 perpendicular vector, neutrino2 perpendicular vector, transverse plane n_, unsorted neutrino1 solutions, unsorted neutrino2 solutions]

NuNuListPxPyPzE([[b1_px, b1_py, b1_pz, b1_e]], [[b2_px, b2_py, b2_pz, b2_e]], 
		[[lep1_px, lep1_py, lep1_pz, lep1_e]], [[lep2_px, lep2_py, lep2_pz, lep2_e]], 
	    	[[met_px, met_py]], [[massTop, massW, massNu]], 
		double cutoff) -> list(Tensor) -> [SkipEvent, neutrino1 cartesian momentum 3-vector, neutrino2 cartesian momentum 3-vector, neutrino1 perpendicular vector, neutrino2 perpendicular vector, transverse plane n_, unsorted neutrino1 solutions, unsorted neutrino2 solutions]
```
