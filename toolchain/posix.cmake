set(CMAKE_C_ARCH "i386")
set(CMAKE_C_FLAGS "-Wall -m32 -Wextra -Qunused-arguments -Wno-undefined-inline" CACHE STRING "CFLAGS")
set(CMAKE_CXX_FLAGS "${CMAKE_C_FLAGS} -fno-exceptions -fno-rtti" CACHE STRING "CXXFLAGS")
set(CMAKE_ASM_FLAGS "-Qunused-arguments" CACHE STRING "ASMFLAGS")
set(CMAKE_ASM-TT_FLAGS "-Qunused-arguments" CACHE STRING "ASMFLAGS")

# Setup LLVM Tooling
SET(LLVM_RECOMMENDED_VERSION 3.4)

if(NOT DEFINED ${LLVM_ROOT})
  # find llvm-config. prefers to the one with version suffix, Ex:llvm-config-3.4
  find_program(LLVM_CONFIG_EXE NAMES "llvm-config-${LLVM_RECOMMENDED_VERSION}" "llvm-config")

  # Get the directory of llvm by using llvm-config. also remove whitespaces.
  execute_process(COMMAND ${LLVM_CONFIG_EXE} --prefix OUTPUT_VARIABLE LLVM_ROOT
                 OUTPUT_STRIP_TRAILING_WHITESPACE )
endif()

message(STATUS "LLVM root: ${LLVM_ROOT}")

# Find a compiler which compiles c++ source into llvm bitcode.
# It first finds clang, then it finds llvm-g++ if there is no clang.
find_program(LLVM_C_COMPILER "clang-${LLVM_RECOMMENDED_VERSION}"
                NAMES clang llvm-gcc
                HINTS ${LLVM_ROOT}/bin )

find_program(LLVM_CXX_COMPILER "clang++-${LLVM_RECOMMENDED_VERSION}"
                NAMES clang++ llvm-g++
                HINTS ${LLVM_ROOT}/bin )


# Checks whether a LLVM_COMPILER is found, give a warning if not found.
# A warning instread of error is beceuse that we don't need clang during
# building pinavm.
if(${LLVM_C_COMPILER} STREQUAL "LLVM_COMPILER-NOTFOUND")
  message(WARNING "Could not find clang or llvm-gcc."
                " Please install one of them !")
endif()

message(STATUS "LLVM C/C++ compiler: ${LLVM_C_COMPILER} ${LLVM_CXX_COMPILER}")


set(CCDIR "${LLVM_ROOT}")
set(CMAKE_C_COMPILER  ${LLVM_C_COMPILER})
set(CMAKE_CXX_COMPILER ${LLVM_CXX_COMPILER})
set(CMAKE_RANLIB "${CCDIR}/bin/llvm-ranlib" CACHE INTERNAL STRING)
set(CMAKE_AR "${CCDIR}/bin/llvm-ar" CACHE INTERNAL STRING)

SET(CMAKE_FIND_ROOT_PATH ${CCDIR})
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

#set(CCDIR "/proj/i4danceos/tools/llvm-3.4")
#set(CMAKE_C_COMPILER  ${CCDIR}/bin/clang)
#set(CMAKE_CXX_COMPILER ${CCDIR}/bin/clang++)
#set(CMAKE_CXX_COMPILER ${CCDIR}/bin/clang++)
#set(CMAKE_RANLIB "${CCDIR}/bin/llvm-ranlib" CACHE INTERNAL STRING)
#set(CMAKE_AR "${CCDIR}/bin/llvm-ar" CACHE INTERNAL STRING)
#
#SET(CMAKE_FIND_ROOT_PATH ${CCDIR})
#SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
#SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
#SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

## Add *additional* architecture specific compiler flags here.
# Note that the flags set in toolchain.cmake are still present and used.
set(ISA_C_FLAGS "-c -emit-llvm" CACHE INTERNAL STRING)
set(ISA_CXX_FLAGS "-stdlib=libc++" CACHE INTERNAL STRING)
set(ISA_ASM-ATT_FLAGS "--32" CACHE INTERNAL STRING)
set(ISA_ASM_FLAGS "-m32" CACHE INTERNAL STRING)
set(ISA_LD_FLAGS "-m32 -Qunused-arguments" CACHE INTERNAL STRING)

set(LD_OUTPUT_FORMAT "elf32-i386" CACHE INTERNAL "LD output format for linker script")

## The kernel will live at 3GB + 1MB in the virtual
##   address space, which will be mapped to 1MB in the
##   physical address space.
#set(LD_KERNEL_START_ADDRESS 0x100000 CACHE INTERNAL "Start address of the first section.")

# ENABLE posix platform
set(BUILD_posix "on" CACHE INTERNAL STRING)
set(DOSEK_ARCHITECTURE "posix")



