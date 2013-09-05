cmake_minimum_required(VERSION 2.6.0)

PROJECT(CoRedOS)
enable_language(ASM)
set(PROJECT_VERSION "0.1" CACHE STRING "Project version number")

# Verbose make
option(VERBOSE_MAKE "Verbose Makefile output" OFF)
set(CMAKE_VERBOSE_MAKEFILE ${VERBOSE_MAKE})

# Binary filename
set(ELFFILE "coredos.elf" CACHE INTERNAL STRING)

set(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR})

# Search path for custom cmake scripts
set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")

## Setup platform independent compiler flags
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${ISA_C_FLAGS} -ffunction-sections -nostdlib -fno-builtin")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${ISA_CXX_FLAGS} ${CMAKE_C_FLAGS}  -fno-exceptions -std=c++11")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} ${ISA_ASM_FLAGS}")
message(STATUS "ISA_ASM_FLAGS: ${ISA_ASM_FLAGS}")

# Hardware independent kernel code
add_subdirectory(os)

# Hardware dependent code
add_subdirectory(arch)


