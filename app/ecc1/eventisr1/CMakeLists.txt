DOSEK_BINARY(
  NAME ecc1_eventisr1a
  SYSTEM_DESC system.oil
  VERIFY verify_a.py
  LIBS libtest
  TEST_ISO
  a.cc
)


DOSEK_BINARY(
  NAME ecc1_eventisr1b
  SYSTEM_DESC system.oil
  VERIFY verify_b.py
  LIBS libtest
  TEST_ISO
  b.cc
)

DOSEK_BINARY(
  NAME ecc1_eventisr1c
  SYSTEM_DESC system.oil
  VERIFY verify_c.py
  LIBS libtest
  TEST_ISO
  c.cc
)

DOSEK_BINARY(
  NAME ecc1_eventisr1d
  SYSTEM_DESC system.oil
  VERIFY verify_d.py
  LIBS libtest
  TEST_ISO
  d.cc
)

DOSEK_BINARY(
  NAME ecc1_eventisr1e
  SYSTEM_DESC system.oil
  #VERIFY verify_e.py
  LIBS libtest
  TEST_ISO
  e.cc
)

