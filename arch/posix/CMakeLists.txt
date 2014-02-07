# (Emulated) RAM size
set(RAM_SIZE "16" CACHE STRING "(Emulated) RAM size in MB")

# Debugger to use
find_program(DEBUGGER "gdb" DOC "Debugger (gdb/ddd)")

# (Random) port for debugging
string(RANDOM LENGTH 4 ALPHABET "123456789" DPORT)
set(DEBUG_PORT ${DPORT} CACHE STRING "Debug (stub) port")
message(STATUS "[${PROJECT_NAME}] Using port ${DEBUG_PORT} for debug stub")

# Enable emulators
OPTION(X86_TARGET_BOCHS "Bochs" OFF)
OPTION(X86_TARGET_QEMU "QEMU" OFF)

# setup x86-32 specific sources
set(SRCS
    dispatch.cc
    terminal.cc
    startup.cc
    itimer.cc
    output.cc
    signalinfo.cc
    irq.cc
)

# Create arch library
add_library(arch ${SRCS})
target_link_libraries(arch generic)

# Add to include directories
coredos_include_dir(${CMAKE_CURRENT_SOURCE_DIR})
set(ARCH_INCLUDE_DIRS ${ARCH_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR} CACHE INTERNAL STRING)

# Setup linker script
#set(LINKER_SCRIPT "${PROJECT_BINARY_DIR}/linker.ld")
#configure_file(linker.ld.in ${LINKER_SCRIPT})

# Show target specific sources, linker script
#message(STATUS "Linker script: ${LINKER_SCRIPT}")

# POSIX CoRedOS executable macro
macro(coredos_executable ELFFILE)
    set(options "EXCLUDE_FROM_ALL")
    set(oneValueArgs "LINKER_SCRIPT")
    set(multiValuedParameters DEFINITIONS LIBS SOURCES)
    cmake_parse_arguments(COREDOS_EXECUTABLE "${options}" "${oneValueArgs}" "${multiValuedParameters}" ${ARGN} )
	set(SOURCES ${COREDOS_EXECUTABLE_SOURCES} ${COREDOS_EXECUTABLE_UNPARSED_ARGUMENTS})
	set(DEFINITIONS ${COREDOS_EXECUTABLE_DEFINITIONS})
    set(ADD_EXECUTABLE_OPTIONS "")
    if(${COREDOS_EXECUTABLE_EXCLUDE_FROM_ALL} STREQUAL "TRUE")
      set(ADD_EXECUTABLE_OPTIONS "EXCLUDE_FROM_ALL")
    endif()


	get_filename_component(ELFNAME ${ELFFILE} NAME_WE)

	# libraries to link with application
	set(TARGET_LIBS os arch ${COREDOS_EXECUTABLE_LIBS})

	# The actual executable
	add_executable(${ELFFILE} ${ADD_EXECUTABLE_OPTIONS} ${SOURCES})
	target_link_libraries(${ELFFILE} ${TARGET_LIBS})

	# set definitions
	if(COREDOS_EXECUTABLE_DEFINITIONS)
		set_target_properties(${ELFFILE} PROPERTIES COMPILE_DEFINITIONS ${COREDOS_EXECUTABLE_DEFINITIONS})
	endif()


	# Set custom linker script/flags
	# libgcc added here to be used as needed (compiler helper functions)and not included in full
	set_target_properties(${ELFFILE} PROPERTIES LINK_FLAGS
		"-lgcc  ${ISA_LD_FLAGS} --linker-prefix=${CMAKE_CURRENT_BINARY_DIR}/${ELFFILE}")


	# we use our own linker (python) script, that calls llvm-link, llc and the system linker
	# setting CMAKE_*_LINK_EXECUTABLE at this point in the CMake run seems a bit unusual, but works as intended
	set(LINK_EXECUTABLE "${PROJECT_SOURCE_DIR}/toolchain/linker --llvm-dir ${CCDIR} <LINK_FLAGS> <OBJECTS> <LINK_LIBRARIES> -o <TARGET>")
	set(CMAKE_C_LINK_EXECUTABLE "${LINK_EXECUTABLE} <CMAKE_C_LINK_FLAGS>")
	set(CMAKE_CXX_LINK_EXECUTABLE "${LINK_EXECUTABLE} <CMAKE_CXX_LINK_FLAGS>")

	# add to executables list
	set(EXECUTABLES ${EXECUTABLES} ${ELFFILE} CACHE INTERNAL STRING)
endmacro()

macro(coredos_add_test FN)
    add_test(${FN} ${PROJECT_BINARY_DIR}/${FN})
    set_tests_properties(${FN} PROPERTIES PASS_REGULAR_EXPRESSION "SUCCESS.+ALL OK" FAIL_REGULAR_EXPRESSION "FAIL" TIMEOUT 10)
    add_dependencies( build_and_test ${FN} )
    add_dependencies( ctest2jenkins ${FN} )
endmacro()
