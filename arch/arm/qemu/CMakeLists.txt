# Get QEMU binary
find_program(QEMU "qemu-system-arm")
if(NOT QEMU)
	message(WARNING "[${PROJECT_NAME} No QEMU found, not generating QEMU targets!")
	return()
endif()

# Common arguments
set(QEMU_ARGS -M xilinx-zynq-a9 -m ${RAM_SIZE} -no-reboot -nographic -serial null -serial mon:stdio)

# Create additional targets for all executables
foreach(ELF ${EXECUTABLES})
	GET_FILENAME_COMPONENT(SUFFIX ${ELF} NAME_WE)

	get_target_property(ELF_ABS ${ELF} LOCATION)

	set(STARTUP_SCRIPTS ${PROJECT_BINARY_DIR}/startup_scripts)
	file(MAKE_DIRECTORY ${STARTUP_SCRIPTS})

	# GDB init file
	set(GDBINITFILE ${STARTUP_SCRIPTS}/${SUFFIX}.qemu.gdbinit)
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/gdbinit.in" ${GDBINITFILE})


	# Start QEMU
	add_custom_target(qrun-${SUFFIX}
		DEPENDS ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ISOFILE} in qemu-system-i386"
		COMMAND ${QEMU} ${QEMU_ARGS} -kernel ${ELF_ABS}
	)

	# Start qemu for tests (only serial console)
	add_custom_target(qtest-${SUFFIX}
		DEPENDS ${ELF} 
		COMMENT "[${PROJECT_NAME}] Running ${ELF} in qemu-system-arm no-graphic mode."
		COMMAND ${QEMU} ${QEMU_ARGS} -kernel ${ELF_ABS}
	)

	# Start qemu and attach debugger
	add_custom_target(qdebug-${SUFFIX}
		DEPENDS ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ELF} in qemu-system-i386 debug mode. "
		COMMAND ${QEMU} ${QEMU_ARGS} -kernel ${ELF_ABS} -gdb tcp::${DEBUG_PORT} -S &
        COMMAND sleep 1
		COMMAND ${DEBUGGER} -n -x ${GDBINITFILE} $<TARGET_FILE:${ELF}>
	)
endforeach()
