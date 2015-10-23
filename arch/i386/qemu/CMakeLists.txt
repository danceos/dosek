# Get QEMU binary
find_program(QEMU "qemu-system-i386")
if(NOT QEMU)
	message(WARNING "[${PROJECT_NAME} No QEMU found, not generating QEMU targets!")
	return()
endif()
set(STARTUP_SCRIPTS ${CMAKE_CURRENT_BINARY_DIR}/startup_scripts)
file(MAKE_DIRECTORY ${STARTUP_SCRIPTS})

# Create additional targets for all executables
foreach(ELF ${EXECUTABLES})
	set(ISOFILE "$<TARGET_FILE:${ELF}>.iso")

    # Common arguments
	set(QEMU_ARGS -kernel ${PROJECT_BINARY_DIR}/${ELF} -no-reboot  -machine pc,accel=tcg -m ${RAM_SIZE} -smp 2)

    # Fix whitespace escaping in CXX FLAGS
    string(REPLACE ";" " " QEMU_ARGS_STR "${QEMU_ARGS}")
    set(ELF_ABS ${PROJECT_BINARY_DIR}/${ELF})
	set(GDBINITFILE ${STARTUP_SCRIPTS}/${ELF}.qemu.gdbinit)
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/gdbinit.in" ${GDBINITFILE})

	# Start QEMU
	# add_custom_target(run-${ELF}
	# 	DEPENDS ${ELF}
	# 	COMMENT "[${PROJECT_NAME}] Running $<TARGET_FILE:${ELF}> in qemu-system-i386"
	# 	COMMAND ${QEMU} ${QEMU_ARGS}
	# )
    #
	# # Start qemu in terminal (for ssh)
	# add_custom_target(runterm-${ELF}
	# 	DEPENDS ${ELF}
	# 	COMMENT "[${PROJECT_NAME}] Running $<TARGET_FILE:${ELF}> in qemu-system-i386 curses mode"
	# 	COMMAND ${QEMU} ${QEMU_ARGS} -display curses
	# )

	# Start qemu for tests (only serial console)
	add_custom_target(test-${ELF}
		DEPENDS  ${ELF}
		COMMENT "[${PROJECT_NAME}] Running $<TARGET_FILE:${ELF}> in qemu-system-i386 no  graphic mode."
		COMMAND ${QEMU} ${QEMU_ARGS} -nographic
	)

	# Start qemu and attach debugger
	add_custom_target(debug-${ELF}
		DEPENDS  ${ELF}
		COMMENT "[${PROJECT_NAME}] Running ${ELF} in qemu-system-i386 debug mode. "
		COMMAND gdb -x "${GDBINITFILE}" $<TARGET_FILE:${ELF}>
	)
endforeach()
