add_library(graph-tensor "")
target_sources(graph-tensor
    PUBLIC 
        ${CMAKE_CURRENT_LIST_DIR}/graph.h
        ${CMAKE_CURRENT_LIST_DIR}/graph.cxx
)

target_link_libraries(graph-tensor PUBLIC ${TORCH_LIBRARIES} physics-tensor transform_ten)
target_include_directories(graph-tensor PUBLIC ${CMAKE_CURRENT_LIST_DIR})

