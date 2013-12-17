message(STATUS "Preparing generic startup code.")

set(SRCS
		startup.cc
		constructors.cc
		constructors.h
		ostream.cc
)

# Add to include directories
set(ARCH_INCLUDE_DIRS ${ARCH_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR} CACHE INTERNAL STRING)

# Setup linker script
set(LINKER_SCRIPT "${PROJECT_BINARY_DIR}/linker.ld")
configure_file(linker.ld.in ${LINKER_SCRIPT})

# Show target specific sources, linker script
message(STATUS "Linker script: ${LINKER_SCRIPT}")

# Link startup code into library
add_library(generic ${SRCS})

macro(coredos_executable ELFFILE)
	# The actual executable
	add_executable(${ELFFILE} ${ARGN})

	target_link_libraries(${ELFFILE} os arch gcc)

	# Set custom linker script
	set_target_properties(${ELFFILE} PROPERTIES LINK_FLAGS
				"-Wl,-T ${PROJECT_BINARY_DIR}/linker.ld ${ISA_LD_FLAGS} -Wl,--build-id=none" )

    # Since the os_main function is defined in the generated coredos
    # source code, we have an cyclic symbol dependency. Therefore we
    # add --start-group,--end-group "parentheses" around object files
    # and library files.
    SET(CMAKE_CXX_LINK_EXECUTABLE  "<CMAKE_CXX_COMPILER> <FLAGS> <CMAKE_CXX_LINK_FLAGS> <LINK_FLAGS> -Xlinker --start-group <OBJECTS> <LINK_LIBRARIES> -Xlinker --end-group -o <TARGET>")
    SET(CMAKE_C_LINK_EXECUTABLE  "<CMAKE_C_COMPILER> <FLAGS> <CMAKE_C_LINK_FLAGS> <LINK_FLAGS> -Xlinker --start-group <OBJECTS> <LINK_LIBRARIES> -Xlinker --end-group -o <TARGET>")

	set(EXECUTABLES ${EXECUTABLES} ${ELFFILE} CACHE INTERNAL STRING)
endmacro()

coredos_executable(${ELFFILE} "${SRCS}")
