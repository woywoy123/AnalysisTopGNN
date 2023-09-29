add_library(operators-tensor "")
target_sources(operators-tensor 
    PUBLIC 
        ${CMAKE_CURRENT_LIST_DIR}/operators.h
        ${CMAKE_CURRENT_LIST_DIR}/operators.cxx
)

target_link_libraries(operators-tensor PUBLIC ${TORCH_LIBRARIES})
target_include_directories(operators-tensor PUBLIC ${CMAKE_CURRENT_LIST_DIR})
