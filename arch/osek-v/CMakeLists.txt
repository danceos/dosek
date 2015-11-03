set(SRCS
  startup.S
  output.cc
  startup.cc
  constructors.cc
  interrupt.cc
  timer.cc
  dispatch.cc
)

# Create arch library
add_library(arch ${SRCS})
target_link_libraries(arch generic)

# Add to include directories
dosek_include_dir(${CMAKE_CURRENT_SOURCE_DIR})
set(ARCH_INCLUDE_DIRS ${ARCH_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR} CACHE INTERNAL STRING)


# POSIX dOSEK executable macro
macro(dosek_executable ELFFILE)
    set(options "EXCLUDE_FROM_ALL")
    set(oneValueArgs "LINKER_SCRIPT")
    set(multiValuedParameters DEFINITIONS LIBS SOURCES)
    cmake_parse_arguments(DOSEK_EXECUTABLE "${options}" "${oneValueArgs}" "${multiValuedParameters}" ${ARGN} )
	set(SOURCES ${DOSEK_EXECUTABLE_SOURCES} ${DOSEK_EXECUTABLE_UNPARSED_ARGUMENTS})
	set(DEFINITIONS ${DOSEK_EXECUTABLE_DEFINITIONS})
    set(ADD_EXECUTABLE_OPTIONS "")
    if(${DOSEK_EXECUTABLE_EXCLUDE_FROM_ALL} STREQUAL "TRUE")
      set(ADD_EXECUTABLE_OPTIONS "EXCLUDE_FROM_ALL")
    endif()


	get_filename_component(ELFNAME ${ELFFILE} NAME_WE)

	# libraries to link with application
	set(TARGET_LIBS os arch ${DOSEK_EXECUTABLE_LIBS})

	# The actual executable
	add_executable(${ELFFILE} ${ADD_EXECUTABLE_OPTIONS} ${SOURCES})
	target_link_libraries(${ELFFILE} ${TARGET_LIBS})

	# set definitions
	if(DOSEK_EXECUTABLE_DEFINITIONS)
		set_target_properties(${ELFFILE} PROPERTIES COMPILE_DEFINITIONS ${DOSEK_EXECUTABLE_DEFINITIONS})
	endif()


	# Set custom linker script/flags
	# libgcc added here to be used as needed (compiler helper functions)and not included in full
	set_target_properties(${ELFFILE} PROPERTIES LINK_FLAGS
		"-lgcc  ${ISA_LD_FLAGS} --linker-prefix=${CMAKE_CURRENT_BINARY_DIR}/${ELFFILE}")


	# we use our own linker (python) script, that calls llvm-link, llc and the system linker
	# setting CMAKE_*_LINK_EXECUTABLE at this point in the CMake run seems a bit unusual, but works as intended
	set(LINK_EXECUTABLE "${PROJECT_SOURCE_DIR}/toolchain/llvm-link.py --clang ${CMAKE_C_COMPILER} --march riscv --mcpu=RocketSmall --ar ${CMAKE_AR} --use-as ${CROSS_AS} --llvm-dir ${CCDIR} <LINK_FLAGS> <OBJECTS> <LINK_LIBRARIES> -o <TARGET> -Wl,-T${PROJECT_SOURCE_DIR}/arch/osek-v/linker.ld")
	set(CMAKE_C_LINK_EXECUTABLE "${LINK_EXECUTABLE} <CMAKE_C_LINK_FLAGS>")
	set(CMAKE_CXX_LINK_EXECUTABLE "${LINK_EXECUTABLE} <CMAKE_CXX_LINK_FLAGS>")

	# add to executables list
	set(EXECUTABLES ${EXECUTABLES} ${ELFFILE} CACHE INTERNAL STRING)

    add_custom_command(TARGET ${ELFNAME} POST_BUILD
      COMMENT "Symlinking rocket config ${NAME}"
      COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/${ELFNAME}/rocket.config ${PROJECT_BINARY_DIR}/${ELFNAME}.rocket.config
    )

endmacro()

macro(dosek_add_test FN)
    add_test(${FN} ${PROJECT_BINARY_DIR}/${FN})
    set_tests_properties(${FN} PROPERTIES PASS_REGULAR_EXPRESSION "SUCCESS.+ALL OK" FAIL_REGULAR_EXPRESSION "FAIL" TIMEOUT 10)
    add_dependencies( tests ${FN} )
endmacro()
