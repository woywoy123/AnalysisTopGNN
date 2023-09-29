#include "cartesian.h"

torch::Tensor Physics::Tensors::Cartesian::P2(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{ 
    return Physics::Tensors::P2(px, py, pz); 
}

torch::Tensor Physics::Tensors::Cartesian::P2(torch::Tensor pmc)
{
    return Physics::Tensors::P2(pmc); 
}

torch::Tensor Physics::Tensors::Cartesian::P(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{ 
    return Physics::Tensors::P(px, py, pz); 
}

torch::Tensor Physics::Tensors::Cartesian::P(torch::Tensor pmc)
{
    return Physics::Tensors::P(pmc); 
}

torch::Tensor Physics::Tensors::Cartesian::Beta2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{ 
    return Physics::Tensors::Beta2(px, py, pz, e); 
}

torch::Tensor Physics::Tensors::Cartesian::Beta2(torch::Tensor pmc)
{
    return Physics::Tensors::Beta2(pmc); 
}

torch::Tensor Physics::Tensors::Cartesian::Beta(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{ 
    return Physics::Tensors::Beta(px, py, pz, e); 
}

torch::Tensor Physics::Tensors::Cartesian::Beta(torch::Tensor pmc)
{
    return Physics::Tensors::Beta(pmc); 
}

torch::Tensor Physics::Tensors::Cartesian::M2(torch::Tensor pmc)
{ 
    return Physics::Tensors::M2(pmc); 
}

torch::Tensor Physics::Tensors::Cartesian::M2(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{ 
    return Physics::Tensors::M2(px, py, pz, e); 
}

torch::Tensor Physics::Tensors::Cartesian::M(torch::Tensor pmc)
{ 
    return Physics::Tensors::M(pmc); 
}

torch::Tensor Physics::Tensors::Cartesian::M(torch::Tensor px, torch::Tensor py, torch::Tensor pz, torch::Tensor e)
{ 
    return Physics::Tensors::M(px, py, pz, e); 
}

torch::Tensor Physics::Tensors::Cartesian::Mt2(torch::Tensor pmc)
{ 
    return Physics::Tensors::Mt2(pmc);
}

torch::Tensor Physics::Tensors::Cartesian::Mt2(torch::Tensor pz, torch::Tensor e)
{ 
    return Physics::Tensors::Mt2(pz, e); 
}

torch::Tensor Physics::Tensors::Cartesian::Mt(torch::Tensor pmc)
{ 
    return Physics::Tensors::Mt(pmc); 
}

torch::Tensor Physics::Tensors::Cartesian::Mt(torch::Tensor pz, torch::Tensor e)
{ 
    return Physics::Tensors::Mt(pz, e); 
}

torch::Tensor Physics::Tensors::Cartesian::Theta(torch::Tensor pmc)
{
    return Physics::Tensors::Theta(pmc); 
}

torch::Tensor Physics::Tensors::Cartesian::Theta(torch::Tensor px, torch::Tensor py, torch::Tensor pz)
{
    return Physics::Tensors::Theta(px, py, pz); 
}

torch::Tensor Physics::Tensors::Cartesian::DeltaR(torch::Tensor pmc1, torch::Tensor pmc2)
{
    const unsigned int len = pmc1.size(0);
    torch::Tensor pmu1 = Transform::Tensors::PtEtaPhiE(torch::cat({pmc1, pmc2}, 0)); 
    torch::Tensor pmu2 = pmu1.index({torch::indexing::Slice({len, len*2+1})}).view({-1, 4});
    pmu1 = pmu1.index({torch::indexing::Slice({0, len})}).view({-1, 4});
    return Physics::Tensors::DeltaR(pmu1, pmu2); 
}

torch::Tensor Physics::Tensors::Cartesian::DeltaR(
        torch::Tensor px1, torch::Tensor px2, 
        torch::Tensor py1, torch::Tensor py2, 
        torch::Tensor pz1, torch::Tensor pz2)
{
    const unsigned int len = px1.size(0);
    torch::Tensor pmu1 = Transform::Tensors::PtEtaPhi(
            torch::cat({px1, px2}, 0), 
            torch::cat({py1, py2}, 0), 
            torch::cat({pz1, pz2}, 0)); 
    torch::Tensor pmu2 = pmu1.index({torch::indexing::Slice({len, len*2+1})}).view({-1, 3});
    pmu1 = pmu1.index({torch::indexing::Slice({0, len})}).view({-1, 3});
    return Physics::Tensors::DeltaR(pmu1, pmu2); 
}
