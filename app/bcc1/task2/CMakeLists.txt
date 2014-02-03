COREDOS_BINARY(
  NAME bcc1_task2a
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  TEST_ISO
  a.cc ../trace.cc
)

COREDOS_BINARY(
  NAME bcc1_task2b
  SYSTEM_XML system.xml
  VERIFY verify_b.py
  TEST_ISO
  b.cc ../trace.cc
)

COREDOS_BINARY(
  NAME bcc1_task2c
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  TEST_ISO
  c.cc ../trace.cc
)
