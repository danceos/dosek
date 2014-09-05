# Hardware dependent code
if(BUILD_i386)
	add_subdirectory(i386)
elseif(BUILD_ARM)
	add_subdirectory(arm)
elseif(BUILD_posix)
	add_subdirectory(posix)
else()
	message(FATAL_ERROR "Hardware platform not found :(")
endif()

## Generic startup code
add_subdirectory(generic)

