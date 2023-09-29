add_library(operators-cuda "")
target_sources(operators-cuda 
    PUBLIC 
        ${CMAKE_CURRENT_LIST_DIR}/operators.h
        ${CMAKE_CURRENT_LIST_DIR}/operators.cu
        ${CMAKE_CURRENT_LIST_DIR}/kernel.cu
        ${CMAKE_CURRENT_LIST_DIR}/torch.cu
)

target_link_libraries(operators-cuda PUBLIC ${TORCH_LIBRARIES})
target_include_directories(operators-cuda PUBLIC ${CMAKE_CURRENT_LIST_DIR})
