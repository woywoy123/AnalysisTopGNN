#include "polar.h"

torch::Tensor Physics::Tensors::Polar::P2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
{
    torch::Tensor pmc = Transform::Tensors::PxPyPz(pt, eta, phi); 
    return Physics::Tensors::P2(pmc); 
} 

torch::Tensor Physics::Tensors::Polar::P2(torch::Tensor pmu)
{
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pmu); 
    return Physics::Tensors::P2(pmc);
}

torch::Tensor Physics::Tensors::Polar::P(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
{
     torch::Tensor pmc = Transform::Tensors::PxPyPz(pt, eta, phi); 
     return Physics::Tensors::P(pmc); 
}

torch::Tensor Physics::Tensors::Polar::P(torch::Tensor pmu)
{
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pmu); 
    return Physics::Tensors::P(pmc);
}

torch::Tensor Physics::Tensors::Polar::Beta2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
{ 
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pt, eta, phi, e); 
    return Physics::Tensors::Beta2(pmc); 
}

torch::Tensor Physics::Tensors::Polar::Beta2(torch::Tensor pmu)
{
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pmu); 
    return Physics::Tensors::Beta2(pmc); 
}

torch::Tensor Physics::Tensors::Polar::Beta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
{ 
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pt, eta, phi, e); 
    return Physics::Tensors::Beta(pmc); 
}

torch::Tensor Physics::Tensors::Polar::Beta(torch::Tensor pmu)
{
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pmu); 
    return Physics::Tensors::Beta(pmc); 
}

torch::Tensor Physics::Tensors::Polar::M2(torch::Tensor pmu)
{ 
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pmu); 
    return Physics::Tensors::M2(pmc); 
}

torch::Tensor Physics::Tensors::Polar::M2(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
{ 
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pt, eta, phi, e); 
    return Physics::Tensors::M2(pmc); 
}

torch::Tensor Physics::Tensors::Polar::M(torch::Tensor pmu)
{ 
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pmu); 
    return Physics::Tensors::M(pmc); 
}

torch::Tensor Physics::Tensors::Polar::M(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi, torch::Tensor e)
{ 
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pt, eta, phi, e); 
    return Physics::Tensors::M(pmc); 
}

torch::Tensor Physics::Tensors::Polar::Mt2(torch::Tensor pmu)
{ 
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pmu); 
    return Physics::Tensors::Mt2(pmc);
}

torch::Tensor Physics::Tensors::Polar::Mt2(torch::Tensor pt, torch::Tensor eta, torch::Tensor e)
{ 
    torch::Tensor pz = Transform::Tensors::Pz(pt, eta); 
    return Physics::Tensors::Mt2(pz, e); 
}

torch::Tensor Physics::Tensors::Polar::Mt(torch::Tensor pmu)
{ 
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pmu); 
    return Physics::Tensors::Mt(pmc); 
}

torch::Tensor Physics::Tensors::Polar::Mt(torch::Tensor pt, torch::Tensor eta, torch::Tensor e)
{ 
    torch::Tensor pz = Transform::Tensors::Pz(pt, eta); 
    return Physics::Tensors::Mt(pz, e); 
}

torch::Tensor Physics::Tensors::Polar::Theta(torch::Tensor pmu)
{
    torch::Tensor pmc = Transform::Tensors::PxPyPzE(pmu); 
    return Physics::Tensors::Theta(pmc); 
}

torch::Tensor Physics::Tensors::Polar::Theta(torch::Tensor pt, torch::Tensor eta, torch::Tensor phi)
{
    torch::Tensor pmc = Transform::Tensors::PxPyPz(torch::cat({pt.view({-1, 1}), eta.view({-1, 1}), phi.view({-1, 1})}, -1)); 
    return Physics::Tensors::Theta(pmc); 
}

torch::Tensor Physics::Tensors::Polar::DeltaR(torch::Tensor pmu1, torch::Tensor pmu2)
{
    return Physics::Tensors::DeltaR(pmu1, pmu2); 
}

torch::Tensor Physics::Tensors::Polar::DeltaR(torch::Tensor eta1, torch::Tensor eta2, torch::Tensor phi1, torch::Tensor phi2)
{
    return Physics::Tensors::DeltaR(eta1, eta2, phi1, phi2); 
}
