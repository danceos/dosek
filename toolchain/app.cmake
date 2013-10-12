include(CMakeParseArguments)
include(rtsc)

MACRO(COREDOS_BINARY)
  set(options )
  set(oneValueArgs SYSTEM_XML NAME)
  set(multiValuedParameters SOURCES)
  cmake_parse_arguments(COREDOS_BINARY "${options}" "${oneValueArgs}" "${multiValuedParameters}" ${ARGN} )
  set(COREDOS_BINARY_SOURCES "${COREDOS_BINARY_UNPARSED_ARGUMENTS};${COREDOS_BINARY_SOURCES}")

  # First we have to compile all source files with clang
  foreach(src ${COREDOS_BINARY_SOURCES})
	set(llvm_bytecode "${CMAKE_CURRENT_BINARY_DIR}/${src}.ll")
	add_custom_command(OUTPUT ${llvm_bytecode}
	  COMMAND ${RTSC_LLVM_BINARY_DIR}/bin/clang -S -emit-llvm -O0 
	  -I${RTSC_SOURCE_DIR}/data/SystemSupport/OSEKOS/include/
	  ${CMAKE_CURRENT_SOURCE_DIR}/${src} -o ${llvm_bytecode}
	  MAIN_DEPENDENCY ${CMAKE_CURRENT_SOURCE_DIR}/${src}
      COMMENT "[${PROJECT_NAME}] Compiling application ${src} with clang")
	

	list(APPEND COREDOS_BINARY_LLVM_BYTECODE ${llvm_bytecode})
  endforeach(src)

  set(COREDOS_SOURCE_SYSTEM "${CMAKE_CURRENT_BINARY_DIR}/source_system.ll")
  
  # Use RTSC to analyze and merge the source system bytecode
  add_custom_command(OUTPUT "${COREDOS_SOURCE_SYSTEM}"
	DEPENDS ${COREDOS_BINARY_LLVM_BYTECODE}
	COMMAND ${RTSC_BINARY} -data-deps=explicit -verify 
	   -sysann=${RTSC_BINARY_DIR}/test/annotate_osek.ll
	   -sourcesystem=${CMAKE_CURRENT_SOURCE_DIR}/${COREDOS_BINARY_SYSTEM_XML}
	   -pns=1 -out=${CMAKE_CURRENT_BINARY_DIR} 
	   -march=${CMAKE_C_ARCH} 
	   -analyze-tasks -dump-source-system
	   ${COREDOS_BINARY_LLVM_BYTECODE}
       COMMENT "[${PROJECT_NAME}] Analyzing application with RTSC")
	 

  # Add Target for the analysis step
  add_custom_target(${COREDOS_BINARY_NAME}-rtsc-analyze
	DEPENDS ${COREDOS_SOURCE_SYSTEM})

ENDMACRO(COREDOS_BINARY)
