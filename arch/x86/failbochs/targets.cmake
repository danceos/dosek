
#set(GRUB_MKRESCUE "grub-mkrescue")
find_program(GRUB_MKRESCUE "grub-mkrescue")
if(GRUB_MKRESCUE)
		set(ISODIR "${PROJECT_BINARY_DIR}/grub_iso")

		set(ISOFILE "${ELFFILE}.iso")

		message(STATUS "Building bootable ISO for ${ELFFILE} in ${ISODIR}")

		# Generate build directory for grub-mkrescue
		set(BOOTDIR "${ISODIR}/boot/")
		set(GRUBDIR "${BOOTDIR}/grub")

		file(MAKE_DIRECTORY ${GRUBDIR})
		# Copy and configure grub configuration file
		configure_file("arch/x86/failbochs/grub.cfg.in" "${GRUBDIR}/grub.cfg")

		add_custom_command(
			SOURCE ${ELFFILE}
			COMMAND ${CMAKE_COMMAND} -E copy ${ELFFILE} ${BOOTDIR}
			COMMAND ${GRUB_MKRESCUE}
			ARGS -o ${ISOFILE} ${ISODIR}
			OUTPUT ${ISOFILE} ${BOOTDIR}/${ELFFILE}
		)

		add_custom_target(run
				DEPENDS ${ISOFILE} ${ELFFILE}
				COMMAND echo "Running ${ISOFILE}..."
			  COMMAND qemu-system-i386 -cdrom ${ISOFILE}
		)
else()
		message(FATAL_ERROR "grub-mkrescue not found, cannot create bootable iso :(")
endif()
