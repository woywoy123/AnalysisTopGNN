#include "../abstractions/cytypes.h"
#include "../selection/selection.h"
#include "../event/event.h"
#include "../graph/graph.h"

#ifndef ROOT_H
#define ROOT_H

using namespace CyTemplate; 

namespace SampleTracer
{
    class CyBatch
    {
        public:
            CyBatch(std::string hash); 
            ~CyBatch(); 
            std::string Hash(); 
            void Import(const meta_t*); 
            void Import(const event_t*);
            void Import(const graph_t*); 
            void Import(const selection_t*); 
            void Import(const batch_t*); 

            batch_t ExportPickled(); 
            void ImportPickled(const batch_t*); 

            batch_t Export(); 
            void Export(batch_t* exp); 

            void Contextualize(); 
            void ApplySettings(const settings_t*); 
            void LinkCode(
                    std::map<std::string, std::string>* inpt, 
                    std::map<std::string, Code::CyCode*>* link, 
                    const std::map<std::string, Code::CyCode*>* code_h); 

            void ApplyCodeHash(const std::map<std::string, Code::CyCode*>*);

            std::map<std::string, CyEventTemplate*> events; 
            std::map<std::string, CyGraphTemplate*> graphs; 
            std::map<std::string, CySelectionTemplate*> selections; 
           
            std::string hash = ""; 

            const meta_t* meta;
            bool lock_meta = false;
            
            // Object Context
            bool get_event = false; 
            bool get_graph = false; 
            bool get_selection = false;
            bool valid = false; 

            CyEventTemplate* this_ev = nullptr; 
            CyGraphTemplate* this_gr = nullptr; 
            CySelectionTemplate* this_sel = nullptr; 

            std::string this_tree = "";
            std::string this_event_name = ""; 
            std::string this_graph_name = "";
            std::string this_selection_name = ""; 

            std::map<std::string, std::string> event_dir = {}; 
            std::map<std::string, std::string> graph_dir = {}; 
            std::map<std::string, std::string> selection_dir = {};  
            std::map<std::string, Code::CyCode*> code_hashes = {};

            template <typename G> 
            void destroy(std::map<std::string, G*>* input)
            {
                typename std::map<std::string, G*>::iterator it; 
                it = input -> begin(); 
                for (; it != input -> end(); ++it){delete it -> second;}
                input -> clear(); 
            };

            template <typename G>
            G* find(std::map<std::string, G*>* input, std::string name)
            {
                typename std::map<std::string, G*>::iterator itr; 
                for (itr = input -> begin(); itr != input -> end(); ++itr){
                    if (!Tools::count(itr -> first, name)){continue;}
                    return itr -> second;      
                }
                return nullptr; 
            }; 

            bool find(std::map<std::string, std::string>* input, std::string name)
            {
                std::map<std::string, std::string>::iterator itr; 
                for (itr = input -> begin(); itr != input -> end(); ++itr){
                    if (!Tools::count(itr -> first, name)){continue;}
                    return true;
                }
                return false; 
            }; 

        private: 
            template <typename G, typename T>
            void export_this(G* inpt, std::map<std::string, T>* out)
            {
                std::string event_name;
                std::string event_tree;
                if (inpt -> is_event){ 
                    event_name = inpt -> event.event_name; 
                    event_tree = inpt -> event.event_tree; 
                }
                else if (inpt -> is_graph){ 
                    event_name = inpt -> graph.event_name; 
                    event_tree = inpt -> graph.event_tree;
                }
                else if (inpt -> is_selection){ 
                    event_name = inpt -> selection.event_name; 
                    event_tree = inpt -> selection.event_tree;
                }

                (*out)[event_tree + "/" + event_name] = inpt -> Export();
            }; 

            template <typename G, typename T>
            void export_this(std::map<std::string, G*> inpt, std::map<std::string, T>* out)
            {
                typename std::map<std::string, G*>::iterator it = inpt.begin();
                for (; it != inpt.end(); ++it){
                    (*out)[it -> first] = it -> second -> Export();
                }
            }; 

            template <typename G>
            void code_link(std::map<std::string, G*> event, const std::map<std::string, Code::CyCode*>* code_h)
            {
                typename std::map<std::string, G*>::iterator it; 
                it = event.begin();
                for (; it != event.end(); ++it){
                    std::string code_hash; 
                    G* entry = it -> second; 
                    if (entry -> is_event){code_hash = entry -> event.code_hash;}
                    else if (entry -> is_graph){code_hash = entry -> graph.code_hash;}
                    else if (entry -> is_selection){code_hash = entry -> selection.code_hash;}
                    if (!code_h -> count(code_hash)){ continue; }
                    entry -> code_link = code_h -> at(code_hash);
                } 
            }; 

