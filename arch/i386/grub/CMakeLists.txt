# Create additional targets for all executables
foreach(ELF ${EXECUTABLES})
	# Do not suffix targets for main executable
	GET_FILENAME_COMPONENT(SUFFIX ${ELF} NAME_WE)
	set(DSUFFIX "-${SUFFIX}")

	get_target_property(ELF_ABS ${ELF} LOCATION)
	set(ISOFILE "${ELF_ABS}.iso")

	set(STARTUP_SCRIPTS ${PROJECT_BINARY_DIR}/grub/${SUFFIX}/startup_scripts)
	file(MAKE_DIRECTORY ${STARTUP_SCRIPTS})

	# Grub
	find_program(GRUB_MKRESCUE "grub-mkrescue")
	if(NOT GRUB_MKRESCUE)
		message(FATAL_ERROR "grub-mkrescue not found, cannot create bootable iso :(")
	endif()

	set(ISODIR "${PROJECT_BINARY_DIR}/grub/${SUFFIX}/grub_iso")

	# Generate build directory for grub-mkrescue
	set(BOOTDIR "${ISODIR}/boot/")
	set(GRUBDIR "${BOOTDIR}/grub")
	file(MAKE_DIRECTORY ${GRUBDIR})

	# Copy the grub configuration file
	file(COPY grub.cfg DESTINATION ${GRUBDIR})

	# Create bootable ISO from ELF
	add_custom_command(
		DEPENDS ${ELF}
		COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${ELF}> ${BOOTDIR}/dosek.elf
		COMMAND ${GRUB_MKRESCUE} -o ${ISOFILE} ${ISODIR}
		COMMAND ${CMAKE_COMMAND} -E remove ${BOOTDIR}/dosek.elf
		COMMENT "[${PROJECT_NAME}] Generating bootable grub iso."
		OUTPUT ${ISOFILE}
	)

	# Create bootable ISO
	add_custom_target(iso${DSUFFIX}
		DEPENDS ${ISOFILE}
	)
endforeach()
