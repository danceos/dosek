DOSEK_BINARY(
  NAME bcc1_task2a
  SYSTEM_DESC system.xml
  VERIFY verify_a.py
  LIBS libtest
  TEST_ISO
  a.cc
)

DOSEK_BINARY(
  NAME bcc1_task2b
  SYSTEM_DESC system.xml
  VERIFY verify_b.py
  LIBS libtest
  TEST_ISO
  b.cc
)

DOSEK_BINARY(
  NAME bcc1_task2c
  SYSTEM_DESC system.xml
  VERIFY verify_a.py
  LIBS libtest
  TEST_ISO
  c.cc
)
