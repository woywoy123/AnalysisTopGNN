cmake_minimum_required(VERSION 3.15 FATAL_ERROR)
project(nusol VERSION ${SKBUILD_PROJECT_VERSION} LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED True)

add_subdirectory(nusol-tensor)
add_subdirectory(nusol-floats)

if(CMAKE_CUDA_COMPILER)
    add_subdirectory(nusol-cuda)
endif()
