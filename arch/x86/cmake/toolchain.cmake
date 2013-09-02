# Generic system
# removes -rdynamic from the linker, which llvm-ld does not support.
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_C_FLAGS "-ffreestanding -m32 -fno-builtin -Wall -Wextra" CACHE STRING "CFLAGS")
set(CMAKE_CXX_FLAGS "${CMAKE_C_FLAGS} -fno-exception -fno-rtti" CACHE STRING "CXXFLAGS")

set(CMAKE_EXE_LINKER_FLAGS  "-nostartfiles" CACHE STRING "LDFLAGS")

set(CCDIR "/proj/i4danceos/tools/llvm-3.4")
set(CMAKE_C_COMPILER  ${CCDIR}/bin/clang)
set(CMAKE_CXX_COMPILER ${CCDIR}/bin/clang++)

SET(CMAKE_FIND_ROOT_PATH ${CCDIR})
SET(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
SET(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
SET(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
