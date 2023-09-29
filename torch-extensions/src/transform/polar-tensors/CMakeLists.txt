add_library(polar-tensors "")
target_sources(polar-tensors PUBLIC  
    ${CMAKE_CURRENT_LIST_DIR}/polar.h
    ${CMAKE_CURRENT_LIST_DIR}/polar.cxx
)

target_link_libraries(polar-tensors PUBLIC ${TORCH_LIBRARIES})
target_include_directories(polar-tensors PUBLIC ${CMAKE_CURRENT_LIST_DIR})
