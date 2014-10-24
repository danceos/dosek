DOSEK_BINARY(
  NAME bcc1_resource2a
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  LIBS libtest
  TEST_ISO
  a.cc
)

DOSEK_BINARY(
  NAME bcc1_resource2b
  SYSTEM_XML system.xml
  VERIFY verify_b.py
  LIBS libtest
  TEST_ISO
  b.cc
)
