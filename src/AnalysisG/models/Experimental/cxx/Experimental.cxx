#include <Experimental.h>
#include <transform/cartesian-cuda.h>
#include <physics/cartesian-cuda.h>
#include <transform/polar-cuda.h>
#include <graph/graph-cuda.h>


experimental::experimental(){
    this -> rnn_x = new torch::nn::Sequential({
            {"rnn_x_l1", torch::nn::Linear(this -> _xin*2, this -> _hidden)},
            {"rnn_x_n1", torch::nn::LayerNorm(torch::nn::LayerNormOptions({this -> _hidden}))}, 
            {"rnn_x_l2", torch::nn::Linear(this -> _hidden, this -> _xin)}, 
            {"rnn_x_t1", torch::nn::Tanh()},
            {"rnn_x_l3", torch::nn::Linear(this -> _xin, this -> _xin)}
    }); 

    int dxx = this -> _dxin*2 + this -> _xin*2; 
    this -> rnn_dx = new torch::nn::Sequential({
            {"rnn_dx_l1", torch::nn::Linear(dxx, dxx)}, 
            {"rnn_dx_s1", torch::nn::Tanh()},
            {"rnn_dx_l2", torch::nn::Linear(dxx, this -> _xin)},
            {"rnn_dx_n2", torch::nn::LayerNorm(torch::nn::LayerNormOptions({this -> _xin}))}, 
            {"rnn_dx_l3", torch::nn::Linear(this -> _xin, this -> _xin)}
    }); 

    this -> rnn_merge = new torch::nn::Sequential({
            {"rnn_mrg_l1", torch::nn::Linear(this -> _xin*2, this -> _hidden)}, 
            {"rnn_mrg_s1", torch::nn::Sigmoid()},
            {"rnn_mrg_l2", torch::nn::Linear(this -> _hidden, this -> _hidden)},
            {"rnn_mrg_r2", torch::nn::ELU()},
            {"rnn_mrg_l3", torch::nn::Linear(this -> _hidden, this -> _hidden)}
    }); 

    dxx = this -> _xin + this -> _xout*2 + this -> _hidden; 
    this -> rnn_top_edge = new torch::nn::Sequential({
            {"rnn_top_l1", torch::nn::Linear(dxx, dxx)}, 
            {"rnn_top_r1", torch::nn::ELU()},
            {"rnn_top_t1", torch::nn::Tanh()},
            {"rnn_top_l2", torch::nn::Linear(dxx, this -> _xout)}, 
            {"rnn_top_s2", torch::nn::Sigmoid()},
            {"rnn_top_l3", torch::nn::Linear(this -> _xout, this -> _xout)},
            {"rnn_top_drp", torch::nn::Dropout(torch::nn::DropoutOptions({this -> drop_out}))}
    }); 

    this -> rnn_res_edge = new torch::nn::Sequential({
            {"rnn_res_l1", torch::nn::Linear(this -> _xin*3, dxx)}, 
            {"rnn_res_r1", torch::nn::ELU()},
            {"rnn_res_t1", torch::nn::Tanh()},
            {"rnn_res_l2", torch::nn::Linear(dxx, this -> _xout)}, 
            {"rnn_res_s2", torch::nn::Sigmoid()},
            {"rnn_res_l3", torch::nn::Linear(this -> _xout, this -> _xout)},
            {"rnn_res_drp", torch::nn::Dropout(torch::nn::DropoutOptions({this -> drop_out}))}
    }); 

    this -> mlp_ntop = new torch::nn::Sequential({
            {"ntop_l1", torch::nn::Linear(2*this -> _xin+1, this -> _hidden)}, 
            {"ntop_t2", torch::nn::Tanh()},
            {"ntop_r1", torch::nn::ReLU()},
            {"ntop_l2", torch::nn::Linear(this -> _hidden, this -> _xin*2)}, 
            {"ntop_n2", torch::nn::LayerNorm(torch::nn::LayerNormOptions({this -> _xin*2}))}, 
            {"ntop_l3", torch::nn::Linear(this -> _xin*2, 5)},
            {"ntop_drp", torch::nn::Dropout(torch::nn::DropoutOptions({this -> drop_out}))}
    }); 

    this -> mlp_sig = new torch::nn::Sequential({
            {"res_l1", torch::nn::Linear(this -> _xin*3, this -> _hidden)}, 
            {"res_t1", torch::nn::Tanh()},
            {"res_r1", torch::nn::ReLU()},
            {"res_l2", torch::nn::Linear(this -> _hidden, this -> _xin*3)}, 
            {"res_n2", torch::nn::LayerNorm(torch::nn::LayerNormOptions({this -> _xin*3}))}, 
            {"res_l3", torch::nn::Linear(this -> _xin*3, this -> _xout)},
            {"res_drp", torch::nn::Dropout(torch::nn::DropoutOptions({this -> drop_out}))}
    }); 

    this -> register_module(this -> rnn_x       );
    this -> register_module(this -> rnn_dx      );
    this -> register_module(this -> rnn_merge   );
    this -> register_module(this -> rnn_top_edge);
    this -> register_module(this -> rnn_res_edge);
    this -> register_module(this -> mlp_ntop    );
    this -> register_module(this -> mlp_sig     );
}

