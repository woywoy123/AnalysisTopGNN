add_library(graph-cuda "")
target_sources(graph-cuda
PUBLIC 
    ${CMAKE_CURRENT_LIST_DIR}/graph.h
    ${CMAKE_CURRENT_LIST_DIR}/graph.cu
    ${CMAKE_CURRENT_LIST_DIR}/graph-kernel.cu
)

target_link_libraries(graph-cuda PUBLIC ${TORCH_LIBRARIES} physics-cuda transform_cu)
target_include_directories(graph-cuda PUBLIC ${CMAKE_CURRENT_LIST_DIR})

