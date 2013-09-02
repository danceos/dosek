FUNCTION(LOAD_PROFILE ARCH PLATFORM)
	# Obtain sources
	set(ARCHPATH "${PROJECT_SOURCE_DIR}/arch/${ARCH}")
	file(GLOB ARCH_SRCS "${ARCHPATH}/*.cc" "${ARCHPATH}/*.S")
	file(GLOB PLATFORM_SRCS "${ARCHPATH}/${PLATFORM}/*.cc")

	# Load platform specific custom targets, if present

	# Load flags
	include("${ARCHPATH}/cmake/flags.cmake")

	# now export our output variables
	set(PLATFORM_LAYOUT "${ARCHPATH}/${PLATFORM}/layout.ld")


	message(STATUS "Architecture sources: ${ARCH_SRCS}, Platform specifics: ${PLATFORM_SRCS}")
	message(STATUS "Memory layout: ${PLATFORM_LAYOUT}")
	add_executable(${ELFFILE} ${PLATFORM_SRCS} ${ARCH_SRCS})
#target_link_libraries(${ELFFILE} TODO)

	set_target_properties(${ELFFILE} PROPERTIES LINK_FLAGS
			"-Wl,-T -m32 ${PLATFORM_LAYOUT} -Wl,-nostdlib -nostdlib -ffreestanding -O2" )

  # Platform specific custom targets/commands.
	include(${ARCHPATH}/${PLATFORM}/targets.cmake)
ENDFUNCTION(LOAD_PROFILE)
