# Prepare cross compiler
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_C_ARCH "riscv")
set(ARCH_PREFIX "riscv64-unknown-elf-")

find_program(CROSS_GCC "${ARCH_PREFIX}gcc")

# gcc -print-search-dirs first line: install: ...
execute_process(COMMAND ${CROSS_GCC} -print-search-dirs OUTPUT_VARIABLE GCC_SEARCH_PATH OUTPUT_STRIP_TRAILING_WHITESPACE)
STRING(REGEX REPLACE "^install: ([^ ]+)\n.*" "\\1" CROSS_ROOT_PATH ${GCC_SEARCH_PATH})

find_program(CROSS_AR "${ARCH_PREFIX}ar")
find_program(CROSS_AS "${ARCH_PREFIX}as")
find_program(CROSS_NM "${ARCH_PREFIX}nm")
find_program(CROSS_RANLIB "${ARCH_PREFIX}ranlib")
# Find objdump for pagetable generation
find_program(CROSS_OBJDUMP "${ARCH_PREFIX}objdump")
find_program(CROSS_OBJCOPY "${ARCH_PREFIX}objcopy")


message(STATUS "Cross compiler root: ${CROSS_ROOT_PATH}")

# Setup LLVM Tooling
SET(LLVM_RECOMMENDED_VERSION 3.4)

SET(LLVM_ROOT "/srv/scratch/qy03fugy/riscv/tools" CACHE STRING "LLVM Root")

if(NOT DEFINED LLVM_ROOT)
  # find llvm-config. prefers to the one with version suffix, Ex:llvm-config-3.4
  find_program(LLVM_CONFIG_EXE NAMES "llvm-config-${LLVM_RECOMMENDED_VERSION}" "llvm-config")

  # Get the directory of llvm by using llvm-config. also remove whitespaces.
  execute_process(COMMAND ${LLVM_CONFIG_EXE} --prefix OUTPUT_VARIABLE LLVM_ROOT
    OUTPUT_STRIP_TRAILING_WHITESPACE )
else()
  find_program(LLVM_CONFIG_EXE NAMES  "llvm-config" "llvm-config-${LLVM_RECOMMENDED_VERSION}" 
    HINTS ${LLVM_ROOT}/bin)
endif()

message(STATUS "LLVM root: ${LLVM_ROOT}")

# Find a compiler which compiles c++ source into llvm bitcode.
# It first finds clang, then it finds llvm-g++ if there is no clang.
find_program(LLVM_C_COMPILER "clang-${LLVM_RECOMMENDED_VERSION}"
                NAMES clang llvm-gcc
                PATHS ${LLVM_ROOT}/bin NO_DEFAULT_PATH)

find_program(LLVM_CXX_COMPILER "clang++-${LLVM_RECOMMENDED_VERSION}"
                NAMES clang++ llvm-g++
                PATHS ${LLVM_ROOT}/bin NO_DEFAULT_PATH)


# Checks whether a LLVM_COMPILER is found, give a warning if not found.
# A warning instread of error is beceuse that we don't need clang during
# building pinavm.
if(${LLVM_C_COMPILER} STREQUAL "LLVM_COMPILER-NOTFOUND")
  message(WARNING "Could not find clang or llvm-gcc."
                " Please install one of them !")
endif()

message(STATUS "LLVM C/C++ compiler: ${LLVM_C_COMPILER} ${LLVM_CXX_COMPILER}")


# Setup ARM specific flags
set(COMMON_RISCV_FLAGS "-target ${CMAKE_C_ARCH} -Wa,-march=RV64IAMD -Xclang -no-implicit-float -ccc-gcc-name ${ARCH_PREFIX}gcc -no-integrated-as ")
set(CMAKE_C_FLAGS "${COMMON_RISCV_FLAGS} -ffreestanding -Wall -Wextra -Qunused-arguments -Wno-undefined-inline -O0" CACHE STRING "CFLAGS")
set(CMAKE_CXX_FLAGS " -fno-exceptions -fno-unwind-tables -fno-rtti" CACHE STRING "CXXFLAGS")
set(CMAKE_ASM_COMPILE_OBJECT "<CMAKE_ASM_COMPILER> -march=RV64IAMD  -I ${PROJECT_SOURCE_DIR}/arch/osek-v -o <OBJECT> <SOURCE>")

set(CMAKE_EXE_LINKER_FLAGS "-nostartfiles" CACHE STRING "LDFLAGS")

# Setup compilers
set(CCDIR "${LLVM_ROOT}")
set(CMAKE_C_COMPILER  ${LLVM_C_COMPILER})
set(CMAKE_ASM_COMPILER  ${CROSS_AS})

set(CMAKE_CXX_COMPILER ${LLVM_CXX_COMPILER})
set(CMAKE_RANLIB "${CROSS_RANLIB}" CACHE INTERNAL STRING)
set(CMAKE_AR "${CROSS_AR}" CACHE INTERNAL STRING)

SET(CMAKE_FIND_ROOT_PATH ${CROSS_ROOT_PATH})
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

## Add *additional* architecture specific compiler flags here.
# Note that the flags set in toolchain.cmake are still present and used.
set(ISA_C_FLAGS "-S -emit-llvm -O0" CACHE INTERNAL STRING)
set(ISA_CXX_FLAGS "" CACHE INTERNAL STRING)
set(ISA_ASM_FLAGS "" CACHE INTERNAL STRING)
set(ISA_LD_FLAGS "${COMMON_RISCV_FLAGS} -static -nostdlib -Qunused-arguments -Wl,--build-id=none" CACHE INTERNAL STRING)

set(DOSEK_ARCHITECTURE "osek-v")

