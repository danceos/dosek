COREDOS_BINARY(
  NAME bcc1_isr2a
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  TEST_ISO
  a.cc ../trace.cc
)

COREDOS_BINARY(
  NAME bcc1_isr2b
  SYSTEM_XML system.xml
  VERIFY verify_b.py
  TEST_ISO
  b.cc ../trace.cc
)

COREDOS_BINARY(
  NAME bcc1_isr2c
  SYSTEM_XML system.xml
  VERIFY verify_c.py
  TEST_ISO
  c.cc ../trace.cc
)

COREDOS_BINARY(
  NAME bcc1_isr2d
  SYSTEM_XML system.xml
  VERIFY verify_d.py
  TEST_ISO
  d.cc ../trace.cc
)


