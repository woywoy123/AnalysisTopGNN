cmake_minimum_required(VERSION 3.15 FATAL_ERROR)
project(physics VERSION ${SKBUILD_PROJECT_VERSION} LANGUAGES CXX)

add_subdirectory(physics-tensor)

if(CMAKE_CUDA_COMPILER)
    add_subdirectory(physics-cuda)
endif()
