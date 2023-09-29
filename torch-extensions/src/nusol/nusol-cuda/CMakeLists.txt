add_library(nusol-cuda "")
target_sources(nusol-cuda 
    PUBLIC 
        ${CMAKE_CURRENT_LIST_DIR}/nusol.h
        ${CMAKE_CURRENT_LIST_DIR}/nusol.cu
        ${CMAKE_CURRENT_LIST_DIR}/kernel.cu
        ${CMAKE_CURRENT_LIST_DIR}/torch.cu 
)

target_link_libraries(nusol-cuda PUBLIC ${TORCH_LIBRARIES} operators-cuda physics-cuda transform_cu)
target_include_directories(nusol-cuda PUBLIC ${CMAKE_CURRENT_LIST_DIR})
