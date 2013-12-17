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

	target_link_libraries(${ELFFILE} os arch)

	# Set custom linker script
	set_target_properties(${ELFFILE} PROPERTIES LINK_FLAGS
				"-Wl,-T ${PROJECT_BINARY_DIR}/linker.ld ${ISA_LD_FLAGS} -Wl,--build-id=none --linker-prefix=${CMAKE_CURRENT_BINARY_DIR}/${ELFFILE}" )

    # We use our own linker script, that calls llvm-link, llc and the system linker
    SET(CMAKE_CXX_LINK_EXECUTABLE  "${PROJECT_SOURCE_DIR}/toolchain/linker --llvm-dir ${CCDIR} <CMAKE_CXX_LINK_FLAGS> <LINK_FLAGS> <OBJECTS> <LINK_LIBRARIES> -o <TARGET>")
    SET(CMAKE_C_LINK_EXECUTABLE  "${PROJECT_SOURCE_DIR}/toolchain/linker --llvm-dir ${CCDIR} <CMAKE_C_LINK_FLAGS> <LINK_FLAGS> <OBJECTS> <LINK_LIBRARIES>  -o <TARGET>")

	set(EXECUTABLES ${EXECUTABLES} ${ELFFILE} CACHE INTERNAL STRING)
endmacro()