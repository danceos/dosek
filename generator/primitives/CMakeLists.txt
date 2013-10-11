add_test(NAME generator/primitives/IncludeManager
	 COMMAND python ${CMAKE_CURRENT_SOURCE_DIR}/IncludeManager.py)

add_test(NAME generator/primitives/DataObjectManager
	 COMMAND python ${CMAKE_CURRENT_SOURCE_DIR}/DataObjectManager.py)
