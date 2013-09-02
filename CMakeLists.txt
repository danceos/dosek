cmake_minimum_required(VERSION 2.6.0)
project(CoRedOS)
enable_language(ASM)

set(ELFFILE "coredos.elf" CACHE INTERNAL STRING)

## Search path for custom cmake scripts
set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")
include(load_profile)

	## setup compiler flags
	set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -m32 -nostdlib -fno-builtin")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${CMAKE_C_FLAGS} ")# -fno-exception")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -m32")


### Setup target architecture and platform ###
LOAD_PROFILE("x86" "failbochs")
##############################################

