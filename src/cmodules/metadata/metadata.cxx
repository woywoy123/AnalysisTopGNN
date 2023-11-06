#include "../metadata/metadata.h"

namespace SampleTracer
{
    CyMetaData::CyMetaData(){}
    CyMetaData::~CyMetaData(){}

    meta_t CyMetaData::Export(){return this -> container;}
    void CyMetaData::Import(meta_t meta){this -> container = meta;}

    void CyMetaData::addsamples(int index, int range, std::string sample)
    {
        this -> container.inputfiles[index] = sample;
        this -> container.inputrange[index] = range;
    }

    void CyMetaData::addconfig(std::string key, std::string val)
    {
        this -> container.config[key] = val;
    }

    void CyMetaData::Hash()
    {
        std::string dsid = Tools::ToString(this -> container.dsid); 
        this -> CyBase::Hash(dsid);
    }

    void CyMetaData::processkeys(std::vector<std::string> keys, unsigned int num)
    {
        auto scanthis = [](
                std::vector<std::string>* req, std::vector<std::string>* tokens,
                std::vector<std::string>* res, std::string key)
        {
            for (unsigned int i(0); i < req -> size(); ++i)
            {
                std::string tmp = req -> at(i);
                if (!Tools::count(key, tmp)){ continue; }
                for (unsigned x(0); x < tokens -> size(); ++x)
                {
                    std::string tok = tokens -> at(x);
                    if (!Tools::count(tok, tmp + ";") && tmp != tok){continue;}

                    res -> push_back(tmp);
                    res -> push_back(tok);
                    return;
                }
            }
        };

        auto search = [&scanthis](
                std::vector<std::string>* r_tree,
                std::vector<std::string>* r_branch,
                std::vector<std::string>* r_leaf,
                std::string* key, collect_t* tr)
        {
            std::vector<std::string> _tree   = {};
            std::vector<std::string> _branch = {};
            std::vector<std::string> _leaf   = {};

            std::vector<std::string> tokens = Tools::split(*key, "/");
            scanthis(r_tree  , &tokens, &_tree  , *key);
            scanthis(r_branch, &tokens, &_branch, *key);
            scanthis(r_leaf  , &tokens, &_leaf  , *key);

            bool lx =   _leaf.size() > 0;
            bool bx = _branch.size() > 0;
            bool tx =   _tree.size() > 0;
            tr -> valid = lx + bx + tx > 0;

            tr ->  lf_requested += (lx) ? _leaf[0] : "";
            tr ->  lf_matched   += (lx) ? _leaf[1] : "";
            tr ->  lf_path      += (lx) ? Tools::join(&tokens, 1, -1, "/") : "";

            tr ->  br_requested += (bx) ? _branch[0] : "";
            tr ->  br_matched   += (bx) ? _branch[1] : "";

            tr ->  tr_requested += (tx) ? _tree[0] : "";
            tr ->  tr_matched   += (tx) ? _tree[1] : "";

            tokens.clear(); 
            _tree.clear(); 
            _branch.clear(); 
            _leaf.clear(); 

        };

        std::vector<std::string>* tr = &(this -> container.req_trees);
        std::vector<std::string>* br = &(this -> container.req_branches);
        std::vector<std::string>* lf = &(this -> container.req_leaves);

        std::vector<collect_t*> check = {};
        std::vector<std::thread*> jbs = {};
        for (unsigned int i(0); i < keys.size(); ++i)
        {
            check.push_back(new collect_t());
            std::thread* p = new std::thread(search, tr, br, lf, &keys[i], check[i]);
            jbs.push_back(p);
        }
        for (unsigned int x(0); x < jbs.size(); ++x){jbs[x] -> join(); delete jbs[x];}
        std::map<std::string, tree_t>* trees = &(this -> container.trees);
        std::map<std::string, branch_t>* branches = &(this -> container.branches);
        std::map<std::string, leaf_t>* leaves = &(this -> container.leaves);

        for (unsigned int x(0); x < check.size(); ++x)
        {
            collect_t* col = check[x];
            std::string tr_get = col -> tr_requested;
            std::string br_get = col -> br_requested;
            std::string lf_get = col -> lf_requested;
            if (!col -> valid){delete col; continue;}

            if (!trees -> count(tr_get) && tr_get.size())
            {
                tree_t tmp;
                tmp.size = num;
                tmp.requested = col -> tr_requested;
                tmp.matched   = col -> tr_matched;
                (*trees)[tr_get] = tmp;
            }

            if (!branches -> count(tr_get) && br_get.size())
            {
                branch_t tmp;
                tmp.requested = col -> br_requested;
                tmp.matched   = col -> br_matched;
                (*branches)[br_get] = tmp;
            }

            if (!leaves -> count(lf_get) && lf_get.size())
            {
                leaf_t tmp;
                tmp.requested = col -> lf_requested;
                tmp.matched   = col -> lf_matched;
                tmp.path      = col -> lf_path;
                (*leaves)[lf_get] = tmp;
            }


            // Do the linking here
            if (lf_get.size())
            {
                leaf_t* lfc = &(leaves -> at(lf_get));
                lfc -> branch_name = br_get;
                lfc -> tree_name = tr_get;

                if (br_get.size()){ (*branches)[br_get].leaves.push_back(*lfc); }
                if (tr_get.size()){ (*trees)[tr_get].leaves.push_back(*lfc); }
            }

            if (br_get.size())
            {
                branch_t* brc = &branches -> at(br_get);
                brc -> tree_name = tr_get;
                if (tr_get.size()){ trees -> at(tr_get).branches.push_back(*brc); }
            }
            delete col; 
        }
    }

