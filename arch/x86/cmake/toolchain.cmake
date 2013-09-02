# Generic system
# removes -rdynamic from the linker, which llvm-ld does not support.
set(CMAKE_SYSTEM_NAME Generic)

# Disable compiler checks
include(CMakeForceCompiler)

set(CCDIR "/proj/i4ezs/tools/gnutools/")
set(CMAKE_C_COMPILER  ${CCDIR}/bin/i386-elf-gcc)
set(CMAKE_CXX_COMPILER ${CCDIR}/bin/i386-elf-g++)
set(CMAKE_RANLIB ${CCDIR}/bin/i386-elf-ranlib)
set(CMAKE_AR ${CCDIR}/bin/i386-elf-ar)
set(CMAKE_LINKER ${CCDIR}/bin/i386-elf-ld)


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
