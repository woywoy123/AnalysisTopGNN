add_library(polar-floats "")
target_sources(polar-floats
        PUBLIC 
            ${CMAKE_CURRENT_LIST_DIR}/polar.h
            ${CMAKE_CURRENT_LIST_DIR}/polar.cxx
)
target_include_directories(polar-floats PUBLIC ${CMAKE_CURRENT_LIST_DIR})           
