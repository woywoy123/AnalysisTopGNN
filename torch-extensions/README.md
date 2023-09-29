# **PyTorchCustom (PyC)**

## **Introduction:**
This part of the framework aims to add extension modules which aim to boost speed and performance for common physics related functions. The package is completely detached from AnalysisG and can be included in other machine learning projects/frameworks. 

This package exploits PyTorch's C++/CUDA API and can therefore be freely included in both a Python and C++ context. In the case of C++, the package uses CMake to build the project and therefore be included in models which are written in C++. Furthermore, the package requires no ROOT and exclusively relies on PyTorch. 

## **Packages:**
- **Transform**: This package is dedicated to changing coordinates from ATLAS's coordinate system to cartesian. 

## Beta testing note: 
Since this is in current development, please note that when installing the package, the import name will actually be **pyext** and not **PyC**. This will change once the package has been completely migrated.

## Installation:
```bash 
pip install .
```

## Python Interface:
### Transform (PyC.Transform):
```python 
def Px(ten1, ten2 = None) -> tensor (n x 1), double, list(double): 
```

This function expects either a single tensor/float of a particle's 4-vector, or two separate tensors, where `ten1` and `ten2` are the particle's `pt` and `phi` coordinates.

```python
def Py(ten1, ten2 = None):
def Pz(ten1, ten2 = None):
def PxPyPz(ten1, ten2 = None, ten3 = None):
def PxPyPzE(ten1, ten2 = None, ten3 = None, ten4 = None):
def Pt(ten1, ten2 = None):
def Eta(ten1, ten2 = None, ten3 = None):
def Phi(ten1, ten2 = None):
def PtEtaPhi(ten1, ten2 = None, ten3 = None):
def PtEtaPhiE(ten1, ten2 = None, ten3 = None, ten4 = None):
```

This function expects either a single tensor/float of a particle's 4-vector, or two separate tensors, where `ten1` and `ten2` are the particle's `pt` and `phi` coordinates.


## C++ Interface:
### Namespaces:
- Transform:
    - `Transform::CUDA`
    - `Transform::Tensors`
    - `Transform::Floats`

 - Physics:
    - `Physics::CUDA`
    - `Physics::Tensors`
    - `Physics::CUDA::Cartesian`
    - `Physics::CUDA::Polar`

- Operators:
    - `Operators::CUDA`
    - `Operators::Tensors`

