cmake_minimum_required(VERSION 2.6.0)

PROJECT(CoRedOS)
enable_language(ASM)
set(PROJECT_VERSION "0.1" CACHE STRING "Project version number")

# Verbose make
option(VERBOSE_MAKE "Verbose Makefile output" OFF)
set(CMAKE_VERBOSE_MAKEFILE ${VERBOSE_MAKE})

set(ELFFILE "coredos.elf" CACHE INTERNAL STRING)

## Search path for custom cmake scripts
set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")
include(load_profile)


### Setup target architecture and platform ###
LOAD_PROFILE("x86" "failbochs")
##############################################

#	## setup compiler flags
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${ISA_C_FLAGS} -nostdlib -fno-builtin")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${ISA_CXX_FLAGS} ${CMAKE_C_FLAGS}  -fno-exceptions")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} ${ISA_ASM_FLAGS}")

## add further libraries
add_subdirectory(arch)
add_subdirectory(os)



# The actual executable
message(STATUS "Architecture sources: ${ARCH_SRCS}, Platform specifics: ${PLATFORM_SRCS}")
message(STATUS "Linker script: ${LINKER_SCRIPT}")

add_executable(${ELFFILE} ${PLATFORM_SRCS} ${ARCH_SRCS})
target_link_libraries(${ELFFILE} arch_generic os)

	set_target_properties(${ELFFILE} PROPERTIES LINK_FLAGS
			"-Wl,-T ${LINKER_SCRIPT} -Wl,-nostdlib ${ISA_LD_FLAGS} -nostdlib -ffreestanding" )


# Platform specific custom targets/commands. (must be included after add_executable!)
include(${ADDITINOAL_TARGETS})

