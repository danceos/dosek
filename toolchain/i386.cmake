# Generic system
# removes -rdynamic from the linker, which llvm-ld does not support.
set(CMAKE_SYSTEM_NAME Generic)

# LLVM version.
SET(LLVM_RECOMMENDED_VERSION 3.4)

if(NOT DEFINED ${LLVM_ROOT})
  # find llvm-config. prefers to the one with version suffix, Ex:llvm-config-3.4
    # find llvm-config. prefers to the one with version suffix, Ex:llvm-config-3.4
  find_program(LLVM_CONFIG_EXE NAMES "llvm-config-${LLVM_RECOMMENDED_VERSION}"
    PATHS /proj/i4danceos/tools/llvm-${LLVM_RECOMMENDED_VERSION}/bin)
  if (NOT LLVM_CONFIG_EXE)
    find_program(LLVM_CONFIG_EXE NAMES "llvm-config"
      PATHS /proj/i4danceos/tools/llvm-${LLVM_RECOMMENDED_VERSION}/bin)
  endif()

  # Get the directory of llvm by using llvm-config. also remove whitespaces.
  execute_process(COMMAND ${LLVM_CONFIG_EXE} --prefix OUTPUT_VARIABLE LLVM_ROOT
    OUTPUT_STRIP_TRAILING_WHITESPACE )
endif()

message(STATUS "LLVM root: ${LLVM_ROOT}")

# Find a compiler which compiles c source into llvm bitcode.
# It first finds clang, then it finds llvm-g++ if there is no clang.
find_program(LLVM_C_COMPILER "clang-${LLVM_RECOMMENDED_VERSION}"
                NAMES clang
                HINTS ${LLVM_ROOT}/bin )
# Find a compiler which compiles c++ source into llvm bitcode.
# It first finds clang, then it finds llvm-g++ if there is no clang.
find_program(LLVM_CXX_COMPILER "clang++-${LLVM_RECOMMENDED_VERSION}"
                NAMES clang++
                HINTS ${LLVM_ROOT}/bin )


# Checks whether a LLVM_COMPILER is found, give a warning if not found.
# A warning instread of error is beceuse that we don't need clang during
# building pinavm.
if(${LLVM_C_COMPILER} STREQUAL "LLVM_C_COMPILER-NOTFOUND")
  message(FATAL "Could not find clang or llvm-g++."
                " Please install one of them !")
endif()

message(STATUS "LLVM compiler: ${LLVM_C_COMPILER}")


if (${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Darwin")
  set(ARCH_PREFIX "i386-elf-")
  find_program(CROSS_GCC "${ARCH_PREFIX}gcc")
  # gcc -print-search-dirs first line: install: ...
  execute_process(COMMAND ${CROSS_GCC} -print-search-dirs OUTPUT_VARIABLE GCC_SEARCH_PATH OUTPUT_STRIP_TRAILING_WHITESPACE)
  message(status "search dirs: ${GCC_SEARCH_PATH}")
  STRING(REGEX REPLACE "^install: ([^ ]+)\n.*" "\\1" CROSS_ROOT_PATH ${GCC_SEARCH_PATH})

  find_program(CROSS_AR "${ARCH_PREFIX}ar")
  find_program(CROSS_NM "${ARCH_PREFIX}nm")
  find_program(CROSS_RANLIB "${ARCH_PREFIX}ranlib")
  # Find objdump for pagetable generation
  find_program(CROSS_OBJDUMP "${ARCH_PREFIX}objdump")

  set(CROSS_COMPILER_FLAGS "-ccc-gcc-name ${ARCH_PREFIX}gcc -target i386-pc-none")

  set(CMAKE_ASM_COMPILER ${ARCH_PREFIX}gcc)

  message(STATUS "Cross compiler root: ${CROSS_ROOT_PATH}")
elseif(${CMAKE_HOST_SYSTEM_NAME} STREQUAL "Linux")
  set(CROSS_RANLIB ${LLVM_ROOT}/bin/llvm-ranlib)
  set(CROSS_AR ${LLVM_ROOT}/bin/llvm-ar)
  find_program(CROSS_OBJDUMP objdump)
  find_program(CROSS_NM "${ARCH_PREFIX}nm" "nm")
else()
  message(FATAL "Host system not found :(")
endif()

set(CMAKE_C_ARCH "i386")
set(CMAKE_C_FLAGS  "${CROSS_COMPILER_FLAGS} -ffreestanding -march=${CMAKE_C_ARCH} -m32 -Wall -Wextra -Qunused-arguments -Wno-undefined-inline" CACHE STRING "CFLAGS")
set(CMAKE_CXX_FLAGS "${CMAKE_C_FLAGS} -fno-exceptions -fno-rtti" CACHE STRING "CXXFLAGS")
set(CMAKE_ASM_FLAGS "-Qunused-arguments -fno-builtin " CACHE STRING "ASMFLAGS")
set(CMAKE_ASM-ATT_FLAGS "-Qunused-arguments" CACHE STRING "ASMFLAGS")
set(CMAKE_EXE_LINKER_FLAGS "-nostartfiles ${CMAKE_CXX_FLAGS}" CACHE STRING "LDFLAGS")

set(CCDIR "${LLVM_ROOT}")
set(CMAKE_C_COMPILER  ${LLVM_C_COMPILER})
set(CMAKE_CXX_COMPILER ${LLVM_CXX_COMPILER})
set(CMAKE_RANLIB "${CROSS_RANLIB}" CACHE INTERNAL STRING)
set(CMAKE_AR "${CROSS_AR}" CACHE INTERNAL STRING)

SET(CMAKE_FIND_ROOT_PATH ${CROSS_ROOT_PATH})
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

## Add *additional* architecture specific compiler flags here.
# Note that the flags set in toolchain.cmake are still present and used.
set(ISA_C_FLAGS "-S -emit-llvm -O0 -m32" CACHE INTERNAL STRING)
set(ISA_CXX_FLAGS "-m32" CACHE INTERNAL STRING)
set(ISA_ASM_FLAGS "-m32" CACHE INTERNAL STRING)
set(ISA_ASM-ATT_FLAGS "--32" CACHE INTERNAL STRING)
set(ISA_LD_FLAGS "-fno-builtin -m32 -static -nostdlib -Qunused-arguments -Wl,--build-id=none" CACHE INTERNAL STRING)

set(LD_OUTPUT_FORMAT "elf32-i386" CACHE INTERNAL "LD output format for linker script")

## The kernel will live at 3GB + 1MB in the virtual
##   address space, which will be mapped to 1MB in the
##   physical address space.
set(LD_KERNEL_START_ADDRESS 0x100000 CACHE INTERNAL "Start address of the first section.")

# ENABLE x86 32 platform
set(BUILD_i386 "on" CACHE INTERNAL STRING)
set(DOSEK_ARCHITECTURE "i386")

