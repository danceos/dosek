DOSEK_BINARY(
  NAME bcc1_resource1a
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_a.py
  TEST_ISO
  a.cc
)

DOSEK_BINARY(
  NAME bcc1_resource1b
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_b.py
  TEST_ISO
  b.cc
)

DOSEK_BINARY(
  NAME bcc1_resource1c
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_a.py # Same constraints as A
  TEST_ISO
  c.cc
)

DOSEK_BINARY(
  NAME bcc1_resource1d
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_d.py
  TEST_ISO
  d.cc
)

DOSEK_BINARY(
  NAME bcc1_resource1e
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_e.py
  TEST_ISO
  e.cc
)

DOSEK_BINARY(
  NAME bcc1_resource1f
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_f.py
  TEST_ISO
  f.cc
)


DOSEK_BINARY(
  NAME bcc1_resource1g
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_g.py
  TEST_ISO
  g.cc
)

DOSEK_BINARY(
  NAME bcc1_resource1h
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_h.py
  TEST_ISO
  h.cc
)

DOSEK_BINARY(
  NAME bcc1_resource1j
  SYSTEM_XML system.xml
  LIBS libtest
  #VERIFY verify_j.py
  TEST_ISO
  j.cc
)

DOSEK_BINARY(
  NAME bcc1_resource1k
  SYSTEM_XML system.xml
  LIBS libtest
  VERIFY verify_k.py
  TEST_ISO
  k.cc
)