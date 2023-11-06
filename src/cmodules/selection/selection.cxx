#include "../selection/selection.h"

namespace CyTemplate
{
    CySelectionTemplate::CySelectionTemplate()
    {
        this -> sel = &(this -> selection); 
        this -> is_selection = true;  
    }

    CySelectionTemplate::~CySelectionTemplate(){}

    bool CySelectionTemplate::operator == (CySelectionTemplate& selection)
    {
        selection_t* gr2 = &(selection.selection); 
        return this -> is_same(this -> sel, gr2);
    }

    bool CySelectionTemplate::operator != (CySelectionTemplate& selection)
    {
        selection_t* gr2 = &(selection.selection); 
        return !this -> is_same(this -> sel, gr2);
    }
    
    void CySelectionTemplate::operator += (CySelectionTemplate& selection)
    {
        selection_t* sel1 = this -> sel; 
        selection_t* sel2 = selection.sel; 

        std::map<std::string, int>::iterator it_i; 
        it_i = sel2 -> cutflow.begin(); 
        for (; it_i != sel2 -> cutflow.end(); ++it_i){
            sel1 -> cutflow[it_i -> first] += it_i -> second;  
        }; 

        it_i = sel2 -> errors.begin(); 
        for (; it_i != sel2 -> errors.end(); ++it_i){
            sel1 -> errors[it_i -> first] += it_i -> second;  
        }; 

        std::vector<double>* x1; 
        std::vector<double>* x2; 
        x1 = &(sel1 -> timestats); 
        x2 = &(sel2 -> timestats); 
        x1 -> insert(x1 -> end(), x2 -> begin(), x2 -> end()); 

        x1 = &(sel1 -> all_weights); 
        x2 = &(sel2 -> all_weights); 
        x1 -> insert(x1 -> end(), x2 -> begin(), x2 -> end()); 

        x1 = &(sel1 -> selection_weights); 
        x2 = &(sel2 -> selection_weights); 
        x1 -> insert(x1 -> end(), x2 -> begin(), x2 -> end()); 

        if (sel2 -> pickled_data.size()){
            sel1 -> data_merge[sel2 -> event_hash] = sel2 -> pickled_data; 
        }
        if (sel2 -> pickled_strategy_data.size()){
            sel1 -> strat_merge[sel2 -> event_hash] = sel2 -> pickled_strategy_data; 
        }
    }

    CySelectionTemplate* CySelectionTemplate::operator + (CySelectionTemplate& sel)
    {
        CySelectionTemplate* out = new CySelectionTemplate();
        out -> Import(this -> selection);
        *out += sel;
        return out;
    }

    std::string CySelectionTemplate::Hash()
    {
        return this -> CyEvent::Hash(&(this -> selection)); 
    }

    void CySelectionTemplate::iadd(CySelectionTemplate* sel)
    {
        *this += *sel; 
    }

    selection_t CySelectionTemplate::Export()
    {
        this -> selection.selection = true; 
        return this -> selection;     
    }

    void CySelectionTemplate::Import(selection_t sel)
    {
        this -> selection = sel; 
        this -> selection.selection = true; 
        this -> is_selection = true; 
    }

    void CySelectionTemplate::RegisterEvent(const event_t* evnt)
    {
        selection_t* sel = &(this -> selection); 
        this -> set_event_hash(sel, evnt); 
        this -> set_event_tag(sel, evnt); 
        this -> set_event_tree(sel, evnt); 
        this -> set_event_root(sel, evnt);
        this -> set_event_index(sel, evnt);
        this -> set_event_weight(sel, evnt); 
        this -> current_weight = evnt -> weight; 
        sel -> all_weights.push_back(evnt -> weight); 
    }
    
    bool CySelectionTemplate::CheckSelection(bool passed)
    {
        if (passed){ this -> sel -> cutflow["Selection::Passed"] += 1; }
        else { this -> sel -> cutflow["Selection::Rejected"] += 1; }
        return passed; 
    }

    bool CySelectionTemplate::CheckSelection(std::string passed)
    {
        int pass; 
        passed = "Selection::" + passed; 
        pass = Tools::count(passed, "::Passed"); 
        if (pass){ this -> sel -> cutflow[passed] += 1; return true;}
        
        pass = Tools::count(passed, "::Rejected"); 
        if (pass){ this -> sel -> cutflow[passed] += 1; return false;}
        
        pass = Tools::count(passed, "::Error"); 
        if (pass){ this -> sel -> cutflow[passed] += 1; return false;}

        this -> sel -> cutflow[passed + "::Ambiguous"] +=1; 
        return true;
    }

    bool CySelectionTemplate::CheckStrategy(bool passed)
    {
        if (passed){ this -> sel -> cutflow["Strategy::Passed"] += 1; }
        else { this -> sel -> cutflow["Strategy::Rejected"] += 1; }
        return passed; 
    }

    bool CySelectionTemplate::CheckStrategy(std::string passed)
    {
        int pass; 
        passed = "Strategy::" + passed; 
        pass = Tools::count(passed, "::Passed"); 
        if (pass){ 
            this -> sel -> cutflow[passed] += 1; 
            this -> sel -> selection_weights.push_back(this -> current_weight);
            return true;
        }

        if (Tools::count(passed, "->")){
            this -> sel -> cutflow[passed] += 1; 
            this -> sel -> selection_weights.push_back(this -> current_weight); 
            return true;
        }
  
        pass = Tools::count(passed, "::Rejected"); 
        if (pass){ this -> sel -> cutflow[passed] += 1; return false;}
        
        pass = Tools::count(passed, "::Error"); 
        if (pass){ this -> sel -> cutflow[passed] += 1; return false;}

        this -> sel -> cutflow[passed + "::Ambiguous"] +=1;
        this -> sel -> selection_weights.push_back(this -> current_weight); 
        return true;
    }

    void CySelectionTemplate::StartTime()
    {
        this -> ts = std::chrono::high_resolution_clock::now(); 
    }

    void CySelectionTemplate::EndTime()
    {        
        this -> te = std::chrono::high_resolution_clock::now(); 
        double tf = std::chrono::duration_cast<std::chrono::nanoseconds>(this -> te - this -> ts).count(); 
        this -> sel -> timestats.push_back(tf); 
    }

    double CySelectionTemplate::Mean()
    {
        double out = 0; 
        for (double i : this -> sel -> timestats){out += i;}
        if (!this -> sel -> timestats.size()){return out;}
        return (out/this -> sel -> timestats.size()); 
    }    

    double CySelectionTemplate::StandardDeviation()
    {
        double mean = this -> Mean(); 
        double out = 0; 
        for (double i : this -> sel -> timestats){ out += std::pow(i - mean, 2); }
        mean = this -> sel -> timestats.size(); 
        if (!mean){return -1;}
        return std::pow(out / mean, 0.5); 
    }

    double CySelectionTemplate::Luminosity()
    {
        double sel_sum = 0; 
        double all_sum = 0; 
        for (double i : this -> sel -> selection_weights){sel_sum += i;}
        for (double i : this -> sel -> all_weights){all_sum += i;}
        if (!all_sum){return -1;}
        return sel_sum/all_sum; 
    }
}
