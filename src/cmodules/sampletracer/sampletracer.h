#include "../metadata/metadata.h"
#include "../root/root.h"
#include <algorithm>

#ifndef SAMPLETRACER_H
#define SAMPLETRACER_H


struct HDF5_t
{
    std::string root_name = ""; 
    std::map<std::string, std::string> cache_path = {}; 
};

static void Search(
        SampleTracer::CyROOT* root, settings_t* apply, 
        std::vector<SampleTracer::CyBatch*>* out, 
        std::map<std::string, Code::CyCode*>* code_hashes)
{
    std::map<std::string, SampleTracer::CyBatch*>::iterator itb; 
    itb = root -> batches.begin(); 
    for (; itb != root -> batches.end(); ++itb){
        SampleTracer::CyBatch* this_b = itb -> second; 
        this_b -> ApplySettings(apply);  
    
        if (!this_b -> valid){continue;}
        this_b -> ApplyCodeHash(code_hashes); 
        out -> push_back(this_b); 
    }
}; 


namespace SampleTracer
{
    namespace CyHelpers
    {
        static void ExportCode(
                std::map<std::string, code_t>* output, 
                std::map<std::string, Code::CyCode*> code_hashes)
        {
            std::map<std::string, Code::CyCode*>::iterator itc;
            itc = code_hashes.begin();
            for (; itc != code_hashes.end(); ++itc){
                Code::CyCode* code = itc -> second; 
                if (!code -> container.object_code.size()){continue;}
                (*output)[itc -> first] = code -> ExportCode();
            }
        }; 

        static void ImportCode(
                std::map<std::string, Code::CyCode*>* output,
                std::map<std::string, code_t>* hashed_code) 
        {
            std::map<std::string, code_t>::iterator itc; 
            itc = hashed_code -> begin(); 
            for (; itc != hashed_code -> end(); ++itc){
                code_t* co = &(itc -> second); 
                if (!co -> object_code.size()){continue;}
                if (output -> count(co -> hash)){ continue; }
                Code::CyCode* co_ = new Code::CyCode();
                co_ -> ImportCode(*co, *hashed_code); 
                (*output)[co -> hash] = co_;
            }
        }; 
    }

    class CySampleTracer
    {
        public:
            CySampleTracer(); 
            ~CySampleTracer(); 

            template<typename G>
            CyROOT* AddContent(G* type, meta_t* meta, std::map<std::string, CyROOT*>* root)
            {
                std::string event_root = type -> event_root; 
                if (!root -> count(event_root)){(*root)[event_root] = new CyROOT(*meta);}
                return root -> at(event_root); 
            }; 
            
            template <typename G>
            void ReleaseObjects(std::map<std::string, std::vector<G*>>* out)
            {
                std::map<std::string, CyROOT*>* roots = &(this -> root_map);
                std::map<std::string, CyROOT*>::iterator itr = roots -> begin();
                typename std::map<std::string, std::vector<G*>>::iterator itG;
                typename std::map<std::string, std::vector<G*>> tmp;
                typename std::vector<G*> app; 
                for (; itr != roots -> end(); ++itr){
                    tmp = {}; 
                    std::string r_name = itr -> first; 
                    itr -> second -> ReleaseObjects(&tmp); 
                    itG = tmp.begin(); 
                    for(; itG != tmp.end(); ++itG){
                        app = itG -> second; 
                        std::string name = r_name + ":" + itG -> first; 
                        (*out)[name].insert((*out)[name].end(), app.begin(), app.end());
                    }
                }
            }; 
            
            template <typename G, typename T>
            std::map<std::string, std::string> make_flush_string(G* ev, std::string subkey, std::map<std::string, T*>* mp)
            {
                std::string cache_path = ""; 
                cache_path += this -> settings.outputdirectory; 
                cache_path += this -> settings.projectname + "/" + subkey + "/"; 

                std::string h5_name = ev -> event_root;
                if (h5_name.rfind(".root.1") == std::string::npos){}
                else {h5_name.erase(h5_name.rfind(".root.1"), h5_name.size()-1);}
                h5_name += ".hdf5";

                typename std::map<std::string, T*>::iterator itr = mp -> begin(); 
                std::map<std::string, std::string> output; 
                for (; itr != mp -> end(); ++itr){
                    std::vector<std::string> x = Tools::split(itr -> first, "/");
                    std::string name_ = cache_path + x[0] + "." + x[1] + "/" + h5_name;
                    output[name_] = ev -> event_root; 
                } 
                return output;
            }; 

            void AddMeta(meta_t, std::string);
            void AddEvent(event_t event, meta_t meta);
            void AddGraph(graph_t graph, meta_t meta); 
            void AddSelection(selection_t selection, meta_t meta); 
            void AddCode(code_t code); 

            std::map<std::string, std::string> RestoreTracer(std::map<std::string, HDF5_t>* data, std::string event_root); 
            std::map<std::string, std::vector<CyBatch*>> RestoreCache(std::string type); 

            CyBatch* RegisterHash(std::string hash, std::string event_root); 

            std::map<std::string, std::vector<CyEventTemplate*>> DumpEvents(); 
            std::map<std::string, std::vector<CyGraphTemplate*>> DumpGraphs(); 
            std::map<std::string, std::vector<CySelectionTemplate*>> DumpSelections();

            void FlushEvents(std::vector<std::string> hashes); 
            void FlushGraphs(std::vector<std::string> hashes); 
            void FlushSelections(std::vector<std::string> hashes); 

            void DumpTracer();

            tracer_t Export(); 
            void Import(tracer_t inpt);

            settings_t ExportSettings();
            void ImportSettings(settings_t inpt); 

            std::vector<CyBatch*> MakeIterable(); 
            std::map<std::string, int> length();  

            CySampleTracer* operator + (CySampleTracer*); 
            void operator += (CySampleTracer*);
            void iadd(CySampleTracer*); 

            std::map<std::string, std::string> link_event_code = {}; 
            std::map<std::string, std::string> link_graph_code = {};
            std::map<std::string, std::string> link_selection_code = {}; 
            std::map<std::string, Code::CyCode*> code_hashes = {};
            std::map<std::string, CyROOT*> root_map = {}; 

            export_t state;
            settings_t settings; 
            std::string caller = ""; 
            std::map<std::string, int> event_trees = {}; 
    }; 
}

#endif
