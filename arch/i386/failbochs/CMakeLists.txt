# Set additional custom targets.
set(ISOFILE "${PROJECT_BINARY_DIR}/${ELFFILE}.iso")

set(BOCHS_BIOS "${CMAKE_CURRENT_SOURCE_DIR}/BIOS-bochs-latest")
set(BOCHS_GUEST_RAM 32)
set(BOCHS_HOST_RAM 32)
set(BOCHS_VGA_IMAGE "${CMAKE_CURRENT_SOURCE_DIR}/vgabios.bin")
set(BOCHS_ISO_IMAGE "${ISOFILE}")

set(BOCHSRC "${PROJECT_BINARY_DIR}/bochsrc")
configure_file("${CMAKE_CURRENT_SOURCE_DIR}/bochsrc.in" ${BOCHSRC} )

set(FAIL_BINARY "Fail binary not set yet :(" CACHE STRING "Fail binary")

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
		configure_file("${CMAKE_CURRENT_SOURCE_DIR}/grub.cfg.in" "${GRUBDIR}/grub.cfg")

		add_custom_command(
			SOURCE ${ELFFILE}
			COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:${ELFFILE}> ${BOOTDIR}
			COMMAND ${GRUB_MKRESCUE}
			ARGS -o ${ISOFILE} ${ISODIR}
			OUTPUT ${ISOFILE} ${BOOTDIR}/${ELFFILE}
		)


    add_custom_target( fail
      COMMAND FAIL_ELF_PATH=$<TARGET_FILE:${ELFFILE}> ${FAIL_BINARY} -f ${BOCHSRC} -q
      DEPENDS ${ISOFILE}
      COMMENT "Starting Fail*"
  )

		add_custom_target(run
				DEPENDS ${ISOFILE} ${ELFFILE}
				COMMAND echo "Running ${ISOFILE}..."
			  COMMAND qemu-system-i386 -cdrom ${ISOFILE}
		)

		add_custom_target(deb
				DEPENDS ${ISOFILE} ${ELFFILE}
				COMMAND echo "Running ${ISOFILE}..."
			  COMMAND qemu-system-i386 -cdrom ${ISOFILE} -s -S &
				ddd $<TARGET_FILE:${ELFFILE}>
		)


else()
		message(FATAL_ERROR "grub-mkrescue not found, cannot create bootable iso :(")
endif()

