# Get bochs binary

# Create additional targets for all executables
set(STARTUP_SCRIPTS ${PROJECT_BINARY_DIR}/startup_scripts)
file(MAKE_DIRECTORY ${STARTUP_SCRIPTS})

foreach(ELF ${EXECUTABLES})
  set(BOCHS_BIOS "${CMAKE_CURRENT_SOURCE_DIR}/BIOS-bochs-latest")
  set(BOCHS_GUEST_RAM ${RAM_SIZE})
  set(BOCHS_HOST_RAM ${RAM_SIZE})
  set(BOCHS_VGA_IMAGE "${CMAKE_CURRENT_SOURCE_DIR}/vgabios.bin")
  set(BOCHS_ISO_IMAGE "${PROJECT_BINARY_DIR}/${ELF}.iso")

  set(BOCHSRC "${STARTUP_SCRIPTS}/bochsrc-${ELF}")
  configure_file("${CMAKE_CURRENT_SOURCE_DIR}/bochsrc-nogui.in" "${BOCHSRC}-nogui" )
endforeach()