torch::Tensor experimental::message(
        torch::Tensor _trk_i, torch::Tensor _trk_j, torch::Tensor pmc, torch::Tensor hx_i, torch::Tensor hx_j
){
    torch::Tensor trk_ij = torch::cat({_trk_i, _trk_j}, {-1}); 

    std::tuple<torch::Tensor, torch::Tensor> aggr = graph::cuda::unique_aggregation(trk_ij, pmc); 
    torch::Tensor pmc_ij = std::get<0>(aggr); 
    torch::Tensor nds_ij = (std::get<1>(aggr) > -1).sum({-1}).view({-1, 1}); 
    torch::Tensor m_ij   = physics::cuda::cartesian::M(pmc_ij);
    torch::Tensor fx_ij  = torch::cat({m_ij, pmc_ij, nds_ij}, {-1}).to(torch::kFloat32); 
    fx_ij = (*this -> rnn_x) -> forward(torch::cat({fx_ij, hx_i}, {-1})) + fx_ij; 

    torch::Tensor fx_i  = std::get<0>(graph::cuda::unique_aggregation(_trk_i, pmc)); 
    fx_i = torch::cat({physics::cuda::cartesian::M(fx_i), fx_i}, {-1}).to(torch::kFloat32); 

    torch::Tensor fx_j  = std::get<0>(graph::cuda::unique_aggregation(_trk_j, pmc)); 
    fx_j = torch::cat({physics::cuda::cartesian::M(fx_j), fx_j}, {-1}).to(torch::kFloat32); 

    torch::Tensor dx = (*this -> rnn_dx) -> forward(torch::cat({fx_i, fx_j - fx_i, hx_i, hx_j - hx_i}, {-1})); 
    return (*this -> rnn_merge) -> forward(torch::cat({fx_ij, dx}, {-1})); 
}

