add_library(cartesian-cuda "")
target_sources(cartesian-cuda
    PUBLIC
        ${CMAKE_CURRENT_LIST_DIR}/cartesian.h
        ${CMAKE_CURRENT_LIST_DIR}/cartesian.cu
        ${CMAKE_CURRENT_LIST_DIR}/kernel.cu
        ${CMAKE_CURRENT_LIST_DIR}/torch.cu
)

target_link_libraries(cartesian-cuda PUBLIC ${TORCH_LIBRARIES})
target_include_directories(cartesian-cuda PUBLIC ${CMAKE_CURRENT_LIST_DIR})

