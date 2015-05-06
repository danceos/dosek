# Get QEMU binary
find_program(QEMU "qemu-system-i386")
if(NOT QEMU)
	message(WARNING "[${PROJECT_NAME} No QEMU found, not generating QEMU targets!")
	return()
endif()

# Create additional targets for all executables
foreach(ELF ${EXECUTABLES})
	GET_FILENAME_COMPONENT(SUFFIX ${ELF} NAME_WE)
	set(DSUFFIX "-${SUFFIX}")

	get_target_property(ELF_ABS ${ELF} LOCATION)
	set(ISOFILE "${ELF_ABS}.iso")

	set(STARTUP_SCRIPTS ${PROJECT_BINARY_DIR}/startup_scripts)
	file(MAKE_DIRECTORY ${STARTUP_SCRIPTS})

    # Common arguments
	set(QEMU_ARGS -kernel ${ELF_ABS} -no-reboot  -machine pc,accel=tcg -m ${RAM_SIZE} -smp 2)

	# GDB init file
    # Fix whitespace escaping in CXX FLAGS
    string(REPLACE ";" " " QEMU_ARGS_STR "${QEMU_ARGS}")
	set(GDBINITFILE ${STARTUP_SCRIPTS}/${SUFFIX}.qemu.gdbinit)
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/gdbinit.in" ${GDBINITFILE})

	# Start QEMU
	add_custom_target(qrun${DSUFFIX}
		DEPENDS ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ELF_ABS} in qemu-system-i386"
		COMMAND ${QEMU} ${QEMU_ARGS}
	)

	# Start qemu in terminal (for ssh)
	add_custom_target(qrunterm${DSUFFIX}
		DEPENDS ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ELF_ABS} in qemu-system-i386 curses mode"
		COMMAND ${QEMU} ${QEMU_ARGS} -display curses
	)

	# Start qemu for tests (only serial console)
	add_custom_target(qtest${DSUFFIX}
		DEPENDS  ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ELF_ABS} in qemu-system-i386 no  graphic mode."
		COMMAND ${QEMU} ${QEMU_ARGS} -nographic
	)

	# Start qemu and attach debugger
	add_custom_target(qdebug${DSUFFIX}
		DEPENDS  ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ELF} in qemu-system-i386 debug mode. "
		COMMAND gdb -x "${GDBINITFILE}" ${ELF_ABS}
	)
endforeach()
