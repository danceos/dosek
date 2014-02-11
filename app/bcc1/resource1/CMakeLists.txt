COREDOS_BINARY(
  NAME bcc1_resource1a
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_a.py
  TEST_ISO
  a.cc
)

COREDOS_BINARY(
  NAME bcc1_resource1b
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_b.py
  TEST_ISO
  b.cc
)

COREDOS_BINARY(
  NAME bcc1_resource1c
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_a.py # Same constraints as A
  TEST_ISO
  c.cc
)

COREDOS_BINARY(
  NAME bcc1_resource1d
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_d.py
  TEST_ISO
  d.cc
)

COREDOS_BINARY(
  NAME bcc1_resource1e
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_e.py
  TEST_ISO
  e.cc
)
