set(PYTHON_MODULES_TEST
  primitives/IncludeManager
  primitives/DataObjectManager
  SystemDescription
)

foreach(module ${PYTHON_MODULES_TEST})
  get_filename_component(basedir ${CMAKE_CURRENT_SOURCE_DIR}/${module} PATH)
  add_test(NAME generator/${module}
	WORKING_DIRECTORY ${basedir}
	COMMAND python ${CMAKE_CURRENT_SOURCE_DIR}/${module}.py)
endforeach(module)
