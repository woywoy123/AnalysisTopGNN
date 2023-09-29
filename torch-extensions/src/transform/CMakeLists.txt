cmake_minimum_required(VERSION 3.15 FATAL_ERROR)
project(transform VERSION ${SKBUILD_PROJECT_VERSION} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_subdirectory(cartesian-floats)
add_subdirectory(polar-floats)

add_subdirectory(cartesian-tensors)
add_subdirectory(polar-tensors)

add_library(transform_fl  "")
add_library(transform_ten "")

target_link_libraries(transform_fl  PUBLIC ${TORCH_LIBRARIES} cartesian-floats  polar-floats)
target_link_libraries(transform_ten PUBLIC ${TORCH_LIBRARIES} cartesian-tensors polar-tensors)

target_include_directories(transform_fl  PUBLIC ${CMAKE_SOURCE_DIR})
target_include_directories(transform_ten PUBLIC ${CMAKE_SOURCE_DIR})

if(CMAKE_CUDA_COMPILER)
    add_subdirectory(cartesian-cuda)
    add_subdirectory(polar-cuda)
    
    add_library(transform_cu  "")
    target_link_libraries(transform_cu PUBLIC ${TORCH_LIBRARIES} cartesian-cuda polar-cuda)
    target_include_directories(transform_cu PUBLIC ${CMAKE_SOURCE_DIR})
endif()
