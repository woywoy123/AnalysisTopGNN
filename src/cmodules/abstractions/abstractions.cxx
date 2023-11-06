#include "../abstractions/abstractions.h"

bool Tools::is_file(const std::string* file)
{
    std::ifstream f(file -> c_str());
    return f.good();     
}

std::string Tools::Hashing(std::string input)
{
    std::hash<std::string> hasher; 
    std::stringstream ss; 
    ss << "0x" << std::hex << hasher(input); 
    std::string out = ss.str(); 
    int diff = out.size() - 18; 
    if (!diff) { return out; }
    out += std::string(std::abs(diff), '0'); 
    return out; 
}

std::string Tools::ToString(double inpt)
{
    std::stringstream ss; 
    ss << inpt; 
    return ss.str(); 
}

std::vector<std::string> Tools::split(std::string inpt, std::string search)
{
    size_t pos = 0;
    size_t s_dim = search.length(); 
    size_t index = 0; 
    std::string token; 
    std::vector<std::string> out = {}; 
    while ((pos = inpt.find(search)) != std::string::npos){
        out.push_back(inpt.substr(0, pos));
        inpt.erase(0, pos + s_dim); 
        ++index; 
    }
    out.push_back(inpt); 
    return out; 
}

std::string Tools::join(std::vector<std::string>* inpt, int index_s, int index_e, std::string delim)
{
    std::string out = ""; 
    if (index_e < 0){ index_e = inpt -> size(); }
    for (int i(index_s); i < index_e-1; ++i){ 
        out += inpt -> at(i) + delim; 
    }
    out += inpt -> at(index_e-1); 
    return out; 
}

int Tools::count(std::string inpt, std::string search)
{
    int index = 0; 
    int s_size = search.length(); 
    if (!s_size){return 0;}

    std::string::size_type i = inpt.find(search); 
    while ( i != std::string::npos){
        ++index; 
        i = inpt.find(search, i + s_size); 
    }
    return index; 
}

static const std::string base64_chars = 
             "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
             "abcdefghijklmnopqrstuvwxyz"
             "0123456789+/";


static inline bool is_base64(unsigned char c) {return (isalnum(c) || (c == '+') || (c == '/'));}

std::string Tools::base64_encode(unsigned char const* bytes_to_encode, unsigned int in_len) 
{
    std::string ret;
    int i = 0;
    int j = 0;
    unsigned char char_array_3[3];
    unsigned char char_array_4[4];
    
    while (in_len--) {
        char_array_3[i++] = *(bytes_to_encode++);
        if (i == 3){
            char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
            char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
            char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
            char_array_4[3] = char_array_3[2] & 0x3f;

            for (i = 0; (i <4) ; i++){ret += base64_chars[char_array_4[i]];}
            i = 0;
        }
    }

    if (i){
        for(j = i; j < 3; j++){char_array_3[j] = '\0';}
        char_array_4[0] = (char_array_3[0] & 0xfc) >> 2;
        char_array_4[1] = ((char_array_3[0] & 0x03) << 4) + ((char_array_3[1] & 0xf0) >> 4);
        char_array_4[2] = ((char_array_3[1] & 0x0f) << 2) + ((char_array_3[2] & 0xc0) >> 6);
        char_array_4[3] = char_array_3[2] & 0x3f;
        for (j = 0; (j < i + 1); j++){ret += base64_chars[char_array_4[j]];}
        while((i++ < 3)){ret += '=';}
    }
    return ret;
}

std::string Tools::base64_decode(std::string const& encoded_string) 
{
    size_t in_len = encoded_string.size();
    size_t i = 0;
    size_t j = 0;
    int in_ = 0;
    unsigned char char_array_4[4], char_array_3[3];
    std::string ret;

    while (in_len-- && ( encoded_string[in_] != '=') && is_base64(encoded_string[in_])) {
        char_array_4[i++] = encoded_string[in_]; in_++;
        if (i ==4) {
            for (i = 0; i <4; i++){
                char_array_4[i] = static_cast<unsigned char>(base64_chars.find(char_array_4[i]));
            }
            char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
            char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
            char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];

            for (i = 0; (i < 3); i++){ret += char_array_3[i];}
            i = 0;
        }
    }
    
    if (i) {
        for (j = i; j <4; j++){char_array_4[j] = 0;}
        for (j = 0; j <4; j++){
            char_array_4[j] = static_cast<unsigned char>(base64_chars.find(char_array_4[j]));
        }
        char_array_3[0] = (char_array_4[0] << 2) + ((char_array_4[1] & 0x30) >> 4);
        char_array_3[1] = ((char_array_4[1] & 0xf) << 4) + ((char_array_4[2] & 0x3c) >> 2);
        char_array_3[2] = ((char_array_4[2] & 0x3) << 6) + char_array_4[3];
        for (j = 0; (j < i - 1); j++) ret += char_array_3[j];
    }
    return ret;
}

std::map<std::string, int> Tools::CheckDifference(std::vector<std::string> inpt1, std::vector<std::string> inpt2, int threads)
{
    auto Scan = [](std::map<std::string, int>* inpt, std::vector<std::string>* check){
        for (unsigned int x = 0; x < check -> size(); ++x){
            if (!inpt -> count(check -> at(x))){continue;}
            (*inpt)[check -> at(x)] += 1; 
        } 
    };  

    std::vector<std::thread*> thrds; 
    std::vector<std::map<std::string, int>*> maps = {}; 
    std::vector<std::vector<std::string>> data = Quantize(inpt1, threads); 
    for (unsigned int x = 0; x < data.size(); ++x){
        std::map<std::string, int>* t = new std::map<std::string, int>(); 
        for (std::string p : data[x]){ (*t)[p] = 0; }
        std::thread* jb = new std::thread(Scan, t, &inpt2); 

        maps.push_back(t); 
        thrds.push_back(jb); 
        
        int run_i = 0; 
        for (unsigned int t(0); t < thrds.size(); ++t){
            run_i += thrds[t] -> joinable(); 
        }
        if (run_i >= threads){jb -> join();}
    }

    std::map<std::string, int> output; 
    for (unsigned int x = 0; x < thrds.size(); ++x){
        std::map<std::string, int>* trg = maps[x]; 
        std::thread* jb = thrds[x]; 
        if (jb -> joinable()){jb -> join();}

        std::map<std::string, int>::iterator itr = trg -> begin(); 
        for (; itr != trg -> end(); ++itr){
            if (itr -> second){continue;}
            output[itr -> first] += itr -> second; 
        }
        trg -> clear();
        delete trg; 
        delete jb;  
    }; 
    return output; 
}


namespace Abstraction
{
    CyBase::CyBase(){}
    CyBase::~CyBase(){}
    void CyBase::Hash(std::string inpt){
        if ((this -> hash).size()){ return; }
        this -> hash = Tools::Hashing( inpt ); 
    }

    CyEvent::CyEvent(){}
    CyEvent::~CyEvent(){}

    void CyEvent::ImportMetaData(meta_t meta){
        this -> meta = meta;
    }
}
