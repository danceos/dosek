# (Emulated) RAM size
set(RAM_SIZE "8" CACHE STRING "(Emulated) RAM size in MB")

# Debugger to use
find_program(DEBUGGER "gdb" DOC "Debugger (gdb/ddd)")

# (Random) port for debugging
string(RANDOM LENGTH 4 ALPHABET "123456789" DPORT)
set(DEBUG_PORT ${DPORT} CACHE STRING "Debug (stub) port")
message(STATUS "[${PROJECT_NAME}] Using port ${DEBUG_PORT} for debug stub")

# Build option to disable MMU protection
option(dOSEK_MPU_PROTECTION "Use MPU protection" ON)
if(NOT dOSEK_MPU_PROTECTION)
	message(STATUS "[${PROJECT_NAME}] Disabling MPU protection")
	add_definitions(-DMPU_DISABLED)
endif()

# Enable emulators
OPTION(X86_TARGET_BOCHS "Bochs" ON)
OPTION(X86_TARGET_QEMU "QEMU" ON)

if(X86_TARGET_BOCHS OR X86_TARGET_QEMU)
	set(ADDITIONAL_TARGETS ${ADDITIONAL_TARGETS}
		${CMAKE_CURRENT_SOURCE_DIR}/grub CACHE INTERNAL STRING)
endif()
if(X86_TARGET_BOCHS)
	set(ADDITIONAL_TARGETS ${ADDITIONAL_TARGETS}
		${CMAKE_CURRENT_SOURCE_DIR}/bochs CACHE INTERNAL STRING)
endif()
if(X86_TARGET_QEMU)
	set(ADDITIONAL_TARGETS ${ADDITIONAL_TARGETS}
		${CMAKE_CURRENT_SOURCE_DIR}/qemu CACHE INTERNAL STRING)
endif()

# setup x86-32 specific sources
set(SRCS
	mp_startup.cc
	mp_startup.s
	mp.s
	constructors.cc
	startup.cc
	startup.s
	gdt.cc
	idt.cc
	idt.S
	paging.cc
	cga.cc
	serial.cc
	output.cc
	pic.cc
	lapic.cc
	ioapic.cc
	pit.cc
	dispatch.cc
	syscall.cc
	reschedule-ast.cc
    machine.cc
    memutil.cc
)

# Create arch library
add_library(arch ${SRCS})
target_link_libraries(arch generic)

# Add to include directories
dosek_include_dir(${CMAKE_CURRENT_SOURCE_DIR})
set(ARCH_INCLUDE_DIRS ${ARCH_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR} CACHE INTERNAL STRING)

# Set linker script template
set(LINKER_TEMPLATE ${CMAKE_CURRENT_SOURCE_DIR}/linker.ld.in CACHE INTERNAL STRING)

# Find objdump for pagetable generation
find_program(OBJDUMP "objdump")

# i386 dOSEK executable macro
# usage: dosek_executable(ELFFILE ... [DEFINTIONS ...])
# Creates dOSEK executable named ELFFILE. All parameters after ELFFILE until
# (optional) DEFINITIONS are passed directly to add_executable.
# To set compile definitions specify them after DEFINITIONS keyword.
macro(dosek_executable ELFFILE)
	# parse DEFINITIONS
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

	# First executable with empty, weak page tables
	set(PRELINK ${ELFNAME}.prelink.elf)
	add_executable(${PRELINK} ${ADD_EXECUTABLE_OPTIONS} ${SOURCES})
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
	add_executable(${ELFFILE} ${ADD_EXECUTABLE_OPTIONS} ${SOURCES} ${PAGETABLES})
	target_link_libraries(${ELFFILE} ${TARGET_LIBS})

	# set definitions
	if(DOSEK_EXECUTABLE_DEFINITIONS)
		set_target_properties(${ELFFILE} ${PRELINK} PROPERTIES COMPILE_DEFINITIONS ${DOSEK_EXECUTABLE_DEFINITIONS})
	endif()

	# Set custom linker script/flags
	# libgcc added here to be used as needed (compiler helper functions)and not included in full
	if(DOSEK_EXECUTABLE_LINKER_SCRIPT)
		set(LINKER_SCRIPT ${DOSEK_EXECUTABLE_LINKER_SCRIPT})
	else()
		set(LINKER_SCRIPT ${CMAKE_CURRENT_BINARY_DIR}/${ELFNAME}_linker.ld)
	endif()
	set_target_properties(${ELFFILE} ${PRELINK} PROPERTIES
		LINK_FLAGS "-lgcc -Wl,-T ${LINKER_SCRIPT} ${ISA_LD_FLAGS} --linker-prefix=${CMAKE_CURRENT_BINARY_DIR}/${ELFFILE}"
		LINK_DEPENDS ${LINKER_SCRIPT})

	# we use our own linker (python) script, that calls llvm-link, llc and the system linker
	# setting CMAKE_*_LINK_EXECUTABLE at this point in the CMake run seems a bit unusual, but works as intended
	set(LINK_EXECUTABLE "${PROJECT_SOURCE_DIR}/toolchain/llvm-link.py --clang ${CMAKE_C_COMPILER} --march x86 --mcpu ${CMAKE_C_ARCH} --llvm-dir ${CCDIR} <LINK_FLAGS> <OBJECTS> <LINK_LIBRARIES> -o <TARGET>")
	set(CMAKE_C_LINK_EXECUTABLE "${LINK_EXECUTABLE} <CMAKE_C_LINK_FLAGS>")
	set(CMAKE_CXX_LINK_EXECUTABLE "${LINK_EXECUTABLE} <CMAKE_CXX_LINK_FLAGS>")

	# add to executables list
	set(EXECUTABLES ${EXECUTABLES} ${ELFFILE} CACHE INTERNAL STRING)
endmacro()


macro(dosek_add_test FN)
    add_test(${FN} qemu-system-i386 -no-reboot  -machine pc,accel=tcg -m ${RAM_SIZE} -nographic -smp 2 -cdrom "${PROJECT_BINARY_DIR}/${FN}.iso")
    set_tests_properties(${FN} PROPERTIES PASS_REGULAR_EXPRESSION "SUCCESS.+ALL OK" FAIL_REGULAR_EXPRESSION "FAIL" TIMEOUT 20)
    add_dependencies( tests iso-${FN} )
endmacro()

