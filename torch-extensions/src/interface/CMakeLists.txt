if(CMAKE_CUDA_COMPILER)
    add_library(pyc_cuda SHARED
        ${CMAKE_CURRENT_LIST_DIR}/pyc_cuda.h
        ${CMAKE_CURRENT_LIST_DIR}/pyc_cuda.cxx
    )
    
    target_link_libraries(pyc_cuda 
        PUBLIC 
            ${TORCH_LIBRARIES} 
            pybind11::module 
            transform_cu 
            physics-cuda
            operators-cuda
            nusol-cuda
            graph-cuda
    )
endif()

add_library(pyc_tensor SHARED
    ${CMAKE_CURRENT_LIST_DIR}/pyc_tensors.h
    ${CMAKE_CURRENT_LIST_DIR}/pyc_tensors.cxx
)

target_link_libraries(pyc_tensor 
    PUBLIC 
        ${TORCH_LIBRARIES} 
        pybind11::module
        physics-cartesian 
        physics-polar
        transform_ten
        operators-tensor 
        nusol-tensor
        graph-tensor
)

add_library(pyc_float SHARED
    ${CMAKE_CURRENT_LIST_DIR}/pyc_floats.h
    ${CMAKE_CURRENT_LIST_DIR}/pyc_floats.cxx
)

target_link_libraries(pyc_float 
    PUBLIC 
        ${TORCH_LIBRARIES} 
        pybind11::module
        transform_fl
        nusol-floats
)
