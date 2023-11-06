cmake_minimum_required(VERSION 3.15 FATAL_ERROR)
project(graph VERSION ${SKBUILD_PROJECT_VERSION} LANGUAGES CXX)

add_subdirectory(graph-tensor)

if(CMAKE_CUDA_COMPILER)
    add_subdirectory(graph-cuda)
endif()
