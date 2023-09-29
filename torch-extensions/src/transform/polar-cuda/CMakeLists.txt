add_library(polar-cuda "")
target_sources(polar-cuda
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}/polar.h
        ${CMAKE_CURRENT_LIST_DIR}/polar.cu
        ${CMAKE_CURRENT_LIST_DIR}/kernel.cu
        ${CMAKE_CURRENT_LIST_DIR}/torch.cu
)

target_link_libraries(polar-cuda PUBLIC ${TORCH_LIBRARIES})
target_include_directories(polar-cuda PUBLIC ${CMAKE_CURRENT_LIST_DIR})

