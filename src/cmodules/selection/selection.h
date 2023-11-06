#include "../abstractions/abstractions.h"
#include "../abstractions/cytypes.h"
#include <chrono>
#include <cmath>

#ifndef SELECTION_H
#define SELECTION_H

namespace CyTemplate
{
    class CySelectionTemplate : public Abstraction::CyEvent
    {
        public:
            CySelectionTemplate(); 
            ~CySelectionTemplate(); 
            
            bool operator == (CySelectionTemplate&); 
            bool operator != (CySelectionTemplate&); 
            void operator += (CySelectionTemplate&); 
            CySelectionTemplate* operator + (CySelectionTemplate&); 
            void iadd(CySelectionTemplate*); 
            
            std::string Hash(); 
            selection_t Export(); 
            void Import(selection_t); 
            void RegisterEvent(const event_t* evnt); 

            bool CheckSelection(bool); 
            bool CheckSelection(std::string); 

            bool CheckStrategy(bool); 
            bool CheckStrategy(std::string); 

            void StartTime(); 
            void EndTime();

            double Mean();
            double StandardDeviation();
            double Luminosity();

        private: 
            selection_t* sel; 
            std::chrono::high_resolution_clock::time_point ts; 
            std::chrono::high_resolution_clock::time_point te; 
            double current_weight = 1; 
    }; 
}

#endif
