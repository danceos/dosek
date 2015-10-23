# Create additional targets for all executables
find_program(GRUB_MKRESCUE NAMES "grub-mkrescue" "grub2-mkrescue")
if(NOT GRUB_MKRESCUE)
  message(WARNING "grub-mkrescue not found, cannot create bootable iso :(")
else(NOT GRUB_MKRESCUE)
  foreach(ELF ${EXECUTABLES})
	# Grub
    SET(ISODIR "${CMAKE_CURRENT_BINARY_DIR}/${ELF}")
	# Generate build directory for grub-mkrescue
	set(BOOTDIR "${ISODIR}/boot/")
	set(GRUBDIR "${BOOTDIR}/grub")
	file(MAKE_DIRECTORY ${GRUBDIR})

	# Copy the grub configuration file
	file(COPY grub.cfg DESTINATION ${GRUBDIR})

	# Create bootable ISO from ELF
	add_custom_target(${ELF}.iso
	  DEPENDS ${ELF}
	  COMMAND ${CMAKE_COMMAND} -E copy "$<TARGET_FILE:${ELF}>" ${BOOTDIR}/dosek.elf
	  COMMAND ${GRUB_MKRESCUE} -o ${PROJECT_BINARY_DIR}/${ELF}.iso ${ISODIR}
	  COMMENT "[${PROJECT_NAME}] Generating bootable grub iso."
      )
  endforeach()
endif()
