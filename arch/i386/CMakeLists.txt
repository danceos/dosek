# (Emulated) RAM size
set(RAM_SIZE "16" CACHE STRING "(Emulated) RAM size in MB")

# Debugger to use
find_program(DEBUGGER "gdb" DOC "Debugger (gdb/ddd)")

# (Random) port for debugging
string(RANDOM LENGTH 4 ALPHABET "123456789" DPORT)
set(DEBUG_PORT ${DPORT} CACHE STRING "Debug (stub) port")
message(STATUS "[${PROJECT_NAME}] Using port ${DEBUG_PORT} for debug stub")

# Enable emulators
OPTION(X86_TARGET_BOCHS "Bochs" ON)
OPTION(X86_TARGET_QEMU "QEMU" ON)

if(X86_TARGET_BOCHS OR X86_TARGET_QEMU)
	set(ADDITIONAL_TARGETS ${ADDITIONAL_TARGETS}
		${CMAKE_CURRENT_SOURCE_DIR}/grub CACHE INTERNAL STRING)
endif()
if(X86_TARGET_BOCHS)
	message(STATUS "Target i386 Bochs")
	set(ADDITIONAL_TARGETS ${ADDITIONAL_TARGETS}
		${CMAKE_CURRENT_SOURCE_DIR}/bochs CACHE INTERNAL STRING)
endif()
if(X86_TARGET_QEMU)
	message(STATUS "Target i386 QEMU")
	set(ADDITIONAL_TARGETS ${ADDITIONAL_TARGETS}
		${CMAKE_CURRENT_SOURCE_DIR}/qemu CACHE INTERNAL STRING)
endif()

# setup x86-32 specific sources
set(SRCS
	startup.cc
	startup.s
	gdt.cc
	idt.cc
	idt.S
	paging.cc
	cga.cc
	serial.cc
	pic.cc
	lapic.cc
	ioapic.cc
	pit.cc
	dispatch.cc
	syscall.cc
)

# Create arch library
add_library(arch ${SRCS})
target_link_libraries(arch generic)

# Add to include directories
coredos_include_dir(${CMAKE_CURRENT_SOURCE_DIR})
set(ARCH_INCLUDE_DIRS ${ARCH_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR} CACHE INTERNAL STRING)

# Setup linker script
set(LINKER_SCRIPT "${PROJECT_BINARY_DIR}/linker.ld")
configure_file(linker.ld.in ${LINKER_SCRIPT})

# Show target specific sources, linker script
message(STATUS "Linker script: ${LINKER_SCRIPT}")

# Find objdump for pagetable generation
find_program(OBJDUMP "objdump")

# i386 CoRedOS executable macro
macro(coredos_executable ELFFILE)
	get_filename_component(ELFNAME ${ELFFILE} NAME_WE)

	# libraries to link with application
	set(TARGET_LIBS os arch)

	# First executable with empty, weak page tables
	set(PRELINK ${ELFNAME}.prelink.elf)
	add_executable(${PRELINK} ${ARGN})
	set_target_properties(${PRELINK} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
	target_link_libraries(${PRELINK} ${TARGET_LIBS})

	# Generate pagetables from first executable
	set(PAGETABLES ${ELFNAME}-pagetables.cc)
	set(GENERATOR ${PROJECT_SOURCE_DIR}/arch/i386/generate-pagetables.py)
	add_custom_command(
		DEPENDS ${PRELINK} ${GENERATOR}
		COMMAND ${PYTHON} ${GENERATOR} -o ${OBJDUMP} -c ${PAGETABLES} -e ${PRELINK}
		COMMENT "Generating static page tables for ${ELFFILE}"
		OUTPUT ${PAGETABLES}
	)

	# The actual executable
	add_executable(${ELFFILE} ${ARGN} ${PAGETABLES})
	target_link_libraries(${ELFFILE} ${TARGET_LIBS})

	# Set custom linker script/flags
	# libgcc added here to be used as needed (compiler helper functions)and not included in full
	set_target_properties(${ELFFILE} ${PRELINK} PROPERTIES LINK_FLAGS
		"-lgcc -Wl,-T ${PROJECT_BINARY_DIR}/linker.ld ${ISA_LD_FLAGS} --linker-prefix=${CMAKE_CURRENT_BINARY_DIR}/${ELFFILE}")

	# add dependency on linker script
	set_source_files_properties(
		${ARGN} PROPERTIES OBJECT_DEPENDS ${PROJECT_BINARY_DIR}/linker.ld)

	# we use our own linker (python) script, that calls llvm-link, llc and the system linker
	# setting CMAKE_*_LINK_EXECUTABLE at this point in the CMake run seems a bit unusual, but works as intended
	set(LINK_EXECUTABLE "${PROJECT_SOURCE_DIR}/toolchain/linker --llvm-dir ${CCDIR} <LINK_FLAGS> <OBJECTS> <LINK_LIBRARIES> -o <TARGET>")
	set(CMAKE_C_LINK_EXECUTABLE "${LINK_EXECUTABLE} <CMAKE_C_LINK_FLAGS>")
	set(CMAKE_CXX_LINK_EXECUTABLE "${LINK_EXECUTABLE} <CMAKE_CXX_LINK_FLAGS>")

	# add to executables list
	set(EXECUTABLES ${EXECUTABLES} ${ELFFILE} CACHE INTERNAL STRING)
endmacro()
