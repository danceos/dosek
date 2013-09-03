
set(BASEDIR "${PROJECT_SOURCE_DIR}/arch/x86/failbochs")

set(ISOFILE "${PROJECT_BINARY_DIR}/${ELFFILE}.iso")

set(BOCHS_BIOS "${BASEDIR}/BIOS-bochs-latest")
set(BOCHS_GUEST_RAM 32)
set(BOCHS_HOST_RAM 32)
set(BOCHS_VGA_IMAGE "${BASEDIR}/vgabios.bin")
set(BOCHS_ISO_IMAGE "${ISOFILE}")

configure_file("${BASEDIR}/bochsrc.in" "${PROJECT_BINARY_DIR}/bochsrc")

#set(GRUB_MKRESCUE "grub-mkrescue")
find_program(GRUB_MKRESCUE "grub-mkrescue")
if(GRUB_MKRESCUE)
		set(ISODIR "${PROJECT_BINARY_DIR}/grub_iso")

		message(STATUS "Building bootable ISO for ${ELFFILE} in ${ISODIR}")

		# Generate build directory for grub-mkrescue
		set(BOOTDIR "${ISODIR}/boot/")
		set(GRUBDIR "${BOOTDIR}/grub")

		file(MAKE_DIRECTORY ${GRUBDIR})
		# Copy and configure grub configuration file
		configure_file("${BASEDIR}/grub.cfg.in" "${GRUBDIR}/grub.cfg")

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

