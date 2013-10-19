cmake_minimum_required(VERSION 2.6.2)

PROJECT(CoRedOS)
enable_language(ASM)
enable_testing()
set(PROJECT_VERSION "0.1" CACHE STRING "Project version number")
set(PROJECT_RELEASE "alpha" CACHE STRING "Project release")

# Enable CTest
enable_testing()

# Verbose make
option(VERBOSE_MAKE "Verbose Makefile output" OFF)
set(CMAKE_VERBOSE_MAKEFILE ${VERBOSE_MAKE})

# Binary filename
set(ELFFILE "coredos.elf" CACHE INTERNAL STRING)

set(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR})

# Search path for custom cmake scripts
set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/toolchain")

## Setup platform independent compiler flags
# ffunction/data-sections needed to link functions/data into different sections based on name(space)
# fno-zero-initialized-in-bss puts all variables into data instead of bss section (for data-section grouping)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${ISA_C_FLAGS} -ffunction-sections -fdata-sections -fno-zero-initialized-in-bss -nostdlib -fno-builtin")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${ISA_CXX_FLAGS} ${CMAKE_C_FLAGS}  -fno-exceptions -std=c++11")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} ${ISA_ASM_FLAGS}")
message(STATUS "[${PROJECT_NAME}] Assembler flags: ${ISA_ASM_FLAGS}")

# Find python
find_program(PYTHON "python")
if(NOT PYTHON)
	message(ERROR "[${PROJECT_NAME}] Python not found!")
endif()

# Variable for additional targets
set(ADDITIONAL_TARGETS "" CACHE INTERNAL STRING)

include(helpers)

# Include source directory
coredos_include_dir(${PROJECT_SOURCE_DIR})

# Tests
add_subdirectory(test)

# Documentation
add_subdirectory(doc)

# List of executables
set(EXECUTABLES "" CACHE INTERNAL "List of executables")

# Hardware dependent code
set(ARCH_INCLUDE_DIRS "" CACHE INTERNAL "Hardware dependent include directories")
add_subdirectory(arch)
coredos_include_dir(${ARCH_INCLUDE_DIRS})

# Hardware independent kernel code
coredos_include_dir("${PROJECT_SOURCE_DIR}/os")
add_subdirectory(os)

# Platform specific custom targets/commands.
# Must be included after add_executable, as they depend on the main target.
foreach(TARGETS ${ADDITIONAL_TARGETS})
	message(STATUS "[${PROJECT_NAME}] Preparing addtional targets: ${TARGETS}")
	add_subdirectory(${TARGETS})
endforeach()

# Static analysis (oclint/clang-static-analyzer
# Find all sources for code cccc metrics.
file(GLOB_RECURSE ALLSRCS RELATIVE ${PROJECT_SOURCE_DIR} *.cc *.h )
set(CCCC_SOURCES ${ALLSRCS} CACHE INTERNAL STRING)

add_subdirectory(static_analysis)
add_subdirectory(generator)
add_subdirectory(app)
