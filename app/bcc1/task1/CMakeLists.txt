COREDOS_BINARY(
  NAME bcc1_task1a
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  TEST_ISO
  a.cc ../trace.cc
)

COREDOS_BINARY(
  NAME bcc1_task1b
  SYSTEM_XML system.xml
  VERIFY verify_b.py
  TEST_ISO
  b.cc ../trace.cc
)

COREDOS_BINARY(
  NAME bcc1_task1c
  SYSTEM_XML system.xml
  VERIFY verify_c.py
  c.cc
)

COREDOS_BINARY(
  NAME bcc1_task1d
  SYSTEM_XML system.xml
  VERIFY verify_d.py
  d.cc
)

COREDOS_BINARY(
  NAME bcc1_task1e
  SYSTEM_XML system.xml
  VERIFY verify_e.py
  e.cc
)

COREDOS_BINARY(
  NAME bcc1_task1f
  SYSTEM_XML system.xml
  VERIFY verify_f.py
  f.cc
)

COREDOS_BINARY(
  NAME bcc1_task1g
  SYSTEM_XML system.xml
  VERIFY verify_g.py
  g.cc
)

