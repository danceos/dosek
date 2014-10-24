DOSEK_BINARY(
  NAME bcc1_lukas_dispatch
  SYSTEM_XML dispatch.xml
  LIBS libtest
  TEST_ISO
  dispatch.cc
)


DOSEK_BINARY(
  NAME bcc1_lukas_alarmstress
  SYSTEM_XML alarmstress.xml
  LIBS libtest
  TEST_ISO
  alarmstress.cc
)

DOSEK_BINARY(
  NAME bcc1_lukas_isr2
  SYSTEM_XML isr2.xml
  LIBS libtest
  TEST_ISO
  isr2.cc
)

