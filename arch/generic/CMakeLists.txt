message(STATUS "Preparing generic startup code.")

set(SRCS
		constructors.cc
		constructors.h
		startup.cc
)

# Setup linker script
set(LINKER_SCRIPT "${PROJECT_BINARY_DIR}/linker.ld")
configure_file(linker.ld.in ${LINKER_SCRIPT})

# Show target specific sources, linker script
message(STATUS "Linker script: ${LINKER_SCRIPT}")

# The actual executable
add_executable(${ELFFILE} ${SRCS})
target_link_libraries(${ELFFILE} arch os gcc)

# Set custom linker script
	set_target_properties(${ELFFILE} PROPERTIES LINK_FLAGS
			"-Wl,-T ${LINKER_SCRIPT} -Wl,-nostdlib ${ISA_LD_FLAGS} -nostdlib -ffreestanding" )

