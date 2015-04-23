macro(config_valid var)
  execute_process(
    COMMAND ${PROJECT_SOURCE_DIR}/config/valid_config.py
           --config ${PROJECT_BINARY_DIR}/config.dict
           ${ARGN}
    RESULT_VARIABLE config_valid_code)
  if (${config_valid_code} EQUAL 0)
    set(${var} ON)
  else()
    set(${var} OFF)
  endif()
endmacro(config_valid)
