include(CMakeParseArguments)
include(rtsc)

MACRO(COREDOS_BINARY_EXECUTABLE NAME SOURCES SYSTEM_XML VERIFY_SCRIPT DEFINITIONS LIBS GENERATOR_ARGS)
  SET(COREDOS_ANNOTATE_SOURCE "${COREDOS_GENERATOR_DIR}/annotate/cored_annotate.cc")
  SET(COREDOS_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/${NAME}")
  file(MAKE_DIRECTORY "${COREDOS_OUTPUT_DIR}")
  SET(COREDOS_ANNOTATE_OBJECT "${COREDOS_OUTPUT_DIR}/cored_annotate.ll")

  # compile annotate file
  add_custom_command(OUTPUT ${COREDOS_ANNOTATE_OBJECT}
    COMMAND ${CLANGPP_BINARY} -S -emit-llvm
    -I${COREDOS_GENERATOR_DIR}/annotate/
    ${ISA_CXX_FLAGS}
    ${INCLUDEDIRS_FLAGS}
    -Wno-return-type
    -m32 -std=c++11
    ${COREDOS_ANNOTATE_SOURCE} -o ${COREDOS_ANNOTATE_OBJECT}
    MAIN_DEPENDENCY ${COREDOS_ANNOTATE_SOURCE}
    COMMENT "[${PROJECT_NAME}/${name}] Compiling cored_annotate.c with clang")

  set(COREDOS_SOURCE_SYSTEM "${COREDOS_OUTPUT_DIR}/source_system.ll")
  set(COREDOS_RTSC_ANALYZE_XML "${COREDOS_OUTPUT_DIR}/rtsc_analyze.xml")
  set(COREDOS_GENERATED_SOURCE "${COREDOS_OUTPUT_DIR}/coredos.cc")
  set(COREDOS_GENERATED_LINKER "${COREDOS_OUTPUT_DIR}/linker.ld")


  set(COREDOS_GENERATED_LLVM "${COREDOS_OUTPUT_DIR}/coredos.ll")
  set(COREDOS_BINARY_LLVM_BYTECODE "")

  set(DEFINITON_FLAGS ";")
  foreach(DEF ${DEFINITIONS})
    set(DEFINITON_FLAGS ${DEFINITON_FLAGS} -D${DEF})
  endforeach()

  # First we have to compile all source files with clang
  foreach(src ${SOURCES})
    set(llvm_bytecode "${COREDOS_OUTPUT_DIR}/${src}.ll")
    add_custom_command(OUTPUT ${llvm_bytecode}
      COMMAND ${CLANGPP_BINARY} -S -emit-llvm -O0 -m32 -std=c++11 ${ISA_CXX_FLAGS} ${DEFINITON_FLAGS} ${INCLUDEDIRS_FLAGS} ${CMAKE_CURRENT_SOURCE_DIR}/${src} -o ${llvm_bytecode}
      MAIN_DEPENDENCY ${src}
      DEPENDS ${src}
      IMPLICIT_DEPENDS CXX ${CMAKE_CURRENT_SOURCE_DIR}/${src}
      COMMENT "[${PROJECT_NAME}/${NAME}] Compiling application ${NAME}/${src} with clang")

    list(APPEND COREDOS_BINARY_LLVM_BYTECODE ${llvm_bytecode})
  endforeach(src)

  # Use RTSC to analyze and merge the source system bytecode
  add_custom_command(OUTPUT "${COREDOS_SOURCE_SYSTEM}"
  DEPENDS ${COREDOS_ANNOTATE_OBJECT}
            ${COREDOS_BINARY_LLVM_BYTECODE}
            ${CMAKE_CURRENT_SOURCE_DIR}/*.xml
  COMMAND ${EAG_BINARY} -data-deps=explicit -verify
     -sysann=${COREDOS_ANNOTATE_OBJECT}
     -sourcesystem=${SYSTEM_XML}
     -out=${COREDOS_OUTPUT_DIR}
     -analyze-tasks -dump-source-system
       -dump-graphs
     ${COREDOS_BINARY_LLVM_BYTECODE}
    COMMENT "[${PROJECT_NAME}/${NAME}] Analyzing application with RTSC")

  # Add Target for the analysis step
  add_custom_target(${NAME}-rtsc-analyze
  DEPENDS ${COREDOS_SOURCE_SYSTEM})


  # All python source files are a dependency
  SET(COREDOS_GENERATOR_ARGS "${GENERATOR_ARGS}")
  file(GLOB_RECURSE PYTHON_SOURCE "${COREDOS_GENERATOR_DIR}/*.py")
  file(GLOB_RECURSE OS_TEMPLATES "${PROJECT_SOURCE_DIR}/os/*.in")
  set(LINKER_TEMPLATE ${PROJECT_SOURCE_DIR}/arch/i386/linker.ld.in)
  if(EXISTS "${VERIFY_SCRIPT}")
    if (IS_DIRECTORY "${VERIFY_SCRIPT}")
      SET(VERIFY_SCRIPT "")
    else()
      SET(COREDOS_GENERATOR_ARGS ${COREDOS_GENERATOR_ARGS} --verify ${VERIFY_SCRIPT})
    endif()
  else()
    SET(VERIFY_SCRIPT "")
  endif()

  if(NOT ENCODED_SYSTEM)
    set(COREDOS_GENERATOR_ARGS ${COREDOS_GENERATOR_ARGS} --unencoded)
  endif()

if(SPECIALIZE_SYSTEMCALLS)
    set(COREDOS_GENERATOR_ARGS ${COREDOS_GENERATOR_ARGS} --specialize-systemcalls)
  endif()

  # Generating COREDOS System
  add_custom_command(OUTPUT "${COREDOS_GENERATED_SOURCE}" 
  DEPENDS ${PYTHON_SOURCE} "${SYSTEM_XML}" "${COREDOS_SOURCE_SYSTEM}"
            "${LLVM_NM_BINARY}" ${VERIFY_SCRIPT} ${OS_TEMPLATES} ${LINKER_TEMPLATE}
    COMMAND ${CMAKE_COMMAND} -E remove -f ${COREDOS_OUTPUT_DIR}/gen_*.dot
    COMMAND ${COREDOS_GENERATOR}
     --system-xml "${SYSTEM_XML}"
       --rtsc-analyze-xml "${COREDOS_RTSC_ANALYZE_XML}"
       --prefix ${COREDOS_OUTPUT_DIR}
       --name ${NAME}
       --template-base ${PROJECT_SOURCE_DIR}
       --arch ${COREDOS_ARCHITECTURE}
       ${COREDOS_GENERATOR_ARGS}
     COMMAND
        if [ x"$$EDIT" != x"" ]; then vim ${COREDOS_GENERATED_SOURCE}\; fi
  COMMENT "[${PROJECT_NAME}/${NAME}] Generating COREDOS source code"
  )

  add_custom_target(${NAME}-generate DEPENDS "${COREDOS_GENERATED_SOURCE}")

  add_custom_target(${NAME}-clean
    COMMAND ${CMAKE_COMMAND} -E remove -f ${COREDOS_OUTPUT_DIR}/* ${COREDOS_BINARY_LLVM_BYTECODE}
  )


  # Since COREDOS_SOURCE_SYSTEM end in .ll the add_executable would
  # simply *silently* ignore the "object" file, by declaring it
  # external it is passed on to the linker
  SET_SOURCE_FILES_PROPERTIES(
    ${COREDOS_SOURCE_SYSTEM}
    PROPERTIES
    EXTERNAL_OBJECT true # to say that "this is actually an object file, so it should not be compiled, only linked"
    GENERATED true       # to say that "it is OK that the obj-files do not exist before build time"
  )

  # Compile the coredos system
  include_directories(${RTSC_SOURCE_DIR}/data/SystemSupport/CoReD/include/)
  coredos_executable(${NAME} EXCLUDE_FROM_ALL
    SOURCES ${COREDOS_SOURCE_SYSTEM} ${COREDOS_GENERATED_SOURCE}
    LIBS ${COREDOS_BINARY_LIBS}
    DEFINITIONS ${DEFINITIONS}
    LINKER_SCRIPT ${COREDOS_GENERATED_LINKER}
    )

ENDMACRO()

MACRO(COREDOS_BINARY)
  set(options TEST_ISO FAIL)
  set(oneValueArgs SYSTEM_XML NAME VERIFY)
  set(multiValuedParameters SOURCES LIBS GENERATOR_ARGS)
  cmake_parse_arguments(COREDOS_BINARY "${options}" "${oneValueArgs}" "${multiValuedParameters}" ${ARGN} )
  set(COREDOS_BINARY_SOURCES "${COREDOS_BINARY_UNPARSED_ARGUMENTS};${COREDOS_BINARY_SOURCES}")
  SET(COREDOS_SYSTEM_XML "${CMAKE_CURRENT_SOURCE_DIR}/${COREDOS_BINARY_SYSTEM_XML}")
  set(COREDOS_VERIFY_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/${COREDOS_BINARY_VERIFY}")
  SET(NAME "${COREDOS_BINARY_NAME}")

  COREDOS_BINARY_EXECUTABLE(${NAME} "${COREDOS_BINARY_SOURCES}" ${COREDOS_SYSTEM_XML} ${COREDOS_VERIFY_SCRIPT} 
    "" "${COREDOS_BINARY_LIBS}" "${COREDOS_BINARY_GENERATOR_ARGS}")
  add_custom_command(TARGET ${NAME} POST_BUILD
    COMMENT "Gathering binary statistics for ${NAME}"
    COMMAND ${COREDOS_GENERATOR_DIR}/stats_binary.py
    --stats-dict ${COREDOS_OUTPUT_DIR}/stats.dict.py
    --elf ${PROJECT_BINARY_DIR}/${NAME})
  

  if((${COREDOS_BINARY_FAIL} STREQUAL "TRUE") OR FAIL_TRACE_ALL)
    COREDOS_BINARY_EXECUTABLE(fail-${NAME} "${COREDOS_BINARY_SOURCES}" ${COREDOS_SYSTEM_XML} ${COREDOS_VERIFY_SCRIPT} 
      "FAIL=1" "${COREDOS_BINARY_LIBS}" "${COREDOS_BINARY_GENERATOR_ARGS}")

    fail_test(${NAME} fail-${NAME})
  endif()

  if(${COREDOS_BINARY_TEST_ISO} STREQUAL "TRUE")
    coredos_add_test(${NAME} )
  else()
    # Add a compile testcase
    add_test(test-${NAME} make ${NAME}-clean ${NAME})
  endif()


ENDMACRO(COREDOS_BINARY)
