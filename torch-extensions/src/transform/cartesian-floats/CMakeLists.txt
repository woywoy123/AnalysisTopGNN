add_library(cartesian-floats "")
target_sources(cartesian-floats
        PUBLIC 
            ${CMAKE_CURRENT_LIST_DIR}/cartesian.h
            ${CMAKE_CURRENT_LIST_DIR}/cartesian.cxx
)
target_include_directories(cartesian-floats PUBLIC ${CMAKE_CURRENT_LIST_DIR})           