void experimental::forward(graph_t* data){

    // get the particle 4-vector and convert it to cartesian
    torch::Tensor* pt     = data -> get_data_node("pt", this);
    torch::Tensor* eta    = data -> get_data_node("eta", this);
    torch::Tensor* phi    = data -> get_data_node("phi", this);
    torch::Tensor* energy = data -> get_data_node("energy", this);
    torch::Tensor* is_lep = data -> get_data_node("is_lep", this); 
    torch::Tensor pmc    = transform::cuda::PxPyPzE(*pt, *eta, *phi, *energy) / 1000.0; 

    torch::Tensor edge_index = data -> get_edge_index(this) -> to(torch::kLong); 
    torch::Tensor src        = edge_index.index({0}).view({-1}); 
    torch::Tensor dst        = edge_index.index({1}).view({-1}); 

    // the event features
    torch::Tensor* num_jets = data -> get_data_graph("num_jets", this); 
    torch::Tensor* num_leps = data -> get_data_graph("num_leps", this); 
    torch::Tensor* met_phi  = data -> get_data_graph("phi", this);
    torch::Tensor* met      = data -> get_data_graph("met", this); 

    torch::Tensor num_bjet = data -> get_data_node("is_b", this) -> sum({0}).view({-1, 1});  
    torch::Tensor pid      = torch::cat({*num_jets, num_bjet, *num_leps, (*met)/1000.0, *met_phi}, {-1});  

    // ------ index the nodes from 0 to N-1 ----- //
    torch::Tensor trk = (torch::ones_like(*pt).cumsum({0}) - 1).to(torch::kInt); 
    torch::Tensor nds = torch::ones_like(*pt).to(torch::kInt); 

    // ------ index the edges from 0 to N^2 -1 ------ //
    torch::Tensor idx_mlp = torch::ones_like(src).cumsum({-1})-1; 
    torch::Tensor idx_mat = torch::zeros({trk.size({0}), trk.size({0})}, src.device()).to(torch::kLong); 
    idx_mat.index_put_({src, dst}, idx_mlp.to(torch::kLong)); 

    // ------ initialize nulls -------- //
    std::vector<torch::Tensor> gr_ = {}; 
    torch::Tensor hx = torch::zeros_like(torch::cat({trk, trk, trk, trk, trk, trk}, {-1}).view({-1, 6})); 
    torch::Tensor fx  = torch::cat({physics::cuda::cartesian::M(pmc), pmc, nds}, {-1}).to(torch::kFloat32); 
    hx = (*this -> rnn_x) -> forward(torch::cat({fx, hx}, {-1})) + fx; 

    int dxx = this -> _xin + this -> _xout*2 + this -> _hidden; 
    for (size_t x(0); x < dxx; ++x){gr_.push_back(torch::zeros_like(src.view({-1, 1})));}
    torch::Tensor top_edge  = (*this -> rnn_top_edge) -> forward(torch::cat(gr_, {-1}).to(torch::kFloat32));
    torch::Tensor top_edge_ = torch::zeros_like(top_edge); 
    torch::Tensor edge_index_ = edge_index.clone();  
    while (edge_index_.size({1})){

        torch::Tensor src_ = edge_index_.index({0}); 
        torch::Tensor dst_ = edge_index_.index({1});

        // ----- use the index matrix to map the source and destination edges to the edge index ----- //
        torch::Tensor idx = idx_mat.index({src_, dst_}); 

        // ----------- create a new intermediate state of the nodes ----------- //
        gr_ = graph::cuda::edge_aggregation(edge_index, top_edge, pmc)["1"]; 
        trk = gr_[0].index({gr_[2]});

        nds = (trk > -1).sum({-1}).view({-1, 1}); 
        fx  = torch::cat({physics::cuda::cartesian::M(gr_[3]), gr_[3], nds}, {-1}).to(torch::kFloat32); 
        hx  = (*this -> rnn_x) -> forward(torch::cat({fx, hx}, {-1})) + fx;

        // ------------------ check edges for new paths ---------------- //
        torch::Tensor hx_ij_ = this -> message(trk.index({src_}), trk.index({dst_}), pmc, hx.index({src_}), hx.index({dst_}));
        torch::Tensor hx_px_ = torch::cat({hx.index({src_}), hx_ij_, top_edge_, top_edge.index({idx}) - top_edge_}, {-1}); 
        top_edge_ = (*this -> rnn_top_edge) -> forward(hx_px_); 

        // ----- update the top_edge prediction weights by index ------- //
        torch::Tensor sel = std::get<1>((top_edge_).max({-1})); 
        top_edge.index_put_({idx}, top_edge_); 

        // ---- check if the new prediction is simply null ---- /
        sel = sel < 1; 
        if (!sel.index({sel == false}).size({0})){break;}
        edge_index_ = edge_index_.index({torch::indexing::Slice(), sel}); 
        top_edge_   = top_edge_.index({sel}); 
    }

    // ----------- compress the top data ----------- //
    torch::Tensor trk_ = torch::zeros_like(*pt).to(torch::kInt).view({-1}); 
    gr_ = graph::cuda::edge_aggregation(edge_index, top_edge, pmc)["1"]; 
    trk = (gr_[0].index({gr_[2]}) > -1).sum({-1}, true);
    trk = torch::cat({trk, hx, physics::cuda::cartesian::M(gr_[3]), pid.index({trk_})}, {-1}); 
    torch::Tensor ntops_ = (*this -> mlp_ntop) -> forward(trk.to(torch::kFloat32)); 

    torch::Tensor r_trk  = torch::cat({gr_[0].index({gr_[2]}).index({src}), gr_[0].index({gr_[2]}).index({dst})}, {-1}); 
    std::tuple<torch::Tensor, torch::Tensor> aggr = graph::cuda::unique_aggregation(r_trk, pmc); 
    torch::Tensor pmc_ij = std::get<0>(aggr); 
    torch::Tensor nds_ij = (std::get<1>(aggr) > -1).sum({-1}).view({-1, 1}); 
    torch::Tensor m_ij   = physics::cuda::cartesian::M(pmc_ij);
    torch::Tensor fx_ij  = torch::cat({m_ij, pmc_ij, nds_ij, hx.index({src}), hx.index({dst}) - hx.index({src})}, {-1}); 
    torch::Tensor res_edge = (*this -> rnn_res_edge) -> forward(fx_ij.to(torch::kFloat32));

    gr_ = graph::cuda::edge_aggregation(edge_index, res_edge, pmc)["1"]; 
    trk = (gr_[0].index({gr_[2]}) > -1).sum({-1}, true);
    trk = torch::cat({trk, hx, physics::cuda::cartesian::M(gr_[3]), pid.index({trk_}), ntops_}, {-1}); 
    torch::Tensor isres_ = (*this -> mlp_sig) -> forward(trk.to(torch::kFloat32));

    ntops_ = ntops_.sum({0}, true) / ntops_.size({0}); 
    isres_ = isres_.sum({0}, true) / isres_.size({0}); 
 
    this -> prediction_edge_feature("top_edge", top_edge); 
    this -> prediction_edge_feature("res_edge", res_edge); 
    this -> prediction_graph_feature("ntops", ntops_);
    this -> prediction_graph_feature("signal", isres_); 
    if (!this -> inference_mode){return;}

    this -> prediction_extra("top_edge_score", top_edge.softmax(-1));
    this -> prediction_extra("res_edge_score", res_edge.softmax(-1));
    this -> prediction_extra("ntops_score"   , ntops_.softmax(-1).view({-1})); 
    this -> prediction_extra("is_res_score"  , isres_.softmax(-1).view({-1})); 

    this -> prediction_extra("is_lep"        , is_lep -> view({-1})); 
    this -> prediction_extra("num_leps"      , num_leps -> view({-1})); 
    this -> prediction_extra("num_jets"      , num_jets -> view({-1})); 
    this -> prediction_extra("num_bjets"     , num_bjet.view({-1})); 
    if (!this -> is_mc){return;}

    torch::Tensor ntops_t  = data -> get_truth_graph("ntops"  , this) -> view({-1}); 
    torch::Tensor signa_t  = data -> get_truth_graph("signal" , this) -> view({-1});
    torch::Tensor r_edge_t = data -> get_truth_edge("res_edge", this) -> view({-1}); 
    torch::Tensor t_edge_t = data -> get_truth_edge("top_edge", this) -> view({-1}); 

    this -> prediction_extra("truth_ntops"   , ntops_t); 
    this -> prediction_extra("truth_signal"  , signa_t); 
    this -> prediction_extra("truth_res_edge", r_edge_t); 
    this -> prediction_extra("truth_top_edge", t_edge_t); 
}

experimental::~experimental(){}
model_template* experimental::clone(){
    experimental* md = new experimental(); 
    md -> drop_out = this -> drop_out; 
    md -> is_mc    = this -> is_mc; 
    return md; 
}
