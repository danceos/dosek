include(CMakeParseArguments)
include(rtsc)

MACRO(COREDOS_BINARY_EXECUTABLE NAME SOURCES SYSTEM_XML VERIFY_SCRIPT DEFINITIONS)
  SET(COREDOS_ANNOTATE_SOURCE "${COREDOS_GENERATOR_DIR}/annotate/cored_annotate.cc")
  SET(COREDOS_ANNOTATE_OBJECT "${CMAKE_CURRENT_BINARY_DIR}/${NAME}_cored_annotate.ll")

  # compile annotate file
  add_custom_command(OUTPUT ${COREDOS_ANNOTATE_OBJECT}
    COMMAND ${CLANGPP_BINARY} -S -emit-llvm
    -I${COREDOS_GENERATOR_DIR}/annotate/
    ${INCLUDEDIRS_FLAGS}
    -Wno-return-type
    -m32 -std=c++11
    ${COREDOS_ANNOTATE_SOURCE} -o ${COREDOS_ANNOTATE_OBJECT}
    MAIN_DEPENDENCY ${COREDOS_ANNOTATE_SOURCE}
    COMMENT "[${PROJECT_NAME}/${name}] Compiling cored_annotate.c with clang")

  set(BDIR "${CMAKE_CURRENT_BINARY_DIR}")
  set(COREDOS_SOURCE_SYSTEM "${BDIR}/${NAME}_source_system.ll")
  set(COREDOS_RTSC_ANALYZE_XML "${BDIR}/${NAME}_rtsc_analyze.xml")

  set(COREDOS_GENERATED_SOURCE "${BDIR}/${NAME}_coredos.cc")

  set(COREDOS_GENERATED_LINKER "${BDIR}/${NAME}_linker.ld")


  set(COREDOS_GENERATED_LLVM "${BDIR}/${NAME}_coredos.ll")
  set(COREDOS_BINARY_LLVM_BYTECODE "")
  set(tmp "")

  set(DEFINITON_FLAGS ";")
  foreach(DEF ${DEFINITIONS})
    set(DEFINITON_FLAGS ${DEFINITON_FLAGS} -D${DEF})
  endforeach()

  # First we have to compile all source files with clang
  foreach(src ${SOURCES})
    set(llvm_bytecode "${CMAKE_CURRENT_BINARY_DIR}/${src}.ll")
    add_custom_command(OUTPUT ${llvm_bytecode}
      COMMAND ${CLANGPP_BINARY} -S -emit-llvm -O0 -m32 -std=c++11 ${DEFINITON_FLAGS} ${INCLUDEDIRS_FLAGS} ${CMAKE_CURRENT_SOURCE_DIR}/${src} -o ${llvm_bytecode}
      MAIN_DEPENDENCY ${src}
      DEPENDS ${src}
      COMMENT "[${PROJECT_NAME}/${NAME}] Compiling application ${NAME}/${src} with clang")

    list(APPEND COREDOS_BINARY_LLVM_BYTECODE ${llvm_bytecode})
    list(APPEND tmp ${src})
  endforeach(src)

  SET(COREDOS_BINARY_SOURCES ${tmp})


  # Use RTSC to analyze and merge the source system bytecode
  add_custom_command(OUTPUT "${COREDOS_SOURCE_SYSTEM}"
  DEPENDS ${COREDOS_ANNOTATE_OBJECT}
            ${COREDOS_BINARY_LLVM_BYTECODE}
            ${CMAKE_CURRENT_SOURCE_DIR}/*.xml
  COMMAND ${EAG_BINARY} -data-deps=explicit -verify
     -sysann=${COREDOS_ANNOTATE_OBJECT}
     -sourcesystem=${SYSTEM_XML}
     -out=${CMAKE_CURRENT_BINARY_DIR}
     -analyze-tasks -dump-source-system
       -dump-graphs
     ${COREDOS_BINARY_LLVM_BYTECODE}
    COMMAND
      ${CMAKE_COMMAND} -E rename ${BDIR}/source_system.ll ${COREDOS_SOURCE_SYSTEM}
    COMMAND
       ${CMAKE_COMMAND} -E rename ${BDIR}/rtsc_analyze.xml ${COREDOS_RTSC_ANALYZE_XML}
    COMMENT "[${PROJECT_NAME}/${NAME}] Analyzing application with RTSC")

  # Add Target for the analysis step
  add_custom_target(${NAME}-rtsc-analyze
  DEPENDS ${COREDOS_SOURCE_SYSTEM})


  # All python source files are a dependency
  SET(COREDOS_GENERATOR_ARGS "")
  file(GLOB_RECURSE PYTHON_SOURCE "${COREDOS_GENERATOR_DIR}/*.py")
  file(GLOB_RECURSE OS_TEMPLATES "${PROJECT_SOURCE_DIR}/os/*.in")
  set(LINKER_TEMPLATE ${PROJECT_SOURCE_DIR}/arch/i386/linker.ld.in)
  if(EXISTS "${VERIFY_SCRIPT}")
    if (IS_DIRECTORY "${VERIFY_SCRIPT}")
      SET(COREDOS_VERIFY_SCRIPT "")
    else()
      SET(COREDOS_GENERATOR_ARGS ${COREDOS_GENERATOR_ARGS} --verify ${VERIFY_SCRIPT})
    endif()
  else()
    SET(COREDOS_VERIFY_SCRIPT "")
  endif()

  # Generating COREDOS System
  add_custom_command(OUTPUT "${COREDOS_GENERATED_SOURCE}" ${COREDOS_GENERATED_LINKER}
  DEPENDS ${PYTHON_SOURCE} "${SYSTEM_XML}" "${COREDOS_SOURCE_SYSTEM}"
            "${LLVM_NM_BINARY}" ${COREDOS_VERIFY_SCRIPT} ${OS_TEMPLATES} ${LINKER_TEMPLATE}
    COMMAND ${COREDOS_GENERATOR}
     --system-xml "${SYSTEM_XML}"
       --rtsc-analyze-xml "${COREDOS_RTSC_ANALYZE_XML}"
     --prefix ${BDIR}
       --name ${NAME}
       --template-base ${PROJECT_SOURCE_DIR}
       ${COREDOS_GENERATOR_ARGS}
     -vv
  COMMENT "[${PROJECT_NAME}/${NAME}] Generating COREDOS source code"
  )

  add_custom_target(${NAME}-generate DEPENDS "${COREDOS_GENERATED_SOURCE}")

  add_custom_target(${NAME}-clean
    COMMAND ${CMAKE_COMMAND} -E remove -f ${CMAKE_CURRENT_BINARY_DIR}/${NAME}* ${COREDOS_BINARY_LLVM_BYTECODE}
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
    ${COREDOS_SOURCE_SYSTEM} ${COREDOS_GENERATED_SOURCE} LINKER_SCRIPT ${COREDOS_GENERATED_LINKER} DEFINITIONS ${DEFINITIONS})

ENDMACRO()

MACRO(COREDOS_BINARY)
  set(options TEST_ISO FAIL)
  set(oneValueArgs SYSTEM_XML NAME VERIFY)
  set(multiValuedParameters SOURCES)
  cmake_parse_arguments(COREDOS_BINARY "${options}" "${oneValueArgs}" "${multiValuedParameters}" ${ARGN} )
  set(COREDOS_BINARY_SOURCES "${COREDOS_BINARY_UNPARSED_ARGUMENTS};${COREDOS_BINARY_SOURCES}")
  SET(COREDOS_SYSTEM_XML "${CMAKE_CURRENT_SOURCE_DIR}/${COREDOS_BINARY_SYSTEM_XML}")
  set(COREDOS_VERIFY_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/${COREDOS_BINARY_VERIFY}")
  SET(NAME "${COREDOS_BINARY_NAME}")

  COREDOS_BINARY_EXECUTABLE(${NAME} "${COREDOS_BINARY_SOURCES}" ${COREDOS_SYSTEM_XML} ${COREDOS_VERIFY_SCRIPT} "${DEFINITIONS}")

  if(${COREDOS_BINARY_FAIL} STREQUAL "TRUE")
    COREDOS_BINARY_EXECUTABLE(fail-${NAME} "${COREDOS_BINARY_SOURCES}" ${COREDOS_SYSTEM_XML} ${COREDOS_VERIFY_SCRIPT} "FAIL=1")

    fail_test(${NAME} fail-${NAME})
  endif()

  if(${COREDOS_BINARY_TEST_ISO} STREQUAL "TRUE")
    coredos_test_iso_image(test-${NAME} ${NAME} "${PROJECT_BINARY_DIR}/${NAME}.iso")
  else()
    # Add a compile testcase
    add_test(test-${NAME} make ${NAME}-clean ${NAME})
  endif()
ENDMACRO(COREDOS_BINARY)