### Transform:
```cpp
// To Cartesian Coordinates using tensors
torch::Tensor Px(torch::Tensor pt, torch::Tensor phi);
torch::Tensor Px(torch::Tensor pmu); 

torch::Tensor Py(torch::Tensor pt, torch::Tensor phi); 
torch::Tensor Py(torch::Tensor pmu); 

torch::Tensor Pz(torch::Tensor pt, torch::Tensor eta); 
torch::Tensor Pz(torch::Tensor pmu); 

torch::Tensor PxPyPz(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi); 
torch::Tensor PxPyPz(torch::Tensor pmu); 

torch::Tensor PxPyPzE(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e); 
torch::Tensor PxPyPzE(torch::Tensor Pmu); 

// To Cartesian Coordinates using doubles
double Px(double pt, double phi); 
std::vector<double> Px(std::vector<std::vector<double>> pmu); 

double Py(double pt, double phi); 
std::vector<double> Py(std::vector<std::vector<double>> pmu); 

double Pz(double pt, double eta); 
std::vector<double> Pz(std::vector<std::vector<double>> pmu); 

std::vector<double> PxPyPz(double pt, double eta, double phi); 
std::vector<std::vector<double>> PxPyPz(std::vector<std::vector<double>> pmu); 

std::vector<double> PxPyPzE(double pt, double eta, double phi, double e); 
std::vector<std::vector<double>> PxPyPzE(std::vector<std::vector<double>> pmu); 

// To Polar Coordinates using tensors
torch::Tensor Pt(torch::Tensor px, torch::Tensor py); 
torch::Tensor Pt(torch::Tensor pmc); 

torch::Tensor Phi(torch::Tensor px, torch::Tensor py);
torch::Tensor Phi(torch::Tensor pmc);

torch::Tensor Eta(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
torch::Tensor Eta(torch::Tensor pmc); 

torch::Tensor PtEta(torch::Tensor pt, torch::Tensor pz); 
torch::Tensor PtEta(torch::Tensor pmc); 

torch::Tensor PtEtaPhi(torch::Tensor px, torch::Tensor py, torch::Tensor pz);
torch::Tensor PtEtaPhi(torch::Tensor pmc);

torch::Tensor PtEtaPhiE(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e);
torch::Tensor PtEtaPhiE(torch::Tensor pmc);

// To Polar Coordinates using doubles
double Pt(double px, double py); 
std::vector<double> Pt(std::vector<std::vector<double>> pmc); 

double Phi(double px, double py); 
std::vector<double> Phi(std::vector<std::vector<double>> pmc); 

double PtEta(double pt, double pz); 
std::vector<double> PtEta(std::vector<std::vector<double>> pmc); 

double Eta(double px, double py, double pz); 
std::vector<double> Eta(std::vector<std::vector<double>> pmc); 

std::vector<double> PtEtaPhi(double px, double py, double pz);
std::vector<std::vector<double>> PtEtaPhi(std::vector<std::vector<double>> pmc); 

std::vector<double> PtEtaPhiE(double px, double py, double pz, double e);
std::vector<std::vector<double>> PtEtaPhiE(std::vector<std::vector<double>> pmc); 
```
### Physics:
```cpp
// using the namespace Physics::<CUDA/Tensors>
// Momentum**2
torch::Tensor P2(torch::Tensor pmc); 
torch::Tensor P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 

// Momentum
torch::Tensor P(torch::Tensor pmc); 
torch::Tensor P(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 

// 4-vector Properties
torch::Tensor Beta2(torch::Tensor pmc); 
torch::Tensor Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
torch::Tensor Beta(torch::Tensor pmc); 
torch::Tensor Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 

// Particle Properties
// Mass**2
torch::Tensor M2(torch::Tensor pmc); 
torch::Tensor M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 

// Mass
torch::Tensor M(torch::Tensor pmc); 
torch::Tensor M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 

// Transverse Mass ** 2
torch::Tensor Mt2(torch::Tensor pmc); 
torch::Tensor Mt2(torch::Tensor pz, torch::Tensor e); 

// Transverse Mass
torch::Tensor Mt(torch::Tensor pmc); 
torch::Tensor Mt(torch::Tensor pz, torch::Tensor e); 

// Angle between between the Pz component and the momentum magnitude
// theta = cos^-1(pz/p)
torch::Tensor Theta(torch::Tensor pmc); 
torch::Tensor Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 

// Radial distance between two particle vectors
torch::Tensor DeltaR(torch::Tensor pmu1, torch::Tensor pmu2);
torch::Tensor DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2); 

// using the namespace Physics::<CUDA/Tensors>::Cartesian
torch::Tensor P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
torch::Tensor P2(torch::Tensor pmc); 
torch::Tensor P(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
torch::Tensor P(torch::Tensor pmc); 
torch::Tensor Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
torch::Tensor Beta2(torch::Tensor pmc); 
torch::Tensor Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
torch::Tensor Beta(torch::Tensor pmc); 
torch::Tensor M2(torch::Tensor pmc); 
torch::Tensor M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
torch::Tensor M(torch::Tensor pmc); 
torch::Tensor M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e); 
torch::Tensor Mt2(torch::Tensor pmc); 
torch::Tensor Mt2(torch::Tensor pz, torch::Tensor e); 
torch::Tensor Mt(torch::Tensor pmc); 
torch::Tensor Mt(torch::Tensor pz, torch::Tensor e); 
torch::Tensor Theta(torch::Tensor pmc); 
torch::Tensor Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz); 
torch::Tensor DeltaR(torch::Tensor pmc1, torch::Tensor pmc2); 
torch::Tensor DeltaR(torch::Tensor px1, torch::Tensor px2, torch::Tensor py1, torch::Tensor py2, torch::Tensor pz1, torch::Tensor pz2); 

// using the namespace Physics::<CUDA/Tensors>::Polar
torch::Tensor P2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
torch::Tensor P2(torch::Tensor Pmu)
torch::Tensor P(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
torch::Tensor P(torch::Tensor Pmu)
torch::Tensor Beta2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
torch::Tensor Beta2(torch::Tensor pmu)
torch::Tensor Beta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
torch::Tensor Beta(torch::Tensor pmu)
torch::Tensor M2(torch::Tensor pmu)
torch::Tensor M2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
torch::Tensor M(torch::Tensor pmu)
torch::Tensor M(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
torch::Tensor Mt2(torch::Tensor pmu)
torch::Tensor Mt2(torch::Tensor pt, torch::Tensor eta, torch::Tensor e)
torch::Tensor Mt(torch::Tensor pmu)
torch::Tensor Mt(torch::Tensor pt, torch::Tensor eta, torch::Tensor e)
torch::Tensor Theta(torch::Tensor pmu)
torch::Tensor Theta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
torch::Tensor DeltaR(torch::Tensor pmu1, torch::Tensor pmu2)
torch::Tensor DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2)
```

### Operators:

```cpp
// Customly designed CUDA operators (normal C++ wrappers are just torch methods)
torch::Tensor Dot(torch::Tensor v1, torch::Tensor v2); 
torch::Tensor Mul(torch::Tensor v1, torch::Tensor v2); 

// Angle Between Tensors
torch::Tensor CosTheta(torch::Tensor v1, torch::Tensor v2); 
torch::Tensor SinTheta(torch::Tensor v1, torch::Tensor v2); 

// Rotation Matrix Generators
torch::Tensor Rx(torch::Tensor angle); 
torch::Tensor Ry(torch::Tensor angle); 
torch::Tensor Rz(torch::Tensor angle); 

// Matrix related operators
torch::Tensor CoFactors(torch::Tensor matrix); 
torch::Tensor Determinant(torch::Tensor matrix); 
torch::Tensor Inverse(torch::Tensor matrix); 
```
