#include "../abstractions/cytypes.h"
#include "../abstractions/abstractions.h"

#ifndef METADATA_H
#define METADATA_H

namespace SampleTracer
{
    class CyMetaData : public Abstraction::CyBase
    {
        public:
            CyMetaData();
            ~CyMetaData();
            meta_t container; 

            void Hash();
            void addconfig(
                    std::string key, 
                    std::string val);

            void addsamples(
                    int index, 
                    int range, 
                    std::string sample);

            void processkeys(
                    std::vector<std::string> keys, 
                    unsigned int num_entries);

            void Import(meta_t meta); 
            meta_t Export();

            std::map<std::string, std::vector<std::string>> MakeGetter();

            std::map<std::string, int> GetLength();
            std::string IndexToSample(int index);
            std::string DatasetName(); 
            std::vector<std::string> DAODList();
 
            template <typename T>
            void _check_this(
                    std::vector<std::string>* req, 
                    std::vector<std::string>* mis, 
                    std::map<std::string, T>* fnd)
            {
                for (unsigned int x(0); x < req -> size(); ++x)
                {
                    std::string key = req -> at(x); 
                    if (fnd -> count(key)){ continue; }
                    mis -> push_back(key); 
                }
                req -> clear(); 
                typename std::map<std::string, T>::const_iterator it;
                it = fnd -> begin(); 
                for(; it != fnd -> end(); ++it)
                { 
                    req -> push_back(it -> first); 
                }
            };

            void FindMissingKeys();
    };
}

#endif
