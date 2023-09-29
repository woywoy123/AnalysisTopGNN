add_library(nusol-tensor "")
target_sources(nusol-tensor
    PUBLIC 
        ${CMAKE_CURRENT_LIST_DIR}/nusol.h
        ${CMAKE_CURRENT_LIST_DIR}/nusol_tools.h
        ${CMAKE_CURRENT_LIST_DIR}/nusol.cxx
        ${CMAKE_CURRENT_LIST_DIR}/nusol_tools.cxx
)

target_link_libraries(nusol-tensor PUBLIC ${TORCH_LIBRARIES} operators-tensor physics-tensor transform_ten)
target_include_directories(nusol-tensor PUBLIC ${CMAKE_CURRENT_LIST_DIR})

