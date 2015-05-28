cmake_minimum_required(VERSION 2.6.2)

PROJECT(dOSEK)

# ASM language defaults to the clang assembler in the Bellolabs.
# It is required since arch/i386/idt.S uses macros that do not
# work with gnu assembler without any changes.
enable_language(ASM)

# ASM-ATT language defaults to gnu assembler. It only matches
# assembler files with a lower case ".s" as file extension.
# Upper case "*.S" is still matched by the ASM language and is
# therefore compiled with clang.
enable_language(ASM-ATT)

enable_testing()
set(PROJECT_VERSION "1.1" CACHE STRING "Project version number")
set(PROJECT_RELEASE "stable" CACHE STRING "Project release")

# Enable CTest
enable_testing()

# Set DEBUG flag when debugging
OPTION(DEBUGGING "Debug mode" OFF)
if(DEBUGGING)
	message(STATUS "[${PROJECT_NAME}] Enabling debug mode")
	add_definitions(-DDEBUG=1)
endif()

include(${CMAKE_CURRENT_BINARY_DIR}/config.cmake)


list(REMOVE_DUPLICATES GENERATOR_ARGS)

if(GENERATOR_ARGS)
	message(STATUS "[${PROJECT_NAME}] Additional Generator Arguments: ${GENERATOR_ARGS}")
    string (REPLACE ";" " " _TMP_STR "${GENERATOR_ARGS}")
    add_definitions(-DGENERATOR_ARGS="${_TMP_STR}")
else()
  add_definitions(-DGENERATOR_ARGS="")
  set(GENERATOR_ARGS "" CACHE STRING "")
endif()

option(FAIL_TRACE_ALL "Trace all binaries" OFF)
if(FAIL_TRACE_ALL)
	message(STATUS "[${PROJECT_NAME}] Fail Trace All: ON")
else()
	message(STATUS "[${PROJECT_NAME}] Fail Trace All: OFF")
endif()

# Verbose make
option(VERBOSE_MAKE "Verbose Makefile output" OFF)
set(CMAKE_VERBOSE_MAKEFILE ${VERBOSE_MAKE})

set(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR})

# Search path for custom cmake scripts
set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/toolchain")

## Setup platform independent compiler flags
# ffunction/data-sections needed to link functions/data into different sections based on name(space)
# fno-zero-initialized-in-bss puts all variables into data instead of bss section (for data-section grouping)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${ISA_C_FLAGS} -ffunction-sections -fdata-sections -fno-zero-initialized-in-bss -nostdlib -fno-builtin")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${ISA_CXX_FLAGS} ${CMAKE_C_FLAGS}  -fno-exceptions -std=c++11")
set(CMAKE_ASM-ATT_FLAGS "${CMAKE_ASM-ATT_FLAGS} ${ISA_ASM-ATT_FLAGS}")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} ${ISA_ASM_FLAGS}")

# Find python
find_program(PYTHON "python")
if(NOT PYTHON)
	message(ERROR "[${PROJECT_NAME}] Python not found!")
endif()

# Variable for additional targets
set(ADDITIONAL_TARGETS "" CACHE INTERNAL STRING)

include(helpers)

# Include source directory
dosek_include_dir(${PROJECT_SOURCE_DIR})
dosek_include_dir(${PROJECT_SOURCE_DIR}/os)
dosek_include_dir(${PROJECT_BINARY_DIR})
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -include ${PROJECT_BINARY_DIR}/dosek_config.h")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -include ${PROJECT_BINARY_DIR}/dosek_config.h")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -include ${PROJECT_BINARY_DIR}/dosek_config.h")




list(REMOVE_DUPLICATES GENERATOR_ARGS)


# Documentation
add_subdirectory(toolchain/doxygen)

# List of executables
set(EXECUTABLES "" CACHE INTERNAL "List of executables")

# Hardware dependent code
set(ARCH_INCLUDE_DIRS "" CACHE INTERNAL "Hardware dependent include directories")
add_subdirectory(arch)
foreach(ARCH_INCLUDE_DIR ${ARCH_INCLUDE_DIRS})
	dosek_include_dir(${ARCH_INCLUDE_DIR})
endforeach()

# Tests
add_subdirectory(test)

# FAIL* targets
add_subdirectory(fail)

# Hardware independent kernel code
add_subdirectory(os)
add_subdirectory(dependability)
add_subdirectory(generator)
add_subdirectory(config)
add_subdirectory(app)

# Platform specific custom targets/commands.
# Must be included after add_executable, as they depend on the main target.
foreach(TARGETS ${ADDITIONAL_TARGETS})
	message(STATUS "[${PROJECT_NAME}] Preparing addtional targets: ${TARGETS}")
	add_subdirectory(${TARGETS})
endforeach()

set(APPTARGETSTRING "")
set(APPTARGETS_LOCAL ${APPTARGETS}) # Copy CACHE list to local variable
set(APPTARGETS "" CACHE INTERNAL "application targets") # clear CACHE variable to prevent aggregation due to multiple cmake calls
foreach(TARGET ${APPTARGETS_LOCAL})
    set(APPTARGETSTRING "${TARGET}\t\t${APPTARGETSTRING}")
endforeach()
add_custom_target(h
    COMMENT "Target overview:
    * make build_and_test -> Build *all* test cases and run ctest on them
    * make <appname> -> e.g., make bcc1_task1a (re-)build application
    * make qtest-<appname> -> Build iso from app and run qemu (default RAM size: 8 MB! [-m 8])
    * make iso-<appname> -> Generate bootable iso
available targets:
${APPTARGETSTRING}"
)


# Static analysis (oclint/clang-static-analyzer
# Find all sources for code cccc metrics.
file(GLOB_RECURSE ALLSRCS RELATIVE ${PROJECT_SOURCE_DIR} *.cc *.h )
set(CCCC_SOURCES ${ALLSRCS} CACHE INTERNAL STRING)

add_subdirectory(static_analysis)
