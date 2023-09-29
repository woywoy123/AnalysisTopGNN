add_library(physics-tensor "")
target_sources(physics-tensor
    PUBLIC 
        ${CMAKE_CURRENT_LIST_DIR}/physics.h
        ${CMAKE_CURRENT_LIST_DIR}/physics.cxx
)

target_link_libraries(physics-tensor PUBLIC ${TORCH_LIBRARIES})
target_include_directories(physics-tensor PUBLIC ${CMAKE_CURRENT_LIST_DIR})

add_library(physics-polar "")
target_sources(physics-polar
    PUBLIC 
        ${CMAKE_CURRENT_LIST_DIR}/polar.h
        ${CMAKE_CURRENT_LIST_DIR}/polar.cxx
)

target_link_libraries(physics-polar PUBLIC ${TORCH_LIBRARIES} transform_ten physics-tensor)
target_include_directories(physics-polar PUBLIC ${CMAKE_CURRENT_LIST_DIR})

add_library(physics-cartesian "")
target_sources(physics-cartesian
    PUBLIC 
        ${CMAKE_CURRENT_LIST_DIR}/cartesian.h
        ${CMAKE_CURRENT_LIST_DIR}/cartesian.cxx
)

target_link_libraries(physics-cartesian PUBLIC ${TORCH_LIBRARIES} transform_ten physics-tensor)
target_include_directories(physics-cartesian PUBLIC ${CMAKE_CURRENT_LIST_DIR})

