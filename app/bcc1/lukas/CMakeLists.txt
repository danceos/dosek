DOSEK_BINARY(
  NAME bcc1_lukas_dispatch
  SYSTEM_DESC dispatch.oil
  LIBS libtest
  TEST_ISO
  dispatch.cc
)


DOSEK_BINARY(
  NAME bcc1_lukas_alarmstress
  SYSTEM_DESC alarmstress.oil
  LIBS libtest
  TEST_ISO
  alarmstress.cc
)

DOSEK_BINARY(
  NAME bcc1_lukas_isr2
  SYSTEM_DESC isr2.oil
  LIBS libtest
  TEST_ISO
  isr2.cc
)

