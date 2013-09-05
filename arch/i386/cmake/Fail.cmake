## FAIL: FAult Injection Leveraged for CiAO ##

if(CIAO_FAIL_BINARY)
set(FAILDIR ${PROJECT_SOURCE_DIR}/test/fail)

if("${CIAO_ARCHITECTURE}" STREQUAL "_x86")

  set(VGAIMAGE ${FAILDIR}/vgabios.bin)
  set(ROMIMAGE ${FAILDIR}/BIOS-bochs-latest)
  set(BOCHSRC ${PROJECT_BINARY_DIR}/bochsrc.txt)
  configure_file(${FAILDIR}/bochsrc.txt.in ${BOCHSRC})

  add_custom_target( fail
      COMMAND FAIL_ELF_PATH=${PROJECT_BINARY_DIR}/bin/${CIAO_APP_NAME} ${CIAO_FAIL_BINARY} -f ${BOCHSRC} -q
      DEPENDS ${PROJECT_BINARY_DIR}/${CIAO_APP_NAME}.iso
      COMMENT "Starting Fail*"
  )

else()
  message(FATAL_ERROR "Fail* not yet supported for this architecture.")
endif()
endif()
