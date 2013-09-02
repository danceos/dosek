# Generic system
# removes -rdynamic from the linker, which llvm-ld does not support.
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_C_FLAGS "-ffreestanding -O2 -Wall -Wextra -fno-exceptions -fno-rtti" CACHE STRING "CFLAGS")
set(CMAKE_CXX_FLAGS "-ffreestanding -O2 -Wall -Wextra -fno-exceptions -fno-rtti" CACHE STRING "CFLAGS")
set(CMAKE_EXE_LINKER_FLAGS -nostartfiles CACHE STRING "LDFLAGS")

# Disable compiler checks
include(CMakeForceCompiler)

set(CCDIR "/proj/i4ezs/tools/gnutools/i386-elf")
set(CMAKE_C_COMPILER  ${CCDIR}/bin/gcc)
#CMAKE_FORCE_C_COMPILER(${CCDIR}/bin/i386-elf-gcc GNU)
set(CMAKE_CXX_COMPILER ${CCDIR}/bin/g++)
#CMAKE_FORCE_CXX_COMPILER(${CCDIR}/bin/i386-elf-g++ GNU)
set(CMAKE_RANLIB ${CCDIR}/bin/ranlib)
set(CMAKE_AR ${CCDIR}/bin/ar)
set(CMAKE_LINKER ${CCDIR}/bin/ld)


#set(CMAKE_C_COMPILER clang)
#set(CMAKE_CXX_COMPILER clang++)
#set(CMAKE_RANLIB "llvm-ranlib" CACHE INTERNAL STRING)
#set(CMAKE_AR "llvm-ar" CACHE INTERNAL STRING)
#set(CMAKE_LINKER "llvm-ld" CACHE INTERNAL STRING)

#SET(CMAKE_C_LINK_EXECUTABLE "llvm-ld <OBJECTS> -o  <TARGET> <CMAKE_C_LINK_FLAGS> <LINK_FLAGS> <LINK_LIBRARIES>")
#SET(CMAKE_CXX_LINK_EXECUTABLE "llvm-ld <OBJECTS> -o  <TARGET> <CMAKE_CXX_LINK_FLAGS> <LINK_FLAGS> <LINK_LIBRARIES>")

SET(CMAKE_FIND_ROOT_PATH ${CCDIR})
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
