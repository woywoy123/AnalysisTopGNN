.. _data-types:

Data Types and Dictionary Mapping
*********************************

Introduction
____________
Since most of the backend of Analysis-G is built in C++ and interfaced via Cython, multiple data types were used to simplify passing arguments between layers.
Luckily, Cython and C++ can share py:type:struct types, which can be mapped into dictionaries and back.
This section of the documentation outlines these types with their respective key and value pairs.

.. py:data:: code_t

    :ivar list[str] input_params: 
    :ivar list[str] co_vars: 
    :ivar dict[str, str] param_space: 
    :ivar dict[str, list[str]] trace: 
    :ivar dict[str, list[str]] extern_imports: 
    :ivar list[str] dependency_hashes: 
    :ivar str function_name:
    :ivar str class_name:
    :ivar str hash:
    :ivar str source_code:
    :ivar str object_code:
    :ivar str defaults:
    :ivar bool is_class:
    :ivar bool is_function:
    :ivar bool is_callable:
    :ivar bool is_initialized:
    :ivar bool has_param_variable:

.. py:data:: leaf_t

    :ivar str requested:
    :ivar str matched:
    :ivar str branch_name:
    :ivar str tree_name:
    :ivar str path:

.. py:data:: branch_t

    :ivar str requested:
    :ivar str matched:
    :ivar str tree_name:
    :ivar list[leaf_t] leaves:

.. py:data:: tree_t

    :ivar int size:
    :ivar str requested:
    :ivar str matched:
    :ivar list[branch_t] branches:
    :ivar list[leaf_t] leaves:

.. py:data:: meta_t

    :ivar str hash:
    :ivar str original_input:
    :ivar str original_path:
    :ivar str original_name:

    :ivar list[str] req_trees: 
    :ivar list[str] req_branches:
    :ivar list[str] req_leaves:
    :ivar list[str] mis_trees: 
    :ivar list[str] mis_branches: 
    :ivar list[str] mis_leaves:

    :ivar int dsid:
    :ivar str AMITag:
    :ivar str generators:
    :ivar bool isMC:
    :ivar str derivationFormat:

    :ivar dict[int, int] inputrange:
    :ivar dict[int, str] inputfiles:
    :ivar dict[str, str] config:

    :ivar int eventNumber:
    :ivar int event_index:
    :ivar bool found:
    :ivar str DatasetName:
    :ivar float ecmEnergy:
    :ivar float genFiltEff:
    :ivar float completion:
    :ivar float beam_energy:
    :ivar float crossSection:
    :ivar float crossSection_mean:
    :ivar float totalSize:
    :ivar int nFiles:
    :ivar int run_number:
    :ivar int totalEvents:
    :ivar int datasetNumber:
    :ivar str identifier:
    :ivar str prodsysStatus:
    :ivar str dataType:
    :ivar str version:
    :ivar str PDF:
    :ivar str AtlasRelease:
    :ivar str principalPhysicsGroup:
    :ivar str physicsShort:
    :ivar str generatorName:
    :ivar str geometryVersion:
    :ivar str conditionsTag:
    :ivar str generatorTune:
    :ivar str amiStatus:
    :ivar str beamType:
    :ivar str productionStep:
    :ivar str projectName:
    :ivar str statsAlgorithm:
    :ivar str genFilterNames:
    :ivar str file_type:
    :ivar str sample_name:
    :ivar list[str] keywords:
    :ivar list[str] weights:
    :ivar list[str] keyword:
    :ivar dict[str, int] LFN:
    :ivar list[st] fileGUID:
    :ivar list[int] events:
    :ivar list[float] fileSize:


.. py:data:: particle_t

    :ivar float e:
    :ivar float mass:
    :ivar float px:
    :ivar float py:
    :ivar float pz:
    :ivar float pt:
    :ivar float eta:
    :ivar float phi:
    :ivar bool cartesian:
    :ivar bool polar:
    :ivar float charge:
    :ivar int pdgid: 
    :ivar int index:
    :ivar str type:
    :ivar str hash:
    :ivar str symbol:
    :ivar list[int] lepdef:
    :ivar list[int] nudef: 

.. py:data:: event_t

    :ivar str event_name:
    :ivar str commit_hash:
    :ivar str code_hash:
    :ivar bool deprecated: 
    :ivar bool cached:
    :ivar float weight: 
    :ivar int event_index:
    :ivar str event_hash:
    :ivar str event_tagging:
    :ivar str event_tree:
    :ivar str event_root:
    :ivar str pickled_data:
    :ivar bool graph: 
    :ivar bool selection: 
    :ivar bool event: 

.. py:data:: graph_t

    :ivar str event_name:
    :ivar str code_hash:
    :ivar dict[str, str] errors: 
    :ivar dict[str, int] presel:
    :ivar bool cached:
    :ivar int event_index:
    :ivar float weight:
    :ivar str event_hash:
    :ivar str event_tagging:
    :ivar str event_tree:
    :ivar str event_root:
    :ivar str pickled_data:
    :ivar bool train:
    :ivar bool evaluation:
    :ivar bool validation:
    :ivar bool empty_graph: bool
    :ivar bool skip_graph: bool
    :ivar dict[str, list[int]] src_dst:
    :ivar dict[str, int] hash_particle:
    :ivar bool self_loops:
    :ivar dict[str, str] graph_feature: 
    :ivar dict[str, str] node_feature: 
    :ivar dict[str, str] edge_feature:
    :ivar dict[str, str] pre_sel_feature:
    :ivar str topo_hash:
    :ivar bool graph:
    :ivar bool selection: 
    :ivar bool event: 

