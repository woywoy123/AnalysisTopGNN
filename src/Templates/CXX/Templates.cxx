#include "../Headers/Templates.h"

CyTemplate::CyEventTemplate::CyEventTemplate(){}
CyTemplate::CyEventTemplate::~CyEventTemplate(){}

std::string CyTemplate::CyEventTemplate::Hash()
{ 
    return this -> _hash; 
}

void CyTemplate::CyEventTemplate::Hash(std::string inpt)
{
    if (this -> _hash != ""){return;}
    if (inpt.size() == 18){ this -> _hash = inpt; return; }
    inpt = inpt + "/" + Tools::ToString(this -> index) + "/" + (this -> tree); 
    this -> _hash = Tools::Hashing(inpt); 
}

CyTemplate::CyParticleTemplate::CyParticleTemplate(){}

CyTemplate::CyParticleTemplate::CyParticleTemplate(double px, double py, double pz, double e)
{
    this -> _px = px; 
    this -> _py = py; 
    this -> _pz = pz; 
    this -> _e = e; 
    this -> _initC = true; 
    this -> Hash();
    this -> pt(); 
    this -> eta(); 
    this -> phi();  
}

CyTemplate::CyParticleTemplate::~CyParticleTemplate(){}

std::string CyTemplate::CyParticleTemplate::Hash()
{
    if (this -> _initC && !(this -> _px + this -> _py + this -> _pz + this -> _e))
    {
        this -> _hash = Tools::ToString(this -> _px); 
        this -> _hash += Tools::ToString(this -> _py); 
        this -> _hash += Tools::ToString(this -> _pz); 
        this -> _hash += Tools::ToString(this -> _e); 
        this -> _hash = Tools::Hashing(this -> _hash); 
    }
    if (this -> _hash == "")
    {
        this -> px(); 
        this -> py(); 
        this -> pz(); 
        this -> _hash = Tools::ToString(this -> _px); 
        this -> _hash += Tools::ToString(this -> _py); 
        this -> _hash += Tools::ToString(this -> _pz); 
        this -> _hash += Tools::ToString(this -> _e); 
        this -> _hash = Tools::Hashing(this -> _hash); 
    }
    return this -> _hash; 
}

// Cartesian Conversion functions
double CyTemplate::CyParticleTemplate::px()
{
    if (this -> _initP)
    {
        this -> _px = (this -> _pt)*std::cos(this -> _phi);
    }
    return this -> _px; 
}

double CyTemplate::CyParticleTemplate::py()
{
    if (this -> _initP)
    {
        this -> _py = (this -> _pt)*std::sin(this -> _phi);
    }
    return this -> _py; 
}

double CyTemplate::CyParticleTemplate::pz()
{
    if (this -> _initP)
    {
        this -> _pz = (this -> _pt) * std::sinh(this -> _eta); 
    }
    return this -> _pz; 
}

// Polar Conversion functions
double CyTemplate::CyParticleTemplate::pt()
{
    if (this -> _initC)
    {
        double sum = 0; 
        sum += std::pow(this -> _px, 2); 
        sum += std::pow(this -> _py, 2);
        sum = std::pow(sum, 0.5); 
        this -> _pt = sum; 
    }
    return this -> _pt; 
}

double CyTemplate::CyParticleTemplate::eta()
{
    if (this -> _initC && this -> _pt)
    {
        this -> _eta = std::asinh(this -> _pz / this -> _pt); 
    }
    return this -> _eta; 
}

double CyTemplate::CyParticleTemplate::phi()
{
    if (this -> _initC)
    {
        this -> _phi = std::atan2(this -> _py, this -> _px); 
    }
    return this -> _phi; 
}

double CyTemplate::CyParticleTemplate::e(){return this -> _e;}

// Cartesian Conversion functions
void CyTemplate::CyParticleTemplate::px(double val)
{ 
    this -> _px = val; 
    this -> _initC = true; 
}

void CyTemplate::CyParticleTemplate::py(double val)
{ 
    this -> _py = val; 
    this -> _initC = true; 
}

void CyTemplate::CyParticleTemplate::pz(double val)
{ 
    this -> _pz = val; 
    this -> _initC = true; 
}

// Polar Conversion functions
void CyTemplate::CyParticleTemplate::pt(double val)
{ 
    this -> _pt = val; 
    this -> _initP = true; 
}

void CyTemplate::CyParticleTemplate::eta(double val)
{ 
    this -> _eta = val; 
    this -> _initP = true; 
}

void CyTemplate::CyParticleTemplate::phi(double val)
{ 
    this -> _phi = val; 
    this -> _initP = true; 
}

void CyTemplate::CyParticleTemplate::e(double val){this -> _e = val;}

// Physics Functions 
double CyTemplate::CyParticleTemplate::Mass()
{
    double sum = 0; 
    sum += std::pow(this -> _e, 2); 
    sum -= std::pow(this -> _px, 2);
    sum -= std::pow(this -> _py, 2);
    sum -= std::pow(this -> _pz, 2);
    this -> _mass = (sum >= 0) ? std::pow(sum, 0.5): 0; 
    return this -> _mass; 
}

void CyTemplate::CyParticleTemplate::Mass(double val){this -> _mass = val;}
double CyTemplate::CyParticleTemplate::DeltaR(const CyTemplate::CyParticleTemplate& p)
{
    double sum = M_PI - fabs(fmod(fabs(this -> _phi - p._phi), 2*M_PI) - M_PI); 
    return std::pow(std::pow(sum, 2) + std::pow(this -> _eta - p._eta, 2), 0.5); 
}

// Particle Functions 
signed int CyTemplate::CyParticleTemplate::pdgid(){return this -> _pdgid;}
void CyTemplate::CyParticleTemplate::pdgid(signed int id){this -> _pdgid = id;}

double CyTemplate::CyParticleTemplate::charge(){return this -> _charge;}
void CyTemplate::CyParticleTemplate::charge(double id){this -> _charge = id;}

std::string CyTemplate::CyParticleTemplate::symbol()
{
    std::map<int, std::string> sym = {
                 {1, "d"}, {2, "u"}, {3, "s"}, {4, "c"}, {5, "b"}, {6, "t"},
                 {11, "e"}, {12, "$\\nu_{e}$"}, {13, "$\\mu$"}, {14, "$\\nu_{\\mu}$"}, 
                 {15, "$\\tau$"}, {16, "$\\nu_{\\tau}$"},
                 {21, "g"}, {22, "$\\gamma$"}
    }; 

    std::stringstream ss; 
    ss << sym[std::abs(this -> _pdgid)];
    return ss.str(); 
}


bool CyTemplate::CyParticleTemplate::is(std::vector<signed int> p)
{
    for (signed int i : p){ if (std::abs(i) == std::abs(this -> _pdgid)) { return true; }}
    return false; 
}
void CyTemplate::CyParticleTemplate::symbol(std::string inpt){this -> _symbol = inpt;}
bool CyTemplate::CyParticleTemplate::is_b(){ return this -> is({5}); }
bool CyTemplate::CyParticleTemplate::is_nu(){ return this -> is(this -> _nudef); }
bool CyTemplate::CyParticleTemplate::is_lep(){ return this -> is(this -> _lepdef); }
