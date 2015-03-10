if("${GENERATOR_ARGS}" MATCHES "--system-calls fsm")
else()
DOSEK_BINARY(
  NAME bcc1_counter1a
  SYSTEM_DESC system.oil
  LIBS libtest
  TEST_ISO
  a.cc
)
endif()
