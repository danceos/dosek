# Hardware dependent code
if(BUILD_i386)
	add_subdirectory(i386)
else()
	message(FATAL_ERROR "Hardware platform not found :(")
endif()

## Generic startup code
add_subdirectory(generic)

