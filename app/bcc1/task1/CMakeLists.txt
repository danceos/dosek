COREDOS_BINARY(
  NAME bcc1_task1a
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  LIBS libtest
  GENERATOR_ARGS -fgen-asserts -fsse
  TEST_ISO
  a.cc
)

COREDOS_BINARY(
  NAME bcc1_task1b
  SYSTEM_XML system.xml
  VERIFY verify_b.py
  LIBS libtest
  TEST_ISO
  b.cc
)

COREDOS_BINARY(
  NAME bcc1_task1c
  SYSTEM_XML system.xml
  VERIFY verify_c.py
  LIBS libtest
  TEST_ISO
  c.cc
)

COREDOS_BINARY(
  NAME bcc1_task1d
  SYSTEM_XML system.xml
  VERIFY verify_d.py
  LIBS libtest
  TEST_ISO
  d.cc
)

COREDOS_BINARY(
  NAME bcc1_task1e
  SYSTEM_XML system.xml
  VERIFY verify_e.py
  LIBS libtest
  TEST_ISO
  e.cc
)

COREDOS_BINARY(
  NAME bcc1_task1f
  SYSTEM_XML system.xml
  VERIFY verify_f.py
  LIBS libtest
  TEST_ISO
  f.cc
)

COREDOS_BINARY(
  NAME bcc1_task1g
  SYSTEM_XML system.xml
  VERIFY verify_g.py
  LIBS libtest
  TEST_ISO
  g.cc 
)

