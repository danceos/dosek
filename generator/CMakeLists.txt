set(PYTHON_MODULES_TEST
  primitives/IncludeManager
  primitives/DataObjectManager
  primitives/FunctionManager
  SystemDescription
  RTSCAnalysis
)

foreach(module ${PYTHON_MODULES_TEST})
  add_test(NAME generator/${module}
	  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
	  COMMAND env PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}/../ python ${CMAKE_CURRENT_SOURCE_DIR}/${module}.py)
endforeach(module)

SET(COREDOS_GENERATOR_DIR "${CMAKE_CURRENT_SOURCE_DIR}" CACHE INTERNAL "")
SET(COREDOS_GENERATOR "${CMAKE_CURRENT_SOURCE_DIR}/main.py" CACHE INTERNAL "")

