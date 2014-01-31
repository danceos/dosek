COREDOS_BINARY(
  NAME bcc1_complex1a
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  a.cc
)

COREDOS_BINARY(
  NAME bcc1_complex1b
  SYSTEM_XML system.xml
  VERIFY verify_b.py
  b.cc
)

COREDOS_BINARY(
  NAME bcc1_complex1c
  SYSTEM_XML system.xml
  VERIFY verify_c.py
  c.cc
)
