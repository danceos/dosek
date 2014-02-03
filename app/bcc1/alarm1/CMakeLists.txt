COREDOS_BINARY(
  NAME bcc1_alarm1a
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  TEST_ISO
  a.cc ../trace.cc
)

COREDOS_BINARY(
  NAME bcc1_alarm1b
  SYSTEM_XML system.xml
  VERIFY verify_b.py
  TEST_ISO
  b.cc ../trace.cc
)

COREDOS_BINARY(
  NAME bcc1_alarm1c
  SYSTEM_XML system.xml
  VERIFY verify_c.py
  TEST_ISO
  c.cc ../trace.cc
)

COREDOS_BINARY(
  NAME bcc1_alarm1d
  SYSTEM_XML system.xml
  VERIFY verify_d.py
  TEST_ISO
  d.cc ../trace.cc
)

COREDOS_BINARY(
  NAME bcc1_alarm1e
  SYSTEM_XML system.xml
  VERIFY verify_e.py
  TEST_ISO
  e.cc ../trace.cc
)


COREDOS_BINARY(
  NAME bcc1_alarm1f
  SYSTEM_XML system.xml
  # VERIFY verify_f.py
  TEST_ISO
  f.cc ../trace.cc
)
