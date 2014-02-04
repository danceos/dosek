COREDOS_BINARY(
  NAME bcc1_alarm1a
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  LIBS libtest
  TEST_ISO
  a.cc
)

COREDOS_BINARY(
  NAME bcc1_alarm1b
  SYSTEM_XML system.xml
  VERIFY verify_b.py
  LIBS libtest
  TEST_ISO
  b.cc
)

COREDOS_BINARY(
  NAME bcc1_alarm1c
  SYSTEM_XML system.xml
  VERIFY verify_c.py
  LIBS libtest
  TEST_ISO
  c.cc
)

COREDOS_BINARY(
  NAME bcc1_alarm1d
  SYSTEM_XML system.xml
  VERIFY verify_d.py
  LIBS libtest
  TEST_ISO
  d.cc
)

COREDOS_BINARY(
  NAME bcc1_alarm1e
  SYSTEM_XML system.xml
  VERIFY verify_e.py
  LIBS libtest
  TEST_ISO
  e.cc
)


COREDOS_BINARY(
  NAME bcc1_alarm1f
  SYSTEM_XML system.xml
  # VERIFY verify_f.py
  LIBS libtest
  TEST_ISO
  f.cc
)
