FUNCTION(LOAD_PROFILE ARCH PLATFORM)
	# Obtain sources
	set(ARCHPATH "${PROJECT_SOURCE_DIR}/arch/${ARCH}")
	file(GLOB ARCH_SRCS "${ARCHPATH}/*.cc" "${ARCHPATH}/*.s")
	file(GLOB PLATFORM_SRCS "${ARCHPATH}/${PLATFORM}/*.cc")

	# Load platform specific custom targets, if present

	# Load flags
	include("${ARCHPATH}/cmake/flags.cmake")

	# Now export our output variables
	set(PLATFORM_LAYOUT "${ARCHPATH}/${PLATFORM}/layout.ld" PARENT_SCOPE)
	set(ARCH_SRCS "${ARCH_SRCS}" PARENT_SCOPE)
	set(PLATFORM_SRCS "${PLATFORM_SRCS}" PARENT_SCOPE)


  # Platform specific custom targets/commands.
	set(ADDITINOAL_TARGETS ${ARCHPATH}/${PLATFORM}/targets.cmake PARENT_SCOPE)
ENDFUNCTION(LOAD_PROFILE)
