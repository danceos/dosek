# Generic system
# removes -rdynamic from the linker, which llvm-ld does not support.
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_C_FLAGS "-march=i386 -ffreestanding  -m32 -Wall -Wextra" CACHE STRING "CFLAGS")
set(CMAKE_CXX_FLAGS "${CMAKE_C_FLAGS} -fno-exceptions -fno-rtti" CACHE STRING "CXXFLAGS")

set(CMAKE_EXE_LINKER_FLAGS  "-nostartfiles" CACHE STRING "LDFLAGS")

set(CCDIR "/proj/i4danceos/tools/llvm-3.4")
set(CMAKE_C_COMPILER  ${CCDIR}/bin/clang)
set(CMAKE_CXX_COMPILER ${CCDIR}/bin/clang++)

SET(CMAKE_FIND_ROOT_PATH ${CCDIR})
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

## Add *additional* architecture specific compiler flags here.
# Note that the flags set in toolchain.cmake are still present and used.
set(ISA_C_FLAGS "" CACHE INTERNAL STRING)
set(ISA_CXX_FLAGS "" CACHE INTERNAL STRING)
set(ISA_ASM_FLAGS "-m32" CACHE INTERNAL STRING)
set(ISA_LD_FLAGS "" CACHE INTERNAL STRING)


set(LD_OUTPUT_FORMAT "elf32-i386" CACHE INTERNAL "LD output format for linker script")

## The kernel will live at 3GB + 1MB in the virtual
##   address space, which will be mapped to 1MB in the
##   physical address space.
set(LD_KERNEL_START_ADDRESS 0x100000 CACHE INTERNAL "Start address of the first section.")

# ENABLE x86 32 platform
set(BUILD_i386 "on" CACHE INTERNAL STRING)

