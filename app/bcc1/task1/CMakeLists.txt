DOSEK_BINARY(
  NAME bcc1_task1a
  SYSTEM_DESC system.oil
  VERIFY verify_a.py
  LIBS libtest
  TEST_ISO
  a.cc
)

DOSEK_BINARY(
  NAME bcc1_task1a_sse
  SYSTEM_DESC system.oil
  VERIFY verify_a.py
  LIBS libtest
  GENERATOR_ARGS -fgen-asserts -fsse
  TEST_ISO
  a.cc
)

DOSEK_BINARY(
  NAME bcc1_task1b
  SYSTEM_DESC system.oil
  VERIFY verify_b.py
  LIBS libtest
  TEST_ISO
  b.cc
)

DOSEK_BINARY(
  NAME bcc1_task1c
  SYSTEM_DESC system.oil
  VERIFY verify_c.py
  LIBS libtest
  TEST_ISO
  c.cc
)

DOSEK_BINARY(
  NAME bcc1_task1d
  SYSTEM_DESC system.oil
  VERIFY verify_d.py
  LIBS libtest
  TEST_ISO
  d.cc
)

DOSEK_BINARY(
  NAME bcc1_task1e
  SYSTEM_DESC system.oil
  VERIFY verify_e.py
  LIBS libtest
  TEST_ISO
  e.cc
)

DOSEK_BINARY(
  NAME bcc1_task1f
  SYSTEM_DESC system.oil
  VERIFY verify_f.py
  LIBS libtest
  TEST_ISO
  f.cc
)

DOSEK_BINARY(
  NAME bcc1_task1g
  SYSTEM_DESC system.oil
  VERIFY verify_g.py
  LIBS libtest
  TEST_ISO
  g.cc 
)

