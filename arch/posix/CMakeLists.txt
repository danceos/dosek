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
OPTION(dOSEK_MPU_PROTECTION "MPU (no-effect)" OFF)
message(STATUS "[${PROJECT_NAME}] MPU Protection: ${dOSEK_MPU_PROTECTION}")

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
dosek_include_dir(${CMAKE_CURRENT_SOURCE_DIR})
set(ARCH_INCLUDE_DIRS ${ARCH_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR} CACHE INTERNAL STRING)

# Setup linker script
#set(LINKER_SCRIPT "${PROJECT_BINARY_DIR}/linker.ld")
#configure_file(linker.ld.in ${LINKER_SCRIPT})

# Show target specific sources, linker script
#message(STATUS "Linker script: ${LINKER_SCRIPT}")

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
	set(LINK_EXECUTABLE "${PROJECT_SOURCE_DIR}/toolchain/llvm-link.py --clang ${CMAKE_C_COMPILER} --march x86 --mcpu ${CMAKE_C_ARCH} --llvm-dir ${CCDIR} <LINK_FLAGS> <OBJECTS> <LINK_LIBRARIES> -o <TARGET>")
	set(CMAKE_C_LINK_EXECUTABLE "${LINK_EXECUTABLE} <CMAKE_C_LINK_FLAGS>")
	set(CMAKE_CXX_LINK_EXECUTABLE "${LINK_EXECUTABLE} <CMAKE_CXX_LINK_FLAGS>")

	# add to executables list
	set(EXECUTABLES ${EXECUTABLES} ${ELFFILE} CACHE INTERNAL STRING)
endmacro()

macro(dosek_add_test FN)
    add_test(${FN} ${PROJECT_BINARY_DIR}/${FN})
    set_tests_properties(${FN} PROPERTIES PASS_REGULAR_EXPRESSION "SUCCESS.+ALL OK" FAIL_REGULAR_EXPRESSION "FAIL" TIMEOUT 10)
    add_dependencies( tests ${FN} )
endmacro()
