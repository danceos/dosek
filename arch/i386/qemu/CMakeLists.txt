# Get QEMU binary
find_program(QEMU "qemu-system-i386")
if(NOT QEMU)
	message(WARNING "[${PROJECT_NAME} No QEMU found, not generating QEMU targets!")
	return()
endif()

# Create additional targets for all executables
foreach(ELF ${EXECUTABLES})
	# Do not suffix targets for main executable
	if(${ELF} STREQUAL ${ELFFILE})
		set(SUFFIX "")
		set(DSUFFIX "")
	else()
		GET_FILENAME_COMPONENT(SUFFIX ${ELF} NAME_WE)
		set(DSUFFIX "-${SUFFIX}")
	endif()

	get_target_property(ELF_ABS ${ELF} LOCATION)
	set(ISOFILE "${ELF_ABS}.iso")

	set(STARTUP_SCRIPTS ${PROJECT_BINARY_DIR}/startup_scripts)
	file(MAKE_DIRECTORY ${STARTUP_SCRIPTS})

	# GDB init file
	set(GDBINITFILE ${STARTUP_SCRIPTS}/${SUFFIX}.qemu.gdbinit)
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/gdbinit.in" ${GDBINITFILE})

	# Common arguments
	set(QEMU_ARGS -cdrom ${ISOFILE} -no-reboot -m ${RAM_SIZE})

	# Start QEMU
	add_custom_target(qrun${DSUFFIX}
		DEPENDS iso${DSUFFIX} ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ISOFILE} in qemu-system-i386"
		COMMAND ${QEMU} ${QEMU_ARGS}
	)

	# Start qemu in terminal (for ssh)
	add_custom_target(qrunterm${DSUFFIX}
		DEPENDS iso${DSUFFIX} ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ISOFILE} in qemu-system-i386 curses mode"
		COMMAND ${QEMU} ${QEMU_ARGS} -display curses
	)

	# Start qemu for tests (only serial console)
	add_custom_target(qtest${DSUFFIX}
		DEPENDS iso${DSUFFIX} ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ISOFILE} in qemu-system-i386 no  graphic mode."
		COMMAND ${QEMU} ${QEMU_ARGS} -nographic
	)

	# Start qemu and attach debugger
	add_custom_target(qdebug${DSUFFIX}
		DEPENDS iso${DSUFFIX} ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ISOFILE} in qemu-system-i386 debug mode. "
		COMMAND ${QEMU} ${QEMU_ARGS} -gdb tcp::${DEBUG_PORT} -S &
		${DEBUGGER} -n -x ${GDBINITFILE} $<TARGET_FILE:${ELF}>
	)
endforeach()