            template <typename G>
            void export_code(std::map<std::string, G*> entry, std::map<std::string, code_t>* out)
            {
                std::map<std::string, Code::CyCode*>::iterator itc; 
                typename std::map<std::string, G*>::iterator it; 
                it = entry.begin(); 
                for (; it != entry.end(); ++it){
                    Code::CyCode* link = it -> second -> code_link; 
                    itc = link -> dependency.begin(); 
                    for (; itc != link -> dependency.end(); ++itc){
                        (*out)[itc -> first] = itc -> second -> ExportCode();
                    }
                    (*out)[link -> hash] = link -> ExportCode(); 
                }
            }; 

            template<typename G>
            void not_code_owner(std::map<std::string, G*>* type)
            {
                typename std::map<std::string, G*>::iterator it;
                it = type -> begin(); 
                for (; it != type -> end(); ++it){it -> second -> code_owner = false;}
            };
    }; 

    class CyROOT
    {
        public:
            CyROOT(meta_t meta);  
            ~CyROOT(); 

            root_t Export(); 
            void Import(const root_t* inpt); 

            void ReleaseObjects(std::map<std::string, std::vector<CyEventTemplate*>>*); 
            void ReleaseObjects(std::map<std::string, std::vector<CyGraphTemplate*>>*); 
            void ReleaseObjects(std::map<std::string, std::vector<CySelectionTemplate*>>*); 

            void AddEvent(const event_t* event);
            void AddGraph(const graph_t* graph);
            void AddSelection(const selection_t* selection);
            void UpdateSampleStats(); 
            
            meta_t meta;
            std::map<std::string, CyBatch*> batches;
            std::map<std::string, int> n_events = {};
            std::map<std::string, int> n_graphs = {}; 
            std::map<std::string, int> n_selections = {};
            std::map<std::string, int> event_trees = {}; 

            int total_hashes = 0; 
        
        private: 
            template<typename G> 
            void ImportBatch(
                    const std::map<std::string, G>* to_import, 
                    std::map<std::string, CyBatch*>* batches, 
                    const meta_t* meta)
            {
                typename std::map<std::string, G>::const_iterator it; 
                it = to_import -> begin();
                for (; it != to_import -> end(); ++it){
                    const std::string event_h = it -> second.event_hash; 
                    CyBatch* bt; 
                    if (!batches -> count(event_h)){
                        bt = new CyBatch(event_h); 
                        (*batches)[event_h] = bt;
                        bt -> hash = event_h; 
                    }
                    else {bt = batches -> at(event_h);} 
                    bt -> Import(meta); 
                    bt -> Import(&it -> second); 
                    std::string name = it -> second.event_name; 
                    std::string tree = it -> second.event_tree;
                    std::string key = tree + "/" + name;  
                    if (it -> second.event){this -> n_events[key] += 1;}
                    else if (it -> second.graph){this -> n_graphs[key] += 1;}
                    else if (it -> second.selection){this -> n_selections[key] += 1;}
                }
            };
            template <typename T>
            static void _make_path(T* evnt, std::string* pth){
                *pth += evnt -> event_tree + "." + evnt -> event_name;
            };

            static void _get(std::map<std::string, CyEventTemplate*>* get, CyBatch* bt){
                *get = bt -> events;  
            };

            static void _get(std::map<std::string, CyGraphTemplate*>* get, CyBatch* bt){
                *get = bt -> graphs;  
            };

            static void _get(std::map<std::string, CySelectionTemplate*>* get, CyBatch* bt){
                *get = bt -> selections;  
            };

            static bool _get_T(CyEventTemplate* inpt, std::string* path){
                event_t* ev = &(inpt -> event);
                if (ev -> cached){return true;}
                _make_path(ev, path);
                return false;
            };

            static bool _get_T(CyGraphTemplate* inpt, std::string* path){
                graph_t* gr = &(inpt -> graph);
                if (gr -> cached){return true;}
                _make_path(gr, path);
                return false;
            };

            static bool _get_T(CySelectionTemplate* inpt, std::string* path){
                selection_t* se = &(inpt -> selection);
                if (se -> cached){return true;}
                _make_path(se, path);
                return false;
            };

            template <typename G>
            void ReleaseData(std::map<std::string, std::vector<G*>>* out)
            {
                typename std::map<std::string, G*> obj; 
                typename std::map<std::string, G*>::iterator it; 

                std::map<std::string, CyBatch*>::iterator itr; 
                itr = this -> batches.begin(); 
                for (; itr != this -> batches.end(); ++itr){
                    _get(&obj, itr -> second); 
                    it = obj.begin();
                    for (; it != obj.end(); ++it){
                        std::string path = ""; 
                        if (_get_T(it -> second, &path)){continue;}
                        (*out)[path].push_back(it -> second);
                    }
                }
            };
    };
}
#endif
