# SSE is the symbolic system execution

DOSEK_BINARY(
  NAME bcc1_sse1a
  SYSTEM_DESC system.oil
  LIBS libtest
  VERIFY verify_a.py
  TEST_ISO
  a.cc
)

DOSEK_BINARY(
  NAME bcc1_sse1b
  SYSTEM_DESC system.oil
  LIBS libtest
  VERIFY verify_b.py
  TEST_ISO
  b.cc
)


DOSEK_BINARY(
  NAME bcc1_sse1c
  SYSTEM_DESC system.oil
  LIBS libtest
  VERIFY verify_c.py
  TEST_ISO
  c.cc
)
