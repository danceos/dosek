macro(dosek_arm_platform_executable NAME)
  set(ELF_FILE "${PROJECT_BINARY_DIR}/${NAME}")
  set(BINARY_FILE "${PROJECT_BINARY_DIR}/${NAME}.bin")
  add_custom_command(OUTPUT ${BINARY_FILE}
    DEPENDS ${NAME}
    COMMAND ${CROSS_OBJCOPY} ${ELF_FILE} -O binary ${BINARY_FILE}
    COMMENT "[${PROJECT_NAME}/${NAME}] Generating Binary Image"
  )

  add_custom_target(${NAME}-objcopy DEPENDS "${BINARY_FILE}")
endmacro()