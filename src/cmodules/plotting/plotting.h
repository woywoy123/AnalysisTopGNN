#include "../abstractions/abstractions.h"
#include "../abstractions/cytypes.h"

#ifndef PLOTTING_H
#define PLOTTING_H

#include <algorithm>
#include <iostream>
#include <cmath>
#include <vector>
#include <map>


struct paint_t
{
    float n_events = 0; 

    bool atlas_style = false; 
    bool root_style = false; 
    bool mpl_style = true; 
    bool autoscale = true;
    bool latex = true;

    std::string color = ""; 
    std::vector<std::string> colors = {}; 

    std::string marker = "."; 
    std::vector<std::string> markers = {
        ",", ".", "--", "x", "o", "O"
    }; 

    std::string texture = "";
    std::vector<std::string> textures = {
        "/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"
    }; 

    float xscaling = 1.25*6.4; 
    float yscaling = 1.25*4.8;
    float alpha = 0.5; 
    float line_width = 1; 

    float font_size = 10; 
    float label_size = 12.5; 
    float title_size = 10; 
    float legend_size = 10;
    std::string legend_loc = "best"; 
    std::string hist_fill = "fill"; 

    int atlas_loc = 1; 
    float atlas_lumi = -1; 
    float atlas_com = -1;
    float atlas_year = -1;
    bool atlas_data = false; 
};

struct axis_t
{
    std::string title = ""; 
    std::string dim = ""; 
    std::map<std::string, std::vector<float>> sorted_data = {}; 
    std::map<std::string, float> label_data = {}; 
    std::vector<float> random_data     = {};
    std::vector<float> random_data_up  = {}; 
    std::vector<float> random_data_down = {}; 

    int bins = 0; 
    float start = 0;
    float end = 0; 
    bool set_end = false; 
    bool set_start = false; 
    float step = 0; 

    bool underflow = false; 
    bool overflow = false;
    bool bin_centering = false;  
    bool logarithmic = false; 
    
}; 

struct io_t
{
    std::string filename = "untitled"; 
    std::string outputdir = "./Plots";
    int dpi = 250; 
}; 

struct figure_t
{
    std::string title = "no-title";
    bool label_data = false; 
    bool overlay = false; 
    bool histogram = false; 
    bool line = false; 
}; 

struct abstract_plot
{
    paint_t  cosmetic; 
    figure_t figure; 
    io_t     file; 
    axis_t   x; 
    axis_t   y; 
    std::map<std::string, axis_t> stacked = {}; 
}; 


class CyPlotting
{
    public:
        CyPlotting(); 
        ~CyPlotting(); 

        paint_t  painter_params;  
        io_t     file_params; 
        figure_t figure_params; 
}; 

#endif 
