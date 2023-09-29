add_library(cartesian-tensors "")
target_sources(cartesian-tensors PUBLIC  
    ${CMAKE_CURRENT_LIST_DIR}/cartesian.h
    ${CMAKE_CURRENT_LIST_DIR}/cartesian.cxx
)
target_link_libraries(cartesian-tensors PUBLIC ${TORCH_LIBRARIES})
target_include_directories(cartesian-tensors PUBLIC ${CMAKE_CURRENT_LIST_DIR})
