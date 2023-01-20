macro(add_python_target tgt)
  foreach(file ${ARGN})
    set(OUT ${CMAKE_CURRENT_BINARY_DIR}/${file}.pyo)
    list(APPEND OUT_FILES ${OUT})
    add_custom_command(OUTPUT ${OUT}
        COMMAND python3 -m py_compile ${file})
  endforeach()

  add_custom_target(${tgt} ALL DEPENDS ${OUT_FILES})
endmacro()

add_python_target(parserTools parserTools.py)