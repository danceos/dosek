# Generic system
set(CMAKE_C_ARCH "i386")
set(CMAKE_C_FLAGS "-Wall -m32 -Wextra -Qunused-arguments -Wno-undefined-inline" CACHE STRING "CFLAGS")
set(CMAKE_CXX_FLAGS "${CMAKE_C_FLAGS} -fno-exceptions -fno-rtti" CACHE STRING "CXXFLAGS")
set(CMAKE_ASM_FLAGS "-Qunused-arguments" CACHE STRING "ASMFLAGS")
set(CMAKE_ASM-TT_FLAGS "-Qunused-arguments" CACHE STRING "ASMFLAGS")

set(CCDIR "/proj/i4danceos/tools/llvm-3.4")
set(CMAKE_C_COMPILER  ${CCDIR}/bin/clang)
set(CMAKE_CXX_COMPILER ${CCDIR}/bin/clang++)
set(CMAKE_CXX_COMPILER ${CCDIR}/bin/clang++)
set(CMAKE_RANLIB "${CCDIR}/bin/llvm-ranlib" CACHE INTERNAL STRING)
set(CMAKE_AR "${CCDIR}/bin/llvm-ar" CACHE INTERNAL STRING)

SET(CMAKE_FIND_ROOT_PATH ${CCDIR})
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

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



