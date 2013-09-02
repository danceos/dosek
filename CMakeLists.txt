cmake_minimum_required(VERSION 2.6.0)
project(CoRedOS)
enable_language(ASM)

set(ELFFILE "coredos.elf" CACHE INTERNAL STRING)

## Search path for custom cmake scripts
set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake")
include(load_profile)

### Setup target architecture and platform ###
LOAD_PROFILE("x86" "failbochs")
##############################################

