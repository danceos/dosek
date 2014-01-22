include(CMakeParseArguments)
include(rtsc)


MACRO(COREDOS_BINARY)
  set(options )
  set(oneValueArgs SYSTEM_XML NAME VERIFY)
  set(multiValuedParameters SOURCES)
  cmake_parse_arguments(COREDOS_BINARY "${options}" "${oneValueArgs}" "${multiValuedParameters}" ${ARGN} )
  set(COREDOS_BINARY_SOURCES "${COREDOS_BINARY_UNPARSED_ARGUMENTS};${COREDOS_BINARY_SOURCES}")
  SET(COREDOS_SYSTEM_XML "${CMAKE_CURRENT_SOURCE_DIR}/${COREDOS_BINARY_SYSTEM_XML}")
  SET(NAME "${COREDOS_BINARY_NAME}")

  SET(COREDOS_ANNOTATE_SOURCE "${COREDOS_GENERATOR_DIR}/annotate/cored_annotate.c")
  SET(COREDOS_ANNOTATE_OBJECT "${CMAKE_CURRENT_BINARY_DIR}/${NAME}_cored_annotate.ll")

  # compile annotate file
  add_custom_command(OUTPUT ${COREDOS_ANNOTATE_OBJECT}
    COMMAND ${CLANG_BINARY} -S -emit-llvm
    -I${COREDOS_GENERATOR_DIR}/annotate/
    ${INCLUDEDIRS_FLAGS}
    -Wno-return-type 
    -m32
    ${COREDOS_ANNOTATE_SOURCE} -o ${COREDOS_ANNOTATE_OBJECT}
    MAIN_DEPENDENCY ${COREDOS_ANNOTATE_SOURCE}
    COMMENT "[${PROJECT_NAME}/${name}] Compiling cored_annotate.c with clang")

  set(BDIR "${CMAKE_CURRENT_BINARY_DIR}")
  set(COREDOS_SOURCE_SYSTEM "${BDIR}/${NAME}_source_system.ll")
  set(COREDOS_RTSC_ANALYZE_XML "${BDIR}/${NAME}_rtsc_analyze.xml")
  set(COREDOS_SOURCE_SYSTEM_OBJECT "${BDIR}/${NAME}_source_system.o")

  set(COREDOS_GENERATED_SOURCE "${BDIR}/${NAME}_coredos.cc")
  set(COREDOS_GENERATED_LLVM "${BDIR}/${NAME}_coredos.ll")
  set(COREDOS_BINARY_LLVM_BYTECODE "")
  set(tmp "")

  # First we have to compile all source files with clang
  foreach(src ${COREDOS_BINARY_SOURCES})
	set(llvm_bytecode "${CMAKE_CURRENT_BINARY_DIR}/${src}.ll")
	add_custom_command(OUTPUT ${llvm_bytecode}
	  COMMAND ${CLANG_BINARY} -S -emit-llvm -O0 
      -m32
      ${INCLUDEDIRS_FLAGS}
	  ${CMAKE_CURRENT_SOURCE_DIR}/${src} -o ${llvm_bytecode}
	  MAIN_DEPENDENCY ${CMAKE_CURRENT_SOURCE_DIR}/${src}
	  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/${src}

      COMMENT "[${PROJECT_NAME}/${NAME}] Compiling application ${NAME}/${src} with clang")
	

	list(APPEND COREDOS_BINARY_LLVM_BYTECODE ${llvm_bytecode})
	list(APPEND tmp ${CMAKE_CURRENT_SOURCE_DIR}/${src})
  endforeach(src)

  SET(COREDOS_BINARY_SOURCES ${tmp})

  
  # Use RTSC to analyze and merge the source system bytecode
  add_custom_command(OUTPUT "${COREDOS_SOURCE_SYSTEM}"
	DEPENDS ${COREDOS_ANNOTATE_OBJECT} 
            ${COREDOS_BINARY_LLVM_BYTECODE}
            ${CMAKE_CURRENT_SOURCE_DIR}/*.xml
	COMMAND ${RTSC_BINARY} -data-deps=explicit -verify 
	   -sysann=${COREDOS_ANNOTATE_OBJECT}
	   -sourcesystem=${CMAKE_CURRENT_SOURCE_DIR}/${COREDOS_BINARY_SYSTEM_XML}
	   -pns=1 -out=${CMAKE_CURRENT_BINARY_DIR} 
	   -march=${CMAKE_C_ARCH} 
	   -analyze-tasks -dump-source-system
       -dump-graphs
	   ${COREDOS_BINARY_LLVM_BYTECODE}
    COMMAND
       mv ${BDIR}/source_system.ll ${COREDOS_SOURCE_SYSTEM}
    COMMAND
       mv ${BDIR}/rtsc_analyze.xml ${COREDOS_RTSC_ANALYZE_XML}
    COMMENT "[${PROJECT_NAME}/${NAME}] Analyzing application with RTSC")

  # Compile source system to a .o file
  add_custom_command(OUTPUT "${COREDOS_SOURCE_SYSTEM_OBJECT}"
	DEPENDS "${COREDOS_SOURCE_SYSTEM}"
	COMMAND ${CLANG_BINARY} -m32 -c -o "${COREDOS_SOURCE_SYSTEM_OBJECT}" "${COREDOS_SOURCE_SYSTEM}"
	COMMENT "[${PROJECT_NAME}/${NAME}] Generating object file for app")

  # Add Target for the analysis step
  add_custom_target(${COREDOS_BINARY_NAME}-rtsc-analyze
	DEPENDS ${COREDOS_SOURCE_SYSTEM} ${COREDOS_SOURCE_SYSTEM_OBJECT})


  # All python source files are a dependency
  SET(COREDOS_GENERATOR_ARGS "")
  file(GLOB_RECURSE PYTHON_SOURCE "${COREDOS_GENERATOR_DIR}/*.py")
  set(COREDOS_VERIFY_SCRIPT "${CMAKE_CURRENT_SOURCE_DIR}/${COREDOS_BINARY_VERIFY}")
  if(EXISTS "${COREDOS_VERIFY_SCRIPT}")
    if (IS_DIRECTORY "${COREDOS_VERIFY_SCRIPT}")
      SET(COREDOS_VERIFY_SCRIPT "")
    else()
      SET(COREDOS_GENERATOR_ARGS ${COREDOS_GENERATOR_ARGS} --verify ${COREDOS_VERIFY_SCRIPT})
    endif()
  else()
    SET(COREDOS_VERIFY_SCRIPT "")
  endif()

  # Generating COREDOS System
  add_custom_command(OUTPUT "${COREDOS_GENERATED_SOURCE}"
	DEPENDS ${PYTHON_SOURCE} "${COREDOS_SYSTEM_XML}" "${COREDOS_SOURCE_SYSTEM_OBJECT}" 
            "${LLVM_NM_BINARY}" ${COREDOS_VERIFY_SCRIPT}
    COMMAND ${COREDOS_GENERATOR} 
	   --system-xml "${COREDOS_SYSTEM_XML}"
	   --app-object "${COREDOS_SOURCE_SYSTEM_OBJECT}" 
       --rtsc-analyze-xml "${COREDOS_RTSC_ANALYZE_XML}"
	   --nm "${LLVM_NM_BINARY}"
	   --output "${COREDOS_GENERATED_SOURCE}"
       ${COREDOS_GENERATOR_ARGS}
	   -vv
	COMMENT "[${PROJECT_NAME}/${NAME}] Generating COREDOS source code"
	)

  add_custom_target(${COREDOS_BINARY_NAME}-generate
	DEPENDS "${COREDOS_GENERATED_SOURCE}")

  add_custom_target(${COREDOS_BINARY_NAME}-clean
	COMMAND rm -f ${CMAKE_CURRENT_BINARY_DIR}/${NAME}*
    )


  # Compile the coredos system
  include_directories(${RTSC_SOURCE_DIR}/data/SystemSupport/CoReD/include/)
  coredos_executable(${NAME} EXCLUDE_FROM_ALL
    ${COREDOS_SOURCE_SYSTEM_OBJECT} ${COREDOS_GENERATED_SOURCE})

  add_test(${NAME}-test make ${NAME}-clean ${NAME}-generate)
ENDMACRO(COREDOS_BINARY)
