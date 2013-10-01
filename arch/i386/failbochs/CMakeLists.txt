# Create additional targets for all executables
foreach(ELF ${EXECUTABLES})
	set(FAIL_BINARY "Fail binary not set yet :(" CACHE STRING "Fail binary")

	# Do not suffix targets for main executable
	if(${ELF} STREQUAL ${ELFFILE})
		set(SUFFIX "")
		set(DSUFFIX "")
	else()
		GET_FILENAME_COMPONENT(SUFFIX ${ELF} NAME_WE)
		set(DSUFFIX "-${SUFFIX}")
	endif()

	set(ISOFILE "${PROJECT_BINARY_DIR}/${ELF}.iso")

	# Bochs
	set(BOCHS_BIOS "${CMAKE_CURRENT_SOURCE_DIR}/BIOS-bochs-latest")
	set(BOCHS_GUEST_RAM 32)
	set(BOCHS_HOST_RAM 32)
	set(BOCHS_VGA_IMAGE "${CMAKE_CURRENT_SOURCE_DIR}/vgabios.bin")
	set(BOCHS_ISO_IMAGE "${ISOFILE}")

	set(BOCHSRC "${PROJECT_BINARY_DIR}/bochsrc${DSUFFIX}")
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/bochsrc.in" ${BOCHSRC} )
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/bochsrc-gdb.in" "${BOCHSRC}-gdb" )
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/bochsrc-term.in" "${BOCHSRC}-term" )
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/gdbinit.in" "${PROJECT_BINARY_DIR}/${SUFFIX}.gdbinit" )

	# Grub
	find_program(GRUB_MKRESCUE "grub-mkrescue")
	if(NOT GRUB_MKRESCUE)
			message(FATAL_ERROR "grub-mkrescue not found, cannot create bootable iso :(")
	endif()

	set(ISODIR "${PROJECT_BINARY_DIR}/grub_iso")

	message(STATUS "Building bootable ISO for ${ELF}")

	# Generate build directory for grub-mkrescue
	set(BOOTDIR "${ISODIR}/boot/")
	set(GRUBDIR "${BOOTDIR}/grub")
	file(MAKE_DIRECTORY ${GRUBDIR})

	# Copy and configure grub configuration file
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/grub.cfg.in" "${GRUBDIR}/grub.cfg")

	# Create bootable ISO from ELF
	add_custom_command(
			DEPENDS ${ELF}
			COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${ELF}> ${BOOTDIR}/${ELFFILE}
			COMMAND ${GRUB_MKRESCUE}
			ARGS -o ${ISOFILE} ${ISODIR}
			OUTPUT ${ISOFILE} ${BOOTDIR}/${ELF}
			)

	# Create bootable ISO
	add_custom_target( grubiso${DSUFFIX}
			DEPENDS ${ISOFILE}
			COMMENT "Generating bootable grub iso."
			)

	# Start FAIL
	add_custom_target( fail${DSUFFIX}
			COMMAND FAIL_ELF_PATH=$<TARGET_FILE:${ELF}> ${FAIL_BINARY} -f ${BOCHSRC}${DSUFFIX} -q
			DEPENDS ${ISOFILE}
			COMMENT "Starting Fail*"
			)

	# Start qemu 
	add_custom_target(qrun${DSUFFIX}
			DEPENDS ${ISOFILE} ${ELF}
			COMMAND echo "Running ${ISOFILE}..."
			COMMAND qemu-system-i386 -cdrom ${ISOFILE} -no-reboot
			)

	# Start qemu in terminal (for ssh) 
	add_custom_target(qrunterm${DSUFFIX}
			DEPENDS ${ISOFILE} ${ELF}
			COMMAND echo "Running ${ISOFILE}..."
			COMMAND qemu-system-i386 -cdrom ${ISOFILE} -display curses -no-reboot
			)

	# Start qemu for tests (only serial console)
	add_custom_target(qtest${DSUFFIX}
			DEPENDS ${ISOFILE} ${ELF}
			COMMAND echo "Running ${ISOFILE}..."
			COMMAND qemu-system-i386 -cdrom ${ISOFILE} -nographic -no-reboot
			)

	# Start qemu and attach debugger
	add_custom_target(qdebug${DSUFFIX}
			DEPENDS ${ISOFILE} ${ELF}
			COMMAND echo "Running ${ISOFILE}..."
			COMMAND qemu-system-i386 -cdrom ${ISOFILE} -s -S -no-reboot &
			ddd $<TARGET_FILE:${ELF}>
			)

	# Start bochs
	add_custom_target(run${DSUFFIX}
			DEPENDS ${ISOFILE} ${ELF}
			COMMAND echo "Running ${ISOFILE}..."
			COMMAND bochs -f ${BOCHSRC}
			)

	# Start bochs in terminal (for ssh)
	add_custom_target(runterm${DSUFFIX}
			DEPENDS ${ISOFILE} ${ELF}
			COMMAND echo "Running ${ISOFILE}..."
			COMMAND bochs -f ${BOCHSRC}-term 
			)

	# Start bochs with GDB stub for debugging
	add_custom_target(debug${DSUFFIX}
			DEPENDS ${ISOFILE} ${ELF}
			COMMAND echo "Running ${ISOFILE}..."
			COMMAND bochs -f ${BOCHSRC}-gdb 
			)

	# Start GDB and attach to bochs
	add_custom_target(gdb${DSUFFIX}
			DEPENDS ${ISOFILE} ${ELF}
			COMMAND echo "Starting gdb for ${ISOFILE}..."
			WORKING_DIRECTORY ${PROJECT_BINARY_DIR}
			COMMAND gdb -n -x ${SUFFIX}.gdbinit 
			)
endforeach()
