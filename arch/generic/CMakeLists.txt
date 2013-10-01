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

macro(coredos_executable ELFFILE SRCS )
	# The actual executable
	add_executable(${ELFFILE} ${SRCS})

	target_link_libraries(${ELFFILE} os arch gcc)

	# Set custom linker script
	set_target_properties(${ELFFILE} PROPERTIES LINK_FLAGS
				"-Wl,-T ${PROJECT_BINARY_DIR}/linker.ld -Wl,-nostdlib ${ISA_LD_FLAGS} -nostdlib -ffreestanding" )

	set(EXECUTABLES ${EXECUTABLES} ${ELFFILE} CACHE INTERNAL STRING)
endmacro()

coredos_executable(${ELFFILE} "${SRCS}")
