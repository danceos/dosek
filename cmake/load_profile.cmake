FUNCTION(LOAD_PROFILE ARCH PLATFORM)
	# Obtain sources
	set(ARCHPATH "${PROJECT_SOURCE_DIR}/arch/${ARCH}")
	set(ARCH_SRCS "${ARCHPATH}/startup.cc" "${ARCHPATH}/startup.s")

	# Load platform specific custom targets, if present

	# Load flags
	include("${ARCHPATH}/${PLATFORM}/config.cmake")

	configure_file(${PROJECT_SOURCE_DIR}/arch/linker.ld.in ${PROJECT_BINARY_DIR}/linker.ld)

	# Now export our output variables
	set(LINKER_SCRIPT "${PROJECT_BINARY_DIR}/linker.ld" PARENT_SCOPE)
	set(ARCH_SRCS "${ARCH_SRCS}" PARENT_SCOPE)
	set(PLATFORM_SRCS "${PLATFORM_SRCS}" PARENT_SCOPE)

  # Platform specific custom targets/commands.
	set(ADDITINOAL_TARGETS ${ARCHPATH}/${PLATFORM}/targets.cmake PARENT_SCOPE)
ENDFUNCTION(LOAD_PROFILE)
