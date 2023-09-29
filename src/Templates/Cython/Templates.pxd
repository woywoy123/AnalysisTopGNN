from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool

cdef extern from "../Headers/Tools.h" namespace "Tools":
    pass

cdef extern from "../Headers/Templates.h" namespace "CyTemplate" nogil:
    cdef cppclass CyParticleTemplate nogil:
        CyParticleTemplate() except + nogil
        CyParticleTemplate(double px, double py, double pz, double e) except + nogil
        CyParticleTemplate operator+(const CyParticleTemplate& p1) except + nogil
        bool operator==(const CyParticleTemplate& p1) except + nogil

        # Book keeping variables
        signed int index;

        # State indicator
        bool _editedC;
        bool _editedP;

        # Particle def 
        vector[signed int] _lepdef;
        vector[signed int] _nudef;
        string Type;

        # Getter Functions
        double px() except + nogil
        double py() except + nogil
        double pz() except + nogil
        double pt() except + nogil
        double eta() except + nogil
        double phi() except + nogil
        double e() except + nogil
        double Mass() except + nogil
        double DeltaR(const CyParticleTemplate& p) except + nogil
        signed int pdgid() except + nogil
        double charge() except + nogil
        string symbol() except + nogil
        bool is_lep() except + nogil
        bool is_nu() except + nogil
        bool is_b() except + nogil

        # Setter Functions
        void px(double val) except + nogil
        void py(double val) except + nogil
        void pz(double val) except + nogil
        void pt(double val) except + nogil
        void eta(double val) except + nogil
        void phi(double val) except + nogil
        void e(double val) except + nogil
        void Mass(double val) except + nogil
        void pdgid(signed int val) except + nogil
        void charge(double val) except + nogil
        void symbol(string val) except + nogil

        string Hash() except + nogil

    cdef cppclass CyEventTemplate nogil:
        CyEventTemplate() except + nogil

        signed int index;
        double weight;
        bool deprecated;
        string tree;
        string commit_hash;

        void Hash(string val) except + nogil
        string Hash() except + nogil

