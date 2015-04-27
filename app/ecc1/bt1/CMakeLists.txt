# Test case: bt1a
# Basic Task activates Basic Task. Both terminate.
DOSEK_BINARY(
  NAME ecc1_bt1a
  SYSTEM_DESC system.oil
  LIBS libtest
  TEST_ISO
  a.cc
)

# Test case: bt1b
# Basic Task activates lower and higher Extended Task. All terminate
DOSEK_BINARY(
  NAME ecc1_bt1b
  SYSTEM_DESC system.oil
  LIBS libtest
  TEST_ISO
  b.cc
)

# Test case: bt1c
# Basic Task activates extened (higher) task which chains to (higher) basic task. Both basic tasks terminate.
DOSEK_BINARY(
  NAME ecc1_bt1c
  SYSTEM_DESC system.oil
  LIBS libtest
  TEST_ISO
  c.cc
)

# Test case: bt1d
# ET activates lower BT and higher BT. All tasks terminate.
DOSEK_BINARY(
  NAME ecc1_bt1d
  SYSTEM_DESC system.oil
  LIBS libtest
  TEST_ISO
  d.cc
)


# Test case: bt1e
# Two BTs running. BT chains to ET. ET terminates
DOSEK_BINARY(
  NAME ecc1_bt1e
  SYSTEM_DESC system.oil
  LIBS libtest
  TEST_ISO
  e.cc
)

# Test case: bt1e
# BT activates ET. ET waits. BT sets event. ET terminates. BT terminates.
DOSEK_BINARY(
  NAME ecc1_bt1f
  SYSTEM_DESC system.oil
  LIBS libtest
  TEST_ISO
  f.cc
)

# ET activates BT 3 times.
DOSEK_BINARY(
  NAME ecc1_bt1g
  SYSTEM_DESC system.oil
  LIBS libtest
  TEST_ISO
  g.cc
)



# BT actiates BT. BT chains to ET. ET terminates.
DOSEK_BINARY(
  NAME ecc1_bt1h
  SYSTEM_DESC system.oil
  LIBS libtest
  TEST_ISO
  h.cc
)
