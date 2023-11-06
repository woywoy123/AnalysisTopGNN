#include "../abstractions/cytypes.h"
#include "../code/code.h"
#include <sstream>
#include <fstream>

#ifndef ABSTRACTION_H
#define ABSTRACTION_H

namespace Tools
{
    std::string base64_encode(unsigned char const*, unsigned int len); 
    std::string base64_decode(std::string const& s); 
    inline std::string encode64(std::string* inpt){
       unsigned int length = inpt -> size(); 
       const char* ch = inpt -> c_str(); 
       return base64_encode((const unsigned char*) ch, length); 
    };

    inline std::string decode64(std::string* inpt){
       return base64_decode(*inpt); 
    };

    bool is_file(const std::string* file); 

    std::string Hashing(std::string input); 
    std::string ToString(double input);
    std::vector<std::string> split(std::string inpt, std::string search); 
    std::string join(std::vector<std::string>* inpt, int s, int e, std::string delim); 
    int count(std::string inpt, std::string search); 
    std::map<std::string, int> CheckDifference(std::vector<std::string> inpt1, std::vector<std::string> inpt2, int threads); 

    template <typename G>
    std::vector<std::vector<G>> Quantize(const std::vector<G>& v, int N)
    {
        int n = v.size(); 
        typename std::vector<std::vector<G>> out; 
        for (int ib = 0; ib < n; ib += N){
            int end = ib + N; 
            if (end > n){ end = n; }
            out.push_back(std::vector<G>(v.begin() + ib, v.begin() + end)); 
        }
        return out; 
    };
}

namespace Abstraction
{
    class CyBase
    {
        public:
            CyBase();
            ~CyBase();

            void Hash(std::string inpt); 
            
            std::string hash = "";
            int event_index = 0; 
    }; 

    class CyEvent
    {
        public: 
            CyEvent(); 
            ~CyEvent();

            void ImportMetaData(meta_t meta); 

            meta_t  meta; 
            event_t event;
            graph_t graph; 
            selection_t selection;

            Code::CyCode* code_link = nullptr; 

            bool is_event = false; 
            bool is_graph = false; 
            bool is_selection = false; 

            template <typename T, typename G> 
            void set_event_hash(T* type, G* event){
                type -> event_hash = event -> event_hash; 
            };

            template <typename T, typename G>
            void set_event_tag(T* type, G* event){
                type -> event_tagging = event -> event_tagging;
            };

            template <typename T, typename G>
            void set_event_tree(T* type, G* event){
                type -> event_tree = event -> event_tree; 
            };

            template <typename T, typename G>
            void set_event_root(T* type, G* event){
                type -> event_root = event -> event_root; 
            };

            template <typename T, typename G>
            void set_event_index(T* type, G* event){
                type -> event_index = event -> event_index;
            }; 

            template <typename T, typename G>
            void set_event_weight(T* type, G* event){
                type -> weight = event -> weight;
            }; 

            template <typename T>
            void set_event_name(T* type, std::string name){
                type -> event_name = name; 
            };


            template <typename T, typename G>
            bool is_same(T* event1, G* event2)
            {
                if (event1 -> event_hash != event2 -> event_hash){ 
                    return false; 
                }
                if (event1 -> event_name != event2 -> event_name){ 
                    return false; 
                }
                if (event1 -> event_tree != event2 -> event_tree){
                    return false; 
                }
                if (event1 -> event_tagging != event2 -> event_tagging){
                    return false; 
                }
                if (event1 -> event != event2 -> event){
                    return false;
                }
                if (event1 -> graph != event2 -> graph){
                    return false;
                }
                if (event1 -> selection != event2 -> selection){
                    return false;
                }
                return true; 
            }; 

            template <typename T>
            std::string Hash(T* event){
                if (event -> event_hash.size()){ 
                    return event -> event_hash; 
                }
                std::string hash = event -> event_root + "/"; 
                hash += Tools::ToString(event -> event_index) + "/"; 
                event -> event_hash = Tools::Hashing(hash);
                return event -> event_hash;
            };
    };
}
#endif
