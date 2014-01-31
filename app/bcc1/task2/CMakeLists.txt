COREDOS_BINARY(
  NAME bcc1_task2a
  SYSTEM_XML system.xml
  VERIFY verify_a.py
  a.cc
)

COREDOS_BINARY(
  NAME bcc1_task2b
  SYSTEM_XML system.xml
  VERIFY verify_b.py
  b.cc
)
