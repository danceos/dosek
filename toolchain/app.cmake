include(CMakeParseArguments)

MACRO(DOSEK_BINARY_EXECUTABLE NAME SOURCES SYSTEM_DESC VERIFY_SCRIPT DEFINITIONS LIBS SPECIFIC_GENERATOR_ARGS)
  SET(DOSEK_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/${NAME}")
  file(MAKE_DIRECTORY "${DOSEK_OUTPUT_DIR}")

  set(DOSEK_SOURCE_SYSTEM "${DOSEK_OUTPUT_DIR}/source_system.ll")
  set(DOSEK_GENERATED_SOURCE "${DOSEK_OUTPUT_DIR}/dosek.cc")
  set(DOSEK_GENERATED_LINKER "${DOSEK_OUTPUT_DIR}/linker.ld")

  set(DOSEK_BINARY_LLVM_BYTECODE "")

  set(DEFINITON_FLAGS ";")
  foreach(DEF ${DEFINITIONS})
    set(DEFINITON_FLAGS ${DEFINITON_FLAGS} -D${DEF})
  endforeach()
  if(DEPENDABILITY_FAILURE_LOGGING)
    set(DEFINITON_FLAGS ${DEFINITON_FLAGS} -DDEPENDABILITY_FAILURE_LOGGING)
  endif()

  # Fix whitespace escaping in CXX FLAGS
  string(REPLACE " " ";" COMPILER_FLAGS ${CMAKE_CXX_FLAGS})

  SET(DOSEK_GENERATOR_ARGS "")

  # Get the definitions to forward the ADD_DEFINITIONS to the
  # application (e.g., -DENCODED)
  get_directory_property(definitions DEFINITIONS)
  separate_arguments(definitions)

  # Fix whitespace escaping in CXX FLAGS
  string(REPLACE " " ";" COMPILER_FLAGS ${CMAKE_CXX_FLAGS})

  # First we have to compile all source files with clang
  foreach(src ${SOURCES})
    set(llvm_bytecode "${DOSEK_OUTPUT_DIR}/${src}.ll")
    GET_FILENAME_COMPONENT(dirname ${llvm_bytecode} DIRECTORY)
    file(MAKE_DIRECTORY ${dirname})
    add_custom_command(OUTPUT ${llvm_bytecode}
        COMMAND ${CMAKE_C_COMPILER}
        ARGS ${COMPILER_FLAGS} 
        ARGS ${definitions}
        ARGS  -S -emit-llvm -O0 -m32 -std=c++11 ${ISA_CXX_FLAGS} ${DEFINITON_FLAGS} 
        ARGS ${INCLUDEDIRS_FLAGS} ${CMAKE_CURRENT_SOURCE_DIR}/${src} -o ${llvm_bytecode}
      MAIN_DEPENDENCY ${src}
      DEPENDS ${src}
      IMPLICIT_DEPENDS CXX ${CMAKE_CURRENT_SOURCE_DIR}/${src}
      COMMENT "[${PROJECT_NAME}/${NAME}] Compiling application ${NAME}/${src} with clang")

    list(APPEND DOSEK_BINARY_LLVM_BYTECODE ${llvm_bytecode})
    SET(DOSEK_GENERATOR_ARGS ${DOSEK_GENERATOR_ARGS} --source-bytecode ${llvm_bytecode})
  endforeach(src)

  SET(DOSEK_GENERATOR_ARGS ${DOSEK_GENERATOR_ARGS} ${GENERATOR_ARGS} ${SPECIFIC_GENERATOR_ARGS})
  separate_arguments(DOSEK_GENERATOR_ARGS)

    # All python source files are a dependency
  file(GLOB_RECURSE PYTHON_SOURCE "${DOSEK_GENERATOR_DIR}/*.py")
  file(GLOB_RECURSE OS_TEMPLATES "${PROJECT_SOURCE_DIR}/os/*.in")
  if(EXISTS "${VERIFY_SCRIPT}")
    if (IS_DIRECTORY "${VERIFY_SCRIPT}")
      SET(VERIFY_SCRIPT "")
    else()
      SET(DOSEK_GENERATOR_ARGS ${DOSEK_GENERATOR_ARGS} --verify ${VERIFY_SCRIPT})
    endif()
  else()
    SET(VERIFY_SCRIPT "")
  endif()

  # Check system description file
  file(GLOB XMLDESCS "${CMAKE_CURRENT_SOURCE_DIR}/*.xml")
  file(GLOB OILDESCS "${CMAKE_CURRENT_SOURCE_DIR}/*.oil")
  set(SYSDESCS ${XMLDESCS} ${OILDESCS})

  # Generating DOSEK System
  add_custom_command(OUTPUT "${DOSEK_GENERATED_SOURCE}"  "${DOSEK_GENERATED_LINKER}" "${DOSEK_SOURCE_SYSTEM}"
  DEPENDS ${PYTHON_SOURCE} "${SYSTEM_DESC}" ${DOSEK_BINARY_LLVM_BYTECODE} ${SYSDESCS}
             ${VERIFY_SCRIPT} ${OS_TEMPLATES} ${LINKER_TEMPLATE}
    COMMAND ${CMAKE_COMMAND} -E remove -f ${DOSEK_OUTPUT_DIR}/gen_*.dot
    COMMAND ${DOSEK_GENERATOR}
       --config "${PROJECT_BINARY_DIR}/config.dict"
       --system-desc "${SYSTEM_DESC}"
       --merged-bytecode "${DOSEK_SOURCE_SYSTEM}"
       --prefix ${DOSEK_OUTPUT_DIR}
       --name ${NAME}
       --template-base ${PROJECT_SOURCE_DIR}
       ${DOSEK_GENERATOR_ARGS}
     COMMAND
        if [ x"$$EDIT" != x"" ]; then vim ${DOSEK_GENERATED_SOURCE}\; fi
  COMMENT "[${PROJECT_NAME}/${NAME}] Generating DOSEK source code"
  )

  add_custom_target(${NAME}-generate DEPENDS "${DOSEK_GENERATED_SOURCE}")

  add_custom_target(${NAME}-clean
    COMMAND ${CMAKE_COMMAND} -E remove -f ${DOSEK_OUTPUT_DIR}/* ${DOSEK_BINARY_LLVM_BYTECODE}
  )

  set(APPTARGETS ${APPTARGETS} ${NAME} CACHE INTERNAL "application targets")
  # Since DOSEK_SOURCE_SYSTEM end in .ll the add_executable would
  # simply *silently* ignore the "object" file, by declaring it
  # external it is passed on to the linker
  SET_SOURCE_FILES_PROPERTIES(
    ${DOSEK_SOURCE_SYSTEM}
    PROPERTIES
    EXTERNAL_OBJECT true # to say that "this is actually an object file, so it should not be compiled, only linked"
    GENERATED true       # to say that "it is OK that the obj-files do not exist before build time"
  )

  # Compile the dosek system
  dosek_executable(${NAME} EXCLUDE_FROM_ALL
    SOURCES ${DOSEK_SOURCE_SYSTEM} ${DOSEK_GENERATED_SOURCE}
    LIBS ${DOSEK_BINARY_LIBS}
    DEFINITIONS ${DEFINITIONS}
    LINKER_SCRIPT ${DOSEK_GENERATED_LINKER}
    )

ENDMACRO()

MACRO(DOSEK_BINARY)
  set(options TEST_ISO FAIL)
  set(oneValueArgs SYSTEM_DESC NAME VERIFY)
  set(multiValuedParameters SOURCES LIBS GENERATOR_ARGS)
  cmake_parse_arguments(DOSEK_BINARY "${options}" "${oneValueArgs}" "${multiValuedParameters}" ${ARGN} )
  set(DOSEK_BINARY_SOURCES "${DOSEK_BINARY_UNPARSED_ARGUMENTS};${DOSEK_BINARY_SOURCES}")
  SET(DOSEK_SYSTEM_DESC "${CMAKE_CURRENT_SOURCE_DIR}/${DOSEK_BINARY_SYSTEM_DESC}")
  set(DOSEK_VERIFY_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/${DOSEK_BINARY_VERIFY}")
  SET(NAME "${DOSEK_BINARY_NAME}")

  DOSEK_BINARY_EXECUTABLE(${NAME} "${DOSEK_BINARY_SOURCES}" ${DOSEK_SYSTEM_DESC} ${DOSEK_VERIFY_SCRIPT} 
    "" "${DOSEK_BINARY_LIBS}" "${DOSEK_BINARY_GENERATOR_ARGS}")
  add_custom_command(TARGET ${NAME} POST_BUILD
    COMMENT "Gathering binary statistics for ${NAME}"
    COMMAND ${DOSEK_GENERATOR_DIR}/stats_binary.py
         --stats-dict ${DOSEK_OUTPUT_DIR}/stats.dict.py
         --elf ${PROJECT_BINARY_DIR}/${NAME}
         --nm  ${CROSS_NM}
    )

  if((${DOSEK_BINARY_FAIL} STREQUAL "TRUE") OR FAIL_TRACE_ALL)
    DOSEK_BINARY_EXECUTABLE(fail-${NAME} "${DOSEK_BINARY_SOURCES}" ${DOSEK_SYSTEM_DESC} ${DOSEK_VERIFY_SCRIPT} 
      "FAIL=1" "${DOSEK_BINARY_LIBS}" "${DOSEK_BINARY_GENERATOR_ARGS}")

    fail_test(${NAME} fail-${NAME})
  endif()

  if(${DOSEK_BINARY_TEST_ISO} STREQUAL "TRUE")
    dosek_add_test(${NAME} )
  else()
    # Add a compile testcase
    add_test(test-${NAME} make ${NAME}-clean ${NAME})
  endif()

ENDMACRO(DOSEK_BINARY)
