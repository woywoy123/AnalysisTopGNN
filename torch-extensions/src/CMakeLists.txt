cmake_minimum_required(VERSION 3.15 FATAL_ERROR)
project(${SKBUILD_PROJECT_NAME} VERSION ${SKBUILD_PROJECT_VERSION} LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED True)
include(CheckLanguage)
check_language(CUDA)

if(CMAKE_CUDA_COMPILER)
    enable_language(CUDA)
    message(STATUS "INSTALLING EXTENSIONS WITH CUDA!")
    string(REGEX REPLACE ".[0-9][0-9]|\\." "" CUDA_V ${CMAKE_CUDA_COMPILER_VERSION})
    message(STATUS "CMAKE_CUDA_COMPILER = ${CMAKE_CUDA_COMPILER}")
    message(STATUS "CMAKE_CUDA_COMPILER_ID = ${CMAKE_CUDA_COMPILER_ID}")
    message(STATUS "CMAKE_CUDA_COMPILER_VERSION = ${CUDA_V}")
    set(CMAKE_CUDA_STANDARD 14)
    set(CMAKE_CUDA_STANDARD_REQUIRED ON)
else()
    message(STATUS "NO CUDA INSTALLATION FOUND, INSTALLING CPU VERSION ONLY!")
    execute_process(COMMAND ${Python_EXECUTABLE} -m pip uninstall torch)
    execute_process(COMMAND ${Python_EXECUTABLE} -m pip install -v torch --extra-index-url https://download.pytorch.org/whl/cpu)
endif()

#find_package(Python REQUIRED COMPONENTS Development)
find_package(pybind11 REQUIRED)
find_package(Torch REQUIRED)

add_subdirectory(transform)
add_subdirectory(physics)
add_subdirectory(operators)
add_subdirectory(nusol)
add_subdirectory(graph)
add_subdirectory(interface)

if(CMAKE_CUDA_COMPILER)
    install(TARGETS pyc_cuda DESTINATION ${SKBUILD_PROJECT_NAME})
endif()

install(TARGETS pyc_tensor DESTINATION ${SKBUILD_PROJECT_NAME})
install(TARGETS pyc_float  DESTINATION ${SKBUILD_PROJECT_NAME})

# Configure the Python package directory 
install(DIRECTORY DESTINATION ${SKBUILD_PROJECT_NAME}/Transform)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/__init__.py            DESTINATION ${SKBUILD_PROJECT_NAME})
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Transform/__init__.py  DESTINATION ${SKBUILD_PROJECT_NAME}/Transform)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Transform/transform.py DESTINATION ${SKBUILD_PROJECT_NAME}/Transform)

install(DIRECTORY DESTINATION ${SKBUILD_PROJECT_NAME}/Physics)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Physics/__init__.py            DESTINATION ${SKBUILD_PROJECT_NAME}/Physics)

install(DIRECTORY DESTINATION ${SKBUILD_PROJECT_NAME}/Physics/Polar)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Physics/Polar/__init__.py      DESTINATION ${SKBUILD_PROJECT_NAME}/Physics/Polar)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Physics/Polar/polar.py         DESTINATION ${SKBUILD_PROJECT_NAME}/Physics/Polar)

install(DIRECTORY DESTINATION ${SKBUILD_PROJECT_NAME}/Physics/Cartesian)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Physics/Cartesian/__init__.py  DESTINATION ${SKBUILD_PROJECT_NAME}/Physics/Cartesian)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Physics/Cartesian/cartesian.py DESTINATION ${SKBUILD_PROJECT_NAME}/Physics/Cartesian)

install(DIRECTORY DESTINATION ${SKBUILD_PROJECT_NAME}/Operators)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Operators/__init__.py  DESTINATION ${SKBUILD_PROJECT_NAME}/Operators)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Operators/operators.py DESTINATION ${SKBUILD_PROJECT_NAME}/Operators)

install(DIRECTORY DESTINATION ${SKBUILD_PROJECT_NAME}/NuSol)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/NuSol/__init__.py DESTINATION ${SKBUILD_PROJECT_NAME}/NuSol)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/NuSol/nusol.py    DESTINATION ${SKBUILD_PROJECT_NAME}/NuSol)

install(DIRECTORY DESTINATION ${SKBUILD_PROJECT_NAME}/NuSol/Polar)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/NuSol/Polar/__init__.py DESTINATION ${SKBUILD_PROJECT_NAME}/NuSol/Polar)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/NuSol/Polar/polar.py    DESTINATION ${SKBUILD_PROJECT_NAME}/NuSol/Polar)

install(DIRECTORY DESTINATION ${SKBUILD_PROJECT_NAME}/NuSol/Cartesian)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/NuSol/Cartesian/__init__.py  DESTINATION ${SKBUILD_PROJECT_NAME}/NuSol/Cartesian)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/NuSol/Cartesian/cartesian.py DESTINATION ${SKBUILD_PROJECT_NAME}/NuSol/Cartesian)

install(DIRECTORY DESTINATION ${SKBUILD_PROJECT_NAME}/Graph)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Graph/__init__.py DESTINATION ${SKBUILD_PROJECT_NAME}/Graph)

install(DIRECTORY DESTINATION ${SKBUILD_PROJECT_NAME}/Graph/Base)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Graph/Base/__init__.py DESTINATION ${SKBUILD_PROJECT_NAME}/Graph/Base)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Graph/Base/base.py DESTINATION ${SKBUILD_PROJECT_NAME}/Graph/Base)

install(DIRECTORY DESTINATION ${SKBUILD_PROJECT_NAME}/Graph/Polar)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Graph/Polar/__init__.py DESTINATION ${SKBUILD_PROJECT_NAME}/Graph/Polar)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Graph/Polar/polar.py DESTINATION ${SKBUILD_PROJECT_NAME}/Graph/Polar)

install(DIRECTORY DESTINATION ${SKBUILD_PROJECT_NAME}/Graph/Cartesian)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Graph/Cartesian/__init__.py DESTINATION ${SKBUILD_PROJECT_NAME}/Graph/Cartesian)
install(FILES ${CMAKE_SOURCE_DIR}/py_interface/Graph/Cartesian/cartesian.py DESTINATION ${SKBUILD_PROJECT_NAME}/Graph/Cartesian)