    void CyMetaData::FindMissingKeys()
    {
        std::vector<std::string>* r_trees      = &(this -> container.req_trees);
        std::vector<std::string>* m_trees      = &(this -> container.mis_trees);
        std::map<std::string, tree_t>* f_trees = &(this -> container.trees);
        this -> _check_this(r_trees, m_trees, f_trees); 

        std::vector<std::string>* r_branches      = &(this -> container.req_branches);
        std::vector<std::string>* m_branches      = &(this -> container.mis_branches);
        std::map<std::string, branch_t>* f_branches = &(this -> container.branches);
        this -> _check_this(r_branches, m_branches, f_branches); 

        std::vector<std::string>* r_leaves      = &(this -> container.req_leaves);
        std::vector<std::string>* m_leaves      = &(this -> container.mis_leaves);
        std::map<std::string, leaf_t>* f_leaves = &(this -> container.leaves);
        this -> _check_this(r_leaves, m_leaves, f_leaves); 
    }

    std::map<std::string, std::vector<std::string>> CyMetaData::MakeGetter()
    {
        std::map<std::string, std::vector<std::string>> output = {};

        std::map<std::string, tree_t>* trees = &(this -> container.trees);
        std::map<std::string, tree_t>::iterator it = trees -> begin();
        for (; it != trees -> end(); ++it)
        {
            output[it -> first] = {};
            for (unsigned int x(0); x < it -> second.leaves.size(); ++x)
            {
                leaf_t* _lf = &(it -> second.leaves[x]);
                std::string get = _lf -> path;
                output[it -> first].push_back(get);
            }
        }
        return output;
    }

    std::map<std::string, int> CyMetaData::GetLength()
    {
        std::map<std::string, int> index = {};
        std::map<std::string, tree_t>* trees = &(this -> container.trees); 
        std::map<std::string, tree_t>::iterator it = trees -> begin();
        for (; it != trees -> end(); ++it)
        {
            index[it -> first] = it -> second.size;
        }
        return index;
    }

    std::string CyMetaData::IndexToSample(int index)
    {
        std::map<int, std::string>::iterator it;
        std::map<int, std::string>* x = &(this -> container.inputfiles);
        std::map<int, int>* ranges = &(this -> container.inputrange); 
        for (it = x -> begin(); it != x -> end(); ++it)
        {
            int iter = it -> first;
            if (index >= ranges -> at(iter)){continue;}
            return it -> second;
        }
        return this -> container.original_name;     
    }

    std::string CyMetaData::DatasetName()
    {
        meta_t* con = &(this -> container); 
        if (con -> DatasetName.size()){ return con -> DatasetName; }
        std::map<int, std::string>::iterator it; 
        it = con -> inputfiles.begin();  

        std::string dsid = Tools::ToString( con -> dsid ); 
        std::vector<std::string> col = {}; 
        for (; it != con -> inputfiles.end(); ++it)
        {
            std::string f_name = it -> second; 
            if (!Tools::count( f_name, dsid )){continue;} 
            col.push_back(f_name); 
        }
        if (!col.size()){ return con -> DatasetName; }
        for (std::string token : Tools::split(col[0], "/"))
        {
            if (!Tools::count( token, dsid )){continue;}
            con -> DatasetName = token; 
            return con -> DatasetName; 
        }
        return con -> DatasetName; 
    }; 

    std::vector<std::string> CyMetaData::DAODList()
    {
        meta_t* con = &(this -> container); 
        std::vector<std::string> out; 

        if (con -> LFN.size())
        { 
            std::map<std::string, int>::iterator it; 
            it = con -> LFN.begin(); 
            for (; it != con -> LFN.end(); ++it)
            {
                out.push_back(it -> first); 
            }
            return out; 
        }
        std::map<int, std::string>::iterator itr; 
        itr = con -> inputfiles.begin();
        for (; itr != con -> inputfiles.end(); ++itr)
        {
            out.push_back( itr -> second ); 
        }
        return out; 
    }; 


}
