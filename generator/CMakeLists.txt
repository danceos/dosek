
set(PYTHON_MODULES_TEST
    coder/elements/template
)

foreach(module ${PYTHON_MODULES_TEST})
  add_test(NAME generator/${module}
	  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
	  COMMAND env PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}/../ python3 ${CMAKE_CURRENT_SOURCE_DIR}/${module}.py)
endforeach(module)

SET(DOSEK_GENERATOR_DIR "${CMAKE_CURRENT_SOURCE_DIR}" CACHE INTERNAL "")
SET(DOSEK_GENERATOR "${CMAKE_CURRENT_SOURCE_DIR}/main.py" CACHE INTERNAL "")

