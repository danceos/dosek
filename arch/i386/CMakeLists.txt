# (Emulated) RAM size
set(RAM_SIZE "16" CACHE STRING "(Emulated) RAM size in MB")

# Debugger to use
find_program(DEBUGGER "gdb" DOC "Debugger (gdb/ddd)")

# (Random) port for debugging
string(RANDOM LENGTH 4 ALPHABET "123456789" DPORT)
set(DEBUG_PORT ${DPORT} CACHE STRING "Debug (stub) port")
message(STATUS "[${PROJECT_NAME}] Using port ${DEBUG_PORT} for debug stub")

# Enable emulators
OPTION(X86_TARGET_BOCHS "Bochs" ON)
OPTION(X86_TARGET_QEMU "QEMU" ON)

if(X86_TARGET_BOCHS OR X86_TARGET_QEMU)
	set(ADDITIONAL_TARGETS ${ADDITIONAL_TARGETS}
		${CMAKE_CURRENT_SOURCE_DIR}/grub CACHE INTERNAL STRING)
endif()
if(X86_TARGET_BOCHS)
	message(STATUS "Target i386 Bochs")
	set(ADDITIONAL_TARGETS ${ADDITIONAL_TARGETS}
		${CMAKE_CURRENT_SOURCE_DIR}/bochs CACHE INTERNAL STRING)
endif()
if(X86_TARGET_QEMU)
	message(STATUS "Target i386 QEMU")
	set(ADDITIONAL_TARGETS ${ADDITIONAL_TARGETS}
		${CMAKE_CURRENT_SOURCE_DIR}/qemu CACHE INTERNAL STRING)
endif()

# setup x86-32 specific sources
set(SRCS
	startup.cc
	startup.s
	cga.cc
	serial.cc
)

add_library(arch ${SRCS})
target_link_libraries(arch generic)

set(ARCH_INCLUDE_DIRS ${ARCH_INCLUDE_DIRS} ${CMAKE_CURRENT_SOURCE_DIR} CACHE INTERNAL STRING)
