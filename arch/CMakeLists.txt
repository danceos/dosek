## Setup platform independent compiler flags
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${ISA_C_FLAGS} -ffunction-sections -nostdlib -fno-builtin")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${ISA_CXX_FLAGS} ${CMAKE_C_FLAGS}  -fno-exceptions")
set(CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} ${ISA_ASM_FLAGS}")
message(STATUS "ISA_ASM_FLAGS: ${ISA_ASM_FLAGS}")

# Hardware dependent code
if(BUILD_i386)
	add_subdirectory(i386)
else()
	message(FATAL_ERROR "Hardware platform not found :(")
endif()

## Generic startup code
add_subdirectory(generic)

# Platform specific custom targets/commands.
# Must be included after add_executable, as they depend on the main target.
if(ADDITIONAL_TARGETS)
	message(STATUS "Preparing addtional targets: ${ADDITIONAL_TARGETS}")
	add_subdirectory(${ADDITIONAL_TARGETS})
else()
	message(STATUS "No additional targets found.")
endif()

