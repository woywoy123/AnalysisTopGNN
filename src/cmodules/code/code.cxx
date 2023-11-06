#include "../code/code.h"

namespace Code
{
    CyCode::CyCode(){}
    CyCode::~CyCode()
    {
        std::map<std::string, CyCode*>::iterator it; 
        it = this -> dependency.begin(); 
        for (; it != this -> dependency.end(); ++it){
            delete it -> second; 
        } 
    }

    void CyCode::Hash()
    {
        std::hash<std::string> hasher; 
        std::stringstream ss; 

        std::string obj_c = this -> container.object_code; 
        ss << "0x" << std::hex << hasher(obj_c); 
        std::string out = ss.str(); 
        int diff = out.size() - 18; 
        if (diff) { out += std::string(std::abs(diff), '0'); }
        this -> hash = out; 
    }

    bool CyCode::operator==(CyCode& inpt)
    {
        inpt.Hash(); 
        this -> Hash(); 
        return this -> hash == inpt.hash;
    }

    code_t CyCode::ExportCode(){
        this -> Hash();
        this -> container.hash = this -> hash;
        code_t code = this -> container; 
        std::map<std::string, CyCode*>::iterator it; 
        it = this -> dependency.begin(); 
        for (; it != this -> dependency.end(); ++it){
            code.dependency_hashes.push_back( it -> first ); 
        }
        return code;  
    }

    void CyCode::ImportCode(code_t code){
        this -> container = code;
    }

    void CyCode::ImportCode(code_t code, std::map<std::string, code_t> code_hashes)
    {
        this -> container = code;  
        code_t* co = &(this -> container); 
        std::map<std::string, code_t> get = {}; 
        std::vector<std::string> update = {}; 
        for (unsigned int x(0); x < co -> dependency_hashes.size(); ++x){
            std::string hash = co -> dependency_hashes[x]; 
            if (code_hashes.count(hash)){get[hash] = code_hashes[hash];}
            else {update.push_back(hash);} 
        }
        co -> dependency_hashes = update; 
        this -> AddDependency(get); 
    }

    void CyCode::AddDependency(std::map<std::string, CyCode*> inpt)
    {
        std::map<std::string, CyCode*>::iterator it; 
        it = inpt.begin(); 
        for (; it != inpt.end(); ++it){
            if (this -> dependency.count(it -> first)){continue;}
            CyCode* co = it -> second; 
            this -> dependency[it -> first] = new CyCode(); 
            this -> dependency[it -> first] -> ImportCode(co -> ExportCode()); 
        }
    }

    void CyCode::AddDependency(std::map<std::string, code_t> inpt)
    {
        std::map<std::string, code_t>::iterator it; 
        it = inpt.begin(); 
        for (; it != inpt.end(); ++it){
            if (this -> dependency.count(it -> first)){continue;}
            this -> dependency[it -> first] = new CyCode(); 
            this -> dependency[it -> first] -> ImportCode(it -> second, inpt); 
        }
    }
}
