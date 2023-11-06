#include "../particle/particle.h"
#include <cmath>

namespace CyTemplate
{
    CyParticleTemplate::CyParticleTemplate(){}

    CyParticleTemplate::CyParticleTemplate(particle_t p)
    {
        this -> state = p; 
    }

    CyParticleTemplate::CyParticleTemplate(double px, double py, double pz, double e) 
    {
        particle_t* p = &(this -> state); 
        p -> px = px; 
        p -> py = py; 
        p -> pz = pz; 
        p -> e = e; 
        p -> polar = true; 
    }

    CyParticleTemplate::CyParticleTemplate(double px, double py, double pz)
    {
        particle_t* p = &(this -> state); 
        p -> px = px; 
        p -> py = py; 
        p -> pz = pz; 
        this -> e(); 
        p -> polar = true; 
    }

    CyParticleTemplate::~CyParticleTemplate(){}

    particle_t CyParticleTemplate::Export()
    {
        this -> state.hash = ""; 
        return this -> state; 
    }
    
    void CyParticleTemplate::Import(particle_t part)
    {
        this -> state = part;
        this -> state.hash = ""; 
        this -> hash(); 
    }

    double CyParticleTemplate::e()
    {
        particle_t* p = &(this -> state); 
        if (p -> e >= 0){return p -> e;}
        p -> e += std::pow(this -> px(), 2); 
        p -> e += std::pow(this -> py(), 2); 
        p -> e += std::pow(this -> pz(), 2); 
        if (p -> mass >= 0){p -> e += p -> mass;}
        p -> e  = std::pow(p -> e, 0.5); 
        return p -> e; 
    }

    void CyParticleTemplate::e(double val)
    { 
        this -> state.e = val; 
    }

    void CyParticleTemplate::mass(double val)
    { 
        this -> state.mass = val; 
    }

    double CyParticleTemplate::mass()
    {
        particle_t* p = &(this -> state); 
        if (p -> mass > -1){ return p -> mass; }
        p -> mass = 0; 
        p -> mass -= std::pow(this -> px(), 2); 
        p -> mass -= std::pow(this -> py(), 2); 
        p -> mass -= std::pow(this -> pz(), 2); 
        p -> mass += std::pow(this -> e() , 2); 
        p -> mass = (p -> mass >= 0) ? std::pow(p -> mass, 0.5) : -1; 
        return p -> mass; 
    }

    void CyParticleTemplate::symbol(std::string val)
    {
        this -> state.symbol = val;
    }

    std::string CyParticleTemplate::symbol()
    {
        particle_t* p = &(this -> state); 
        if ((p -> symbol).size() != 0){return p -> symbol;}
        
        std::map<int, std::string> sym = {
                 {1, "d"}, {2, "u"}, {3, "s"}, 
                 {4, "c"}, {5, "b"}, {6, "t"},
                 {11, "e"}, {12, "$\\nu_{e}$"}, 
                 {13, "$\\mu$"}, {14, "$\\nu_{\\mu}$"}, 
                 {15, "$\\tau$"}, {16, "$\\nu_{\\tau}$"},
                 {21, "g"}, {22, "$\\gamma$"}
        }; 

        std::stringstream ss; 
        ss << sym[std::abs(p -> pdgid)];
        return ss.str(); 
    }


    void CyParticleTemplate::pdgid(int val)
    {
        this -> state.pdgid = val; 
    }

    int CyParticleTemplate::pdgid()
    {
        particle_t* p = &(this -> state); 
        if (p -> pdgid != 0){ return p -> pdgid; }
        if (p -> symbol.size() == 0){ return p -> pdgid; }
        
        std::map<int, std::string> sym = {
                 {1, "d"}, {2, "u"}, {3, "s"}, 
                 {4, "c"}, {5, "b"}, {6, "t"},
                 {11, "e"}, {12, "$\\nu_{e}$"}, 
                 {13, "$\\mu$"}, {14, "$\\nu_{\\mu}$"}, 
                 {15, "$\\tau$"}, {16, "$\\nu_{\\tau}$"},
                 {21, "g"}, {22, "$\\gamma$"}
        }; 
        std::map<int, std::string>::iterator it; 
        for (it = sym.begin(); it != sym.end(); ++it)
        {
            if (it -> second != p -> symbol){continue;}
            p -> pdgid = it -> first; 
            break; 
        }
        return p -> pdgid;  
    }

    void CyParticleTemplate::charge(double val)
    {
        this -> state.charge = val;
    }

    double CyParticleTemplate::charge()
    {
        return this -> state.charge;
    }

    bool CyParticleTemplate::is(std::vector<int> p)
    {
        for (int i : p){ 
            if (std::abs(i) != std::abs(this -> state.pdgid)){} 
            else {return true;}
        }
        return false; 
    }
    bool CyParticleTemplate::is_b()  { return this -> is({5}); }
    bool CyParticleTemplate::is_nu() { return this -> is(this -> state.nudef); }
    bool CyParticleTemplate::is_lep(){ return this -> is(this -> state.lepdef); }
    bool CyParticleTemplate::is_add()
    { 
        bool out = (this -> is_lep() || this -> is_nu() || this -> is_b()); 
        return !out; 
    }

    bool CyParticleTemplate::lep_decay(std::vector<particle_t> inpt)
    {
        bool nu  = false; 
        bool lep = false; 
        for (unsigned int x(0); x < inpt.size(); ++x)
        {
            CyParticleTemplate* p = new CyParticleTemplate(inpt[x]); 
            if (!nu) { nu  = p -> is_nu();}
            if (!lep){ lep = p -> is_lep();}
            delete p; 
        }
        if (lep && nu){ return true; }
        return false;
    }

    // Cartesian Conversion functions
    void CyParticleTemplate::ToCartesian() 
    {
        particle_t* p = &(this -> state); 
        if (!p -> cartesian){ return; }
        p -> px = (p -> pt)*std::cos(p -> phi); 
        p -> py = (p -> pt)*std::sin(p -> phi); 
        p -> pz = (p -> pt)*std::sinh(p -> eta); 
        p -> cartesian = false; 
    }
    
    double CyParticleTemplate::px()
    {
        this -> ToCartesian(); 
        return this -> state.px;
    }
    double CyParticleTemplate::py()
    {
        this -> ToCartesian(); 
        return this -> state.py;
    }
    double CyParticleTemplate::pz()
    {
        this -> ToCartesian(); 
        return this -> state.pz;
    }

    // Polar Conversion functions
    void CyParticleTemplate::ToPolar()
    {
        particle_t* p = &(this -> state); 
        if (!p -> polar){ return; }

        // Transverse Momenta
        p -> pt  = std::pow(p -> px, 2); 
        p -> pt += std::pow(p -> py, 2);
        p -> pt  = std::pow(p -> pt, 0.5); 

        // Rapidity 
        p -> eta = std::asinh(p -> pz / p -> pt); 
        p -> phi = std::atan2(p -> py, p -> px);  
        p -> polar = false; 
    }

    double CyParticleTemplate::pt()
    {
        this -> ToPolar(); 
        return this -> state.pt;
    }
    double CyParticleTemplate::eta()
    {
        this -> ToPolar(); 
        return this -> state.eta;
    }
    double CyParticleTemplate::phi()
    {
        this -> ToPolar(); 
        return this -> state.phi;
    }

    void CyParticleTemplate::px(double val)
    { 
        this -> state.px = val; 
        this -> state.polar = true; 
    }

    void CyParticleTemplate::py(double val)
    { 
        this -> state.py = val; 
        this -> state.polar = true; 
    }
    
    void CyParticleTemplate::pz(double val)
    { 
        this -> state.pz = val; 
        this -> state.polar = true; 
    }
    
    // Polar Conversion functions
    void CyParticleTemplate::pt(double val)
    { 
        this -> state.pt = val; 
        this -> state.cartesian = true;
    }
    
    void CyParticleTemplate::eta(double val)
    { 
        this -> state.eta = val; 
        this -> state.cartesian = true; 
    }
    
    void CyParticleTemplate::phi(double val)
    { 
        this -> state.phi = val; 
        this -> state.cartesian = true; 
    }

    std::string CyParticleTemplate::hash()
    {
        particle_t* p = &(this -> state); 
        if ((p -> hash).size()){return p -> hash;}

        this -> ToCartesian(); 
        p -> hash  = Tools::ToString(this -> px()); 
        p -> hash += Tools::ToString(this -> py()); 
        p -> hash += Tools::ToString(this -> pz());
        p -> hash += Tools::ToString(this -> e()); 
        p -> hash  = Tools::Hashing(p -> hash); 
        return p -> hash; 
    }

    void CyParticleTemplate::addleaf(std::string key, std::string leaf)
    {
        this -> leaves[key] = leaf; 
    }

    CyParticleTemplate* CyParticleTemplate::operator + (CyParticleTemplate* p)
    {
        p -> ToCartesian(); 
        CyParticleTemplate* p2 = new CyParticleTemplate(
                p -> px() + this -> px(), 
                p -> py() + this -> py(), 
                p -> pz() + this -> pz(), 
                p -> e()  + this -> e()
        ); 

        p2 -> ToCartesian(); 
        p2 -> ToPolar(); 
        p2 -> state.type = this -> state.type; 
        return p2; 
    }

    void CyParticleTemplate::operator += (CyParticleTemplate* p)
    {
        p -> ToCartesian(); 
        this -> ToCartesian();

        this -> state.px += p -> px(); 
        this -> state.py += p -> py(); 
        this -> state.pz += p -> pz(); 
        this -> state.e  += p -> e(); 
        this -> state.polar = true;
    }

    void CyParticleTemplate::iadd(CyParticleTemplate* p)
    {
        *this += p; 
    }

    bool CyParticleTemplate::operator == (CyParticleTemplate& p)
    {
        return this -> hash() == p.hash(); 
    }

    double CyParticleTemplate::DeltaR(CyParticleTemplate* p)
    {
        double sum = fabs( this -> phi() - p -> phi());
        sum = fmod(sum, 2*M_PI); 
        sum = M_PI - fabs(sum - M_PI); 
        sum = std::pow(sum, 2);
        sum += std::pow(this -> eta() - p -> eta(), 2); 
        sum = std::pow(sum, 0.5); 
        return sum; 
    }
}
