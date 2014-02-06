COREDOS_BINARY(
  NAME bcc1_complex1a
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  LIBS libtest
  TEST_ISO
  a.cc
)

COREDOS_BINARY(
  NAME bcc1_complex1b
  SYSTEM_XML system.xml
  VERIFY verify_b.py
  LIBS libtest
  TEST_ISO
  b.cc
 )

COREDOS_BINARY(
  NAME bcc1_complex1c
  SYSTEM_XML system.xml
  VERIFY verify_c.py
  LIBS libtest
  TEST_ISO
  c.cc
)

COREDOS_BINARY(
  NAME bcc1_complex1d
  SYSTEM_XML system.xml
  LIBS libtest
  TEST_ISO
  d.cc
)
