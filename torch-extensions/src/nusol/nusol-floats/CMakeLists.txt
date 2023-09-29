add_library(nusol-floats "")
target_sources(nusol-floats
    PUBLIC 
        ${CMAKE_CURRENT_LIST_DIR}/nusol.h
        ${CMAKE_CURRENT_LIST_DIR}/nusol_tools.h
        ${CMAKE_CURRENT_LIST_DIR}/nusol.cxx
        ${CMAKE_CURRENT_LIST_DIR}/nusol_tools.cxx
)

target_link_libraries(nusol-floats PUBLIC ${TORCH_LIBRARIES} operators-tensor physics-tensor transform_ten nusol-tensor)
target_include_directories(nusol-floats PUBLIC ${CMAKE_CURRENT_LIST_DIR})

