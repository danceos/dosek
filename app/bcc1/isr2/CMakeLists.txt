COREDOS_BINARY(
  NAME bcc1_isr2a
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  a.c
)

COREDOS_BINARY(
  NAME bcc1_isr2b
  SYSTEM_XML system.xml
  VERIFY verify_b.py
  b.c
)

COREDOS_BINARY(
  NAME bcc1_isr2c
  SYSTEM_XML system.xml
  VERIFY verify_c.py
  c.c
)

COREDOS_BINARY(
  NAME bcc1_isr2d
  SYSTEM_XML system.xml
  VERIFY verify_d.py
  d.c
)


