# SSE is the symbolic system execution

COREDOS_BINARY(
  NAME bcc1_sse1a
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_a.py
  TEST_ISO
  a.cc
)

COREDOS_BINARY(
  NAME bcc1_sse1b
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_b.py
  TEST_ISO
  b.cc
)


COREDOS_BINARY(
  NAME bcc1_sse1c
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_c.py
  TEST_ISO
  c.cc
)
