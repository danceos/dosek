cmake_minimum_required(VERSION 2.6.2)

PROJECT(CoRedOS)
enable_language(ASM)
enable_testing()
set(PROJECT_VERSION "0.1" CACHE STRING "Project version number")

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
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${ISA_C_FLAGS} -ffunction-sections -nostdlib -fno-builtin")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${ISA_CXX_FLAGS} ${CMAKE_C_FLAGS}  -fno-exceptions -std=c++11")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} ${ISA_ASM_FLAGS}")
message(STATUS "ISA_ASM_FLAGS: ${ISA_ASM_FLAGS}")

include(helpers)

# Include source directory
coredos_include_dir(${PROJECT_SOURCE_DIR})

# Tests
add_subdirectory(test)

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
if(ADDITIONAL_TARGETS)
	message(STATUS "Preparing addtional targets: ${ADDITIONAL_TARGETS}")
	add_subdirectory(${ADDITIONAL_TARGETS})
else()
	message(STATUS "No additional targets found.")
endif()

# Static analysis (oclint/clang-static-analyzer
# Find all sources for code cccc metrics.
file(GLOB_RECURSE ALLSRCS RELATIVE ${PROJECT_SOURCE_DIR} *.cc *.h )
set(CCCC_SOURCES ${ALLSRCS} CACHE INTERNAL STRING)

add_subdirectory(static_analysis)
