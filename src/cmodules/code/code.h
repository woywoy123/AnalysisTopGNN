#include "../abstractions/cytypes.h"
#include <sstream> 

#ifndef CODE_H
#define CODE_H

namespace Code
{
    class CyCode
    {
        public:
            CyCode();
            ~CyCode();

            void Hash(); 
            void ImportCode(code_t code);
            void ImportCode(code_t code, std::map<std::string, code_t> code_hashes);

            code_t ExportCode(); 

            void AddDependency(std::map<std::string, code_t>); 
            void AddDependency(std::map<std::string, CyCode*>); 
           
            code_t container;
            bool operator == (CyCode& code);
            std::string hash = "";
            
            std::map<std::string, CyCode*> dependency = {};  
    };
}

#endif
