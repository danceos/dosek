COREDOS_BINARY(
  NAME bcc1_task2a
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  LIBS libtest
  TEST_ISO
  a.cc
)

COREDOS_BINARY(
  NAME bcc1_task2b
  SYSTEM_XML system.xml
  VERIFY verify_b.py
  LIBS libtest
  TEST_ISO
  b.cc
)

COREDOS_BINARY(
  NAME bcc1_task2c
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  LIBS libtest
  TEST_ISO
  c.cc
)