.. py:data:: selection_t

    :ivar str event_name:
    :ivar str code_hash:
    :ivar dict[str, int] errors:
    :ivar bool cached:
    :ivar int event_index:
    :ivar float weight:
    :ivar str event_hash:
    :ivar str event_tagging:
    :ivar str event_tree:
    :ivar str event_root:
    :ivar str pickled_data:
    :ivar str pickled_strategy_data:
    :ivar dict[str, str] strat_merge:
    :ivar dict[str, str] data_merge:
    :ivar dict[str, int] cutflow:
    :ivar list[float] timestats:
    :ivar list[float] all_weights:
    :ivar list[float] selection_weights:
    :ivar bool allow_failure:
    :ivar str _params_:
    :ivar bool graph:
    :ivar bool selection: 
    :ivar bool event: 

.. py:data:: batch_t

    :ivar dict[str, event_t] events:
    :ivar dict[str, graph_t] graphs:
    :ivar dict[str, selection_t] selections:
    :ivar dict[str, code_t] code_hashes:
    :ivar meta_t meta:
    :ivar str hash:

.. py:data:: folds_t

    :ivar bool test: 
    :ivar bool train:
    :ivar bool evaluation:
    :ivar int kfold:
    :ivar str event_hash:

.. py:data:: data_t

    :ivar str name: str
    :ivar list[list[float]] truth:
    :ivar list[list[float]] pred:
    :ivar list[list[float]] index:
    :ivar list[list[float]] nodes:
    :ivar list[list[float]] loss:
    :ivar list[list[float]] accuracy:
    :ivar map[int, list[list[float]]] mass_truth:
    :ivar map[int, list[list[float]]] mass_pred:

.. py:data:: metric_t
   
    :ivar dict[str, list[list[float]] truth:
    :ivar dict[str, list[list[float]] pred:
    :ivar dict[str, float] acc_average:
    :ivar dict[str, float] loss_average:
    :ivar dict[str, int] num_nodes:


.. py:data:: root_t

    :ivar dict[str, batch_t] batches:
    :ivar dict[str, int] n_events:
    :ivar dict[str, int] n_graphs:
    :ivar dict[str, int] n_selections:

.. py:data:: tracer_t

    :ivar dict[str, root_t] root_names:
    :ivar dict[str, meta_t] root_meta:
    :ivar dict[str, code_t] hashed_code:
    :ivar dict[str, int ] event_trees:
    :ivar dict[str, str] link_event_code:
    :ivar dict[str, str] link_graph_code:

.. py:data:: export_t

    :ivar dict[str, meta_t] root_meta: dict[str, meta_t]
    :ivar dict[str, code_t] hashed_code: dict[str, code_t]
    :ivar dict[str, str] link_event_code: dict[str, str]
    :ivar dict[str, str] link_graph_code: dict[str, str]
    :ivar dict[str, str] link_selection_code: dict[str, str]
    :ivar dict[str, list[str]] event_name_hash: 
    :ivar dict[str, list[str]] graph_name_hash:
    :ivar dict[str, list[str]] selection_name_hash:
    :ivar dict[str, str] event_dir: 
    :ivar dict[str, str] graph_dir: 
    :ivar dict[str, str] selection_dir: 

.. py:data:: settings_t

    :ivar str projectname:
    :ivar str outputdirectory:
    :ivar dict[str, list[str]] files:
    :ivar dict[str, list[str]] samplemap:
    :ivar int verbose:
    :ivar int chunks:
    :ivar int threads:
    :ivar bool enable_pyami:
    :ivar str tree:
    :ivar str eventname:
    :ivar str graphname:
    :ivar str selectionname:
    :ivar int event_start:
    :ivar int event_stop:
    :ivar str training_name:
    :ivar str run_name:
    :ivar str device:
    :ivar str optimizer_name:
    :ivar dict[str, str] optimizer_params:
    :ivar str scheduler_name:
    :ivar dict[str, str] scheduler_params:
    :ivar int kfolds:
    :ivar int batch_size: 
    :ivar int epochs: 
    :ivar dict[int, int] epoch:
    :ivar list[int] kfold:
    :ivar code_t model:
    :ivar dict[str, str] model_params:
    :ivar dict[str, str] kinematic_map: 
    :ivar bool debug_mode:
    :ivar bool continue_training:
    :ivar bool runplotting:
    :ivar bool sort_by_nodes:
    :ivar bool enable_reconstruction:
    :ivar dict[str, str] kinematic_map:
    :ivar bool getgraph:
    :ivar bool getevent:
    :ivar bool getselection:
    :ivar bool eventcache: 
    :ivar bool graphcache: 
    :ivar list[str] search: 
    :ivar bool get_all: 
    :ivar dict[str, code_t] hashed_code:
    :ivar dict[str, str] link_event_code:
    :ivar dict[str, str] link_graph_code:
    :ivar dict[str, str] link_selection_code:
