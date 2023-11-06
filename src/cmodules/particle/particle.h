#include "../abstractions/abstractions.h"
#include "../abstractions/cytypes.h"

#ifndef PARTICLE_H
#define PARTICLE_H


namespace CyTemplate
{
    class CyParticleTemplate
    {
        public:
            CyParticleTemplate(); 
            CyParticleTemplate(particle_t p); 
            CyParticleTemplate(double px, double py, double pz, double e); 
            CyParticleTemplate(double px, double py, double pz); 
            ~CyParticleTemplate(); 

            double DeltaR(CyParticleTemplate* p);

            particle_t Export(); 
            void Import(particle_t part); 


            double e(); 
            void e(double val); 
            
            void mass(double val); 
            double mass(); 

            void pdgid(int val); 
            int pdgid(); 

            void symbol(std::string val); 
            std::string symbol(); 

            void charge(double val); 
            double charge(); 

            bool is_lep(); 
            bool is_nu(); 
            bool is_b(); 
            bool is_add(); 
            bool lep_decay(std::vector<particle_t>);

            // ===== Cartesian ===== //
            // getter
            double px(); 
            double py(); 
            double pz(); 

            // setter
            void px(double val); 
            void py(double val);
            void pz(double val); 

            // ===== Polar ==== // 
            // getter
            double pt(); 
            double eta(); 
            double phi(); 

            // setter
            void pt(double val); 
            void eta(double val);
            void phi(double val); 

            void ToCartesian(); 
            void ToPolar(); 

            std::string hash(); 
            void addleaf(std::string key, std::string leaf); 

            bool operator == (CyParticleTemplate& p); 
            CyParticleTemplate* operator+(CyParticleTemplate* p);
            void operator += (CyParticleTemplate* p); 
            void iadd(CyParticleTemplate* p); 
            
            std::map<std::string, std::string> leaves = {}; 
       
            particle_t state; 
            bool is(std::vector<int> p); 
    }; 
}
#endif